from torch_geometric.nn import ResGatedGraphConv, Linear, HeteroConv, HeteroLinear, LayerNorm
import torch.nn
from torch import sigmoid
# Script based on https://github.com/pyg-team/pytorch_geometric/blob/master/examples/link_pred.py by Fey, M. and Niketan, N. (2023) and
# lfangyu09, and Fey, M. Edge classification with gcn or gat in https://github.com/pyg-team/pytorch_geometric/discussions/8862, 2024. Retrieved on February 23, 2026
# and Graphia by Bhuiyan, M. H. M. (2025). Call Me Maybe: Enhancing JavaScript Call Graph Construction using Graph Neural Network
# https://arxiv.org/abs/2506.18191
device = torch.get_default_device()
class GNN(torch.nn.Module):
    def __init__(self, hidden_channels, num_layers):
        super().__init__()
        self.node_encoder = Linear(in_channels = -1, out_channels = hidden_channels)
        self.final_linear = Linear(in_channels = -1, out_channels = 1)
        self.layers = torch.nn.ModuleList()
        self.conv1 = ResGatedGraphConv(-1, hidden_channels)
        self.conv2 = ResGatedGraphConv(hidden_channels, hidden_channels)
        self.norm = LayerNorm(hidden_channels, affine = True)
        self.act = torch.nn.ReLU()
            

    def forward(self, x, edge_index):
        # Get node embeddings
        x = self.node_encoder(x)
        # Apply ResGatedGraphConv
        x = self.conv1(x, edge_index)
        # Apply it again
        x = self.conv2(x, edge_index)
        x = self.norm(x)
        x = self.act(x)
        x_src, x_dst = x[edge_index[0]], x[edge_index[1]]
        edge_feat = torch.cat([x_src, x_dst], dim = -1)
        edge_feat = self.final_linear(edge_feat)
        edge_feat = sigmoid(edge_feat)
        return edge_feat
