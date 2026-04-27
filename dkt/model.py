import torch
import torch.nn as nn

class DKT(nn.Module):
    def __init__(self, num_skills, hidden_size=64):
        super().__init__()
        self.embedding = nn.Embedding(num_skills * 2, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_skills)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.embedding(x)
        out, _ = self.lstm(x)
        out = self.fc(out)
        return self.sigmoid(out)