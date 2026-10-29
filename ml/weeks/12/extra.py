"""Fit a small PyTorch network: python -m pip install torch; python extra.py."""

import torch
from torch import nn

from lab import data


def main():
    torch.manual_seed(3305)
    torch.set_num_threads(1)
    train_x, validation_x, train_y, validation_y = data()
    features = torch.tensor(train_x, dtype=torch.float32)
    targets = torch.tensor(train_y, dtype=torch.float32)
    validation = torch.tensor(validation_x, dtype=torch.float32)
    labels = torch.tensor(validation_y)
    model = nn.Sequential(nn.Linear(2, 8), nn.Tanh(), nn.Linear(8, 1))
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.02)
    for epoch in range(1, 181):
        model.train()
        optimizer.zero_grad()
        logits = model(features).squeeze(1)
        loss = criterion(logits, targets)
        loss.backward()
        optimizer.step()
        if epoch % 30 == 0:
            model.eval()
            with torch.no_grad():
                validation_logits = model(validation).squeeze(1)
                validation_loss = criterion(validation_logits, labels.float()).item()
                accuracy = ((validation_logits >= 0) == labels.bool()).float().mean().item()
            print(f"epoch={epoch:3} train_loss={loss.item():.3f} "
                  f"validation_loss={validation_loss:.3f} accuracy={accuracy:.3f}")


if __name__ == "__main__":
    main()
