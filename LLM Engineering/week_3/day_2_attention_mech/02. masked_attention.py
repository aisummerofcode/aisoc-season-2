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