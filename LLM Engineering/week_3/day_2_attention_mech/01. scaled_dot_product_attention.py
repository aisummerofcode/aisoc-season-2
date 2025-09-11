import torch 
import torch.nn as nn 


class SelfAttention_v1(nn.Module):
    def __init__(self, d_in: int, d_out: int) -> None:
        super().__init__()
        self.W_query = nn.Parameter(torch.rand(d_in, d_out))
        self.W_key = nn.Parameter(torch.rand(d_in, d_out))
        self.W_value = nn.Parameter(torch.rand(d_in, d_out)) 

    def forward(self, x: torch.Tensor)-> torch.Tensor:
        """
        Compute the self-attention output for the input sequence.

        Args:
            x (torch.Tensor): Input tensor of shape (seq_len, d_in), 
                where seq_len is the sequence length.

        Returns:
            torch.Tensor: Context vector of shape (seq_len, d_out) 
            after applying scaled dot-product attention.
        """
        
        keys = x @ self.W_key
        queries = x @ self.W_query
        values = x @ self.W_value 
        attention_scores = queries @ keys.T 
        attention_weights = torch.softmax(attention_scores / (keys.shape[-1] ** 0.5), dim=-1)
        context_vector = attention_weights @ values
        return context_vector
    
    
class SelfAttention_v2(nn.Module):
    def __init__(self, d_in, d_out, qkv_bias=False): 
        super().__init__()
        self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_key = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)

    def forward(self, x): 
        keys = self.W_key(x)
        queries = self.W_query(x)
        values = self.W_value(x)
        attention_scores = queries @ keys.T 
        attention_weights = torch.softmax(attention_scores / (keys.shape[-1] ** 0.5), dim=-1)
        context_vector = attention_weights @ values
        return context_vector