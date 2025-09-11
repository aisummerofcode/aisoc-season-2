import torch 
import torch.nn as nn


class CausalAttention(nn.Module): 
    def __init__(self, d_in, d_out, context_length, dropout, qkv_bias=False):
        super().__init__() 
        self.d_out = d_out  
        self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_key   = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer('mask', torch.triu(torch.ones(context_length, context_length), diagonal=1))

    def forward(self, x): 
        b, num_tokens, d_in = x.shape #<--- 2 x 6 x 3 (batch size, number of tokens in input sequence, input embedding size)
        keys = self.W_key(x)
        queries = self.W_query(x)
        values = self.W_value(x)
        
        attention_scores = queries @ keys.transpose(1, 2) #<--- We transpose dimensions 1 and 2, keeping the batch dimension at the first position (0)
        attention_scores.masked_fill_(self.mask.bool()[:num_tokens, :num_tokens], -torch.inf)
        attention_weights = torch.softmax(attention_scores / keys.shape[-1] ** 0.5, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        context_vector = attention_weights @ values
        return context_vector
    
    
class MultiHeadAttentionWrapper(nn.Module): 
    def __init__(self, d_in, d_out, context_length, dropout, num_heads, qkv_bias = False): 
        super().__init__()
        self.heads = nn.ModuleList(
            [
                CausalAttention(d_in, d_out, context_length, dropout, qkv_bias) for _ in range(num_heads)
                ]
            )

    def forward(self, x): 
        return torch.cat([head(x) for head in self.heads], dim=-1) 


class MultiHeadAttention(nn.Module):
    def __init__(self, d_in, d_out, context_length, dropout, num_heads, qkv_bias=False): 
        super().__init__()
        assert d_out % num_heads == 0, "d_out must be divisible by num_heads" 
        
        self.d_out = d_out 
        self.num_heads = num_heads 
        self.head_dim = d_out // num_heads     #<--- Reduces the projection dim to match the desired output dim
        self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_key = nn.Linear(d_in, d_out, bias=qkv_bias) 
        self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias) 
        self.out_proj = nn.Linear(d_out, d_out) #<--- Uses a Linear layer to combine head outputs
        self.dropout = nn.Dropout(dropout)
        self.register_buffer("mask", torch.triu(torch.ones(context_length, context_length), diagonal=1)) 

    def forward(self, x):
        b, num_tokens, d_in = x.shape
        keys = self.W_key(x)        #<--- tensor shape: (b, num_tokens, d_out)
        queries = self.W_query(x)   #<--- tensor shape: (b, num_tokens, d_out)
        values = self.W_value(x)    #<--- tensor shape: (b, num_tokens, d_out)
        
        # Next, we implicitly split the matrix by adding a num_heads dimension. 
        # Then we unroll the last dim: (b, num_tokens, d_out) -> (b, num_tokens, num_heads, head_dim).
        
        keys = keys.view(b, num_tokens, self.num_heads, self.head_dim)
        values = values.view(b, num_tokens, self.num_heads, self.head_dim)
        queries = queries.view(b, num_tokens, self.num_heads, self.head_dim) 

        # Transposes from shape: (b, num_tokens, num_heads, head_dim) to (b, num_heads,num_tokens, head_dim)
        keys = keys.transpose(1, 2)         
        queries = queries.transpose(1, 2)   
        values = values.transpose(1, 2)

        attn_scores = queries @ keys.transpose(2, 3)             #<--- Computes  dot product for each head
        mask_bool = self.mask.bool()[:num_tokens, :num_tokens]   #<--- Masks truncated to the number of tokens
        
        attn_scores.masked_fill_(mask_bool, -torch.inf)          #<--- Uses the mask to fill attention scores
        
        attn_weights = torch.softmax(attn_scores / keys.shape[-1]**0.5, dim=-1)
        attn_weights = self.dropout(attn_weights) 

        context_vec = (attn_weights @ values).transpose(1, 2) #<--- Tensor shape: (b, num_tokens, n_heads, head_dim)
        
        context_vec = context_vec.contiguous().view(b, num_tokens, self.d_out) #<--- Combines heads, where self.d_out = self.num_heads * self.head_dim
        context_vec = self.out_proj(context_vec) #<--- Adds an optional linear projection
        
        return context_vec