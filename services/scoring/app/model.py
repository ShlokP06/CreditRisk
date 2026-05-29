import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from .schemas import SubgraphPayload, ScoreResponse, FeatureContributor, NODE_FEATUR_NAMES, get_risk_band
from .config import settings

class FraudGNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = SAGEConv(4, 64)
        self.conv2 = SAGEConv(64, 64)
        self.edge_mlp = nn.Sequential(
            nn.Linear(131, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x, edge_index, edge_attr):
        x = F.relu(self.conv1(x, edge_index))
        x = F.relu(self.conv2(x, edge_index))
        src, dst = edge_index
        combined = torch.cat([x[src], x[dst], edge_attr], dim=-1)
        return self.edge_mlp(combined)
    
class DummyModel:
    version = 'dummy-v0'
    def predict(self, payload):
        return ScoreResponse(
            transaction_id = payload.transaction_id,
            risk_score = 0.5,
            risk_band = "medium",
            model_version = self.version,
            top_contributors = []
        )
    
class FraudModel:
    def __init__(self):
        self.gnn = None
        self.version = "unknown"
        self.norm_params = {}

    @classmethod
    def load(cls, path):
        if settings.model_fallback:
            return DummyModel()
        checkpoint = torch.load(path, map_location='cpu')
        gnn = FraudGNN()
        gnn.load_state_dict(checkpoint['model_state'])
        gnn.eval()
        instance = cls()
        instance.gnn = gnn
        instance.version = checkpoint["version"]
        instance.norm_params = checkpoint.get('norm_params', {})
        return instance
    
    def predict(self, payload):
        x = torch.tensor([payload.user_features, payload.merchant_features],
                         dtype = torch.float32)
        edge_index = torch.tensor([[0],[1]], dtype = torch.long)
        edge_attr = torch.tensor([payload.edge_features], dtype = torch.float32)
        x.requires_grad_(True)
        if self.gnn:
            out = self.gnn(x, edge_index, edge_attr).squeeze()
            out.backward()
            score = out.item()