"""Pretrain a tiny PyTorch CNN and transfer it to noisier line images."""

from copy import deepcopy

import torch
from torch import nn

from lab import transfer_data


def tensors(samples):
    pixels, labels = samples
    return torch.tensor(pixels[:, None], dtype=torch.float32), torch.tensor(labels)


def cnn(classes, backbone=None):
    features = backbone if backbone is not None else nn.Sequential(
        nn.Conv2d(1, 8, kernel_size=3), nn.ReLU(),
        nn.AdaptiveAvgPool2d(1), nn.Flatten(),
    )
    return nn.Sequential(features, nn.Linear(8, classes))


def fit(model, examples, epochs):
    pixels, labels = examples
    model.train()
    optimizer = torch.optim.Adam((p for p in model.parameters() if p.requires_grad), lr=0.025)
    criterion = nn.CrossEntropyLoss()
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = criterion(model(pixels), labels)
        loss.backward()
        optimizer.step()


def accuracy(model, examples):
    pixels, labels = examples
    model.eval()
    with torch.inference_mode():
        return (model(pixels).argmax(1) == labels).float().mean().item()


def main():
    torch.manual_seed(3305)
    torch.set_num_threads(1)
    source, training, validation = map(tensors, transfer_data())
    pretrained = cnn(3)
    fit(pretrained, source, epochs=170)
    for mode in ("scratch", "frozen", "fine-tuned"):
        torch.manual_seed(42)
        features = None if mode == "scratch" else deepcopy(pretrained[0])
        model = cnn(2, features)
        if mode == "frozen":
            for weight in model[0].parameters():
                weight.requires_grad_(False)
        fit(model, training, epochs=90)
        print(f"{mode:10} validation_accuracy={accuracy(model, validation):.3f}")


if __name__ == "__main__":
    main()
