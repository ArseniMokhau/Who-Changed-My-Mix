"""Usage:  python train.py --data path/to/music_folder --epochs 15"""
import argparse
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from dataset import ManipulationDataset, list_audio, split_files
from model import CLASSES, MixAuditorModel


def run_epoch(model, loader, device, opt=None):
    train = opt is not None
    model.train(train)
    loss_fn = nn.CrossEntropyLoss()
    total, correct, loss_sum = 0, 0, 0.0
    with torch.set_grad_enabled(train):
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = loss_fn(logits, y)
            if train:
                opt.zero_grad()
                loss.backward()
                opt.step()
            total += len(y)
            correct += (logits.argmax(1) == y).sum().item()
            loss_sum += loss.item() * len(y)
    return loss_sum / total, correct / total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--samples-per-file", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="weights/mixauditor.pt")
    a = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    files = list_audio(a.data)
    print(f"{len(files)} audio files found, device={device}")
    train_f, val_f = split_files(files)

    train_dl = DataLoader(ManipulationDataset(train_f, a.samples_per_file, True),
                          batch_size=a.batch, shuffle=True, num_workers=a.workers, drop_last=True)
    val_dl = DataLoader(ManipulationDataset(val_f, 10, False),
                        batch_size=a.batch, num_workers=a.workers)

    model = MixAuditorModel().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.epochs)

    best = 0.0
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    for ep in range(1, a.epochs + 1):
        tl, ta = run_epoch(model, train_dl, device, opt)
        vl, va = run_epoch(model, val_dl, device)
        sched.step()
        print(f"epoch {ep:02d} | train loss {tl:.3f} acc {ta:.3f} | val loss {vl:.3f} acc {va:.3f}")
        if va > best:
            best = va
            torch.save({"state_dict": model.state_dict(), "classes": CLASSES}, a.out)
            print(f"  saved best model (val acc {va:.3f})")


if __name__ == "__main__":
    main()
