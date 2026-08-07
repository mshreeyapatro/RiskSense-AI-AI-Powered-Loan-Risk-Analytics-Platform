"""
Tabular autoencoder for unsupervised anomaly detection.
Learns to reconstruct genuine-application feature vectors; applications that
reconstruct poorly (high error) diverge from the normal-profile manifold,
surfacing patterns the supervised classifier wasn't trained to recognize.
"""

from __future__ import annotations

from torch import nn


class TabularAutoencoder(nn.Module):
    def __init__(self, input_dim: int, bottleneck_dim: int = 8):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, bottleneck_dim),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck_dim, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim),
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))
