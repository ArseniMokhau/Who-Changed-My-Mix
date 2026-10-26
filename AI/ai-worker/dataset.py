import random
from pathlib import Path

import librosa
import numpy as np
import torch
from torch.utils.data import Dataset

from model import SR, SEGMENT_LEN, SEGMENT_SEC, waveform_to_features

EXTS = {".wav", ".mp3", ".flac", ".ogg"}
MAX_RATE = 1.3
LOAD_SEC = SEGMENT_SEC * MAX_RATE + 0.5  # enough audio even after speed-up


def list_audio(root: str):
    return sorted(str(p) for p in Path(root).rglob("*") if p.suffix.lower() in EXTS)


def split_files(files, val_frac=0.15, seed=42):
    """Split BY SONG so the model can't memorise songs it is validated on."""
    files = files[:]
    random.Random(seed).shuffle(files)
    n_val = max(1, int(len(files) * val_frac))
    return files[n_val:], files[:n_val]


class ManipulationDataset(Dataset):
    """label 0 = original, 1 = time_stretch, 2 = pitch_shift.
    Every class goes through the SAME load -> process -> crop path, so the model
    can't cheat on file format or length."""

    def __init__(self, files, samples_per_file=20, train=True):
        self.items = []
        for f in files:
            try:
                dur = librosa.get_duration(path=f)
            except Exception:
                continue
            if dur > LOAD_SEC:
                self.items.append((f, dur))
        self.n = samples_per_file
        self.train = train

    def __len__(self):
        return len(self.items) * self.n

    def __getitem__(self, idx):
        path, dur = self.items[idx // self.n]
        rng = random.Random(None if self.train else idx)  # fixed val set
        label = rng.randrange(3)
        offset = rng.uniform(0, dur - LOAD_SEC)
        y, _ = librosa.load(path, sr=SR, mono=True, offset=offset, duration=LOAD_SEC)

        if label == 1:
            rate = rng.choice([rng.uniform(0.75, 0.95), rng.uniform(1.05, MAX_RATE)])
            y = librosa.effects.time_stretch(y, rate=rate)
        elif label == 2:
            steps = rng.choice([-1, 1]) * rng.uniform(0.5, 4.0)
            y = librosa.effects.pitch_shift(y, sr=SR, n_steps=steps)

        start = (len(y) - SEGMENT_LEN) // 2 if not self.train else rng.randint(0, len(y) - SEGMENT_LEN)
        y = y[start:start + SEGMENT_LEN]
        if self.train:
            y = y * rng.uniform(0.6, 1.0)
            y = y + np.random.randn(len(y)) * rng.uniform(0, 0.003)
        y = torch.from_numpy(y.astype(np.float32))
        return waveform_to_features(y).squeeze(0), label
