"""
Retrains the tabular autoencoder against the v2 (relabeled) dataset and
preprocessor, so it stays consistent with FraudPredictor's fitted
preprocessor after ml/predictor.py was pointed at preprocessor_v2.pkl.

The autoencoder only ever trains on genuine rows, so the fraud relabeling
itself doesn't change what it learns -- this rerun exists purely to refit it
against preprocessor_v2.pkl's (very slightly different, due to an 80% vs
100% subsample) StandardScaler statistics, avoiding a train/serve mismatch.

Identical methodology to train_autoencoder.py; see that file for rationale.
"""

import joblib
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from ml.autoencoder_model import TabularAutoencoder

DATASET_PATH = "loan_applications_v2.csv"
PREPROCESSOR_PATH = "preprocessor_v2.pkl"
MODEL_OUT = "autoencoder_v2.pt"
META_OUT = "autoencoder_meta_v2.pkl"

EPOCHS = 30
BATCH_SIZE = 256
LEARNING_RATE = 1e-3
VAL_SPLIT = 0.1
THRESHOLD_PERCENTILE = 97.5

print("Loading dataset and preprocessor...")
df = pd.read_csv(DATASET_PATH)
df = df.dropna(subset=["fraud_flag"])
preprocessor = joblib.load(PREPROCESSOR_PATH)

genuine = df[df["fraud_flag"] == 0]
X = genuine.drop(
    [
        "fraud_flag",
        "loan_status",
        "fraud_type",
        "application_id",
        "customer_id",
        "application_date",
        "residential_address",
    ],
    axis=1,
    errors="ignore",
)
X_transformed = preprocessor.transform(X).astype("float32")

rng = np.random.default_rng(42)
indices = rng.permutation(len(X_transformed))
val_size = int(len(indices) * VAL_SPLIT)
val_idx, train_idx = indices[:val_size], indices[val_size:]

train_tensor = torch.from_numpy(X_transformed[train_idx])
val_tensor = torch.from_numpy(X_transformed[val_idx])
train_loader = DataLoader(TensorDataset(train_tensor), batch_size=BATCH_SIZE, shuffle=True)

input_dim = X_transformed.shape[1]
model = TabularAutoencoder(input_dim)
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
loss_fn = nn.MSELoss()

print(f"Training autoencoder on {len(train_tensor)} genuine records ({input_dim} features)...")
for epoch in range(1, EPOCHS + 1):
    model.train()
    running_loss = 0.0
    for (batch,) in train_loader:
        optimizer.zero_grad()
        reconstruction = model(batch)
        loss = loss_fn(reconstruction, batch)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * len(batch)
    train_loss = running_loss / len(train_tensor)

    model.eval()
    with torch.no_grad():
        val_loss = loss_fn(model(val_tensor), val_tensor).item()

    if epoch == 1 or epoch % 5 == 0 or epoch == EPOCHS:
        print(f"Epoch {epoch:>3}/{EPOCHS} — train MSE: {train_loss:.5f}  val MSE: {val_loss:.5f}")

print("Computing anomaly threshold from validation reconstruction errors...")
with torch.no_grad():
    per_sample_error = ((model(val_tensor) - val_tensor) ** 2).mean(dim=1).numpy()
threshold = float(np.percentile(per_sample_error, THRESHOLD_PERCENTILE))
print(f"Anomaly threshold ({THRESHOLD_PERCENTILE}th percentile of genuine val errors): {threshold:.5f}")

torch.save(model.state_dict(), MODEL_OUT)
joblib.dump({"input_dim": input_dim, "threshold": threshold}, META_OUT)
print(f"Saved {MODEL_OUT} and {META_OUT}.")
