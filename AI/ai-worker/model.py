import torch
import torch.nn as nn
import torchaudio

SR = 22050
SEGMENT_SEC = 3.0
SEGMENT_LEN = int(SR * SEGMENT_SEC)
CLASSES = ["original", "time_stretch", "pitch_shift"]

_mel = torchaudio.transforms.MelSpectrogram(
    sample_rate=SR, n_fft=1024, hop_length=512, n_mels=128
)
_db = torchaudio.transforms.AmplitudeToDB(top_db=80)


def waveform_to_features(wave: torch.Tensor) -> torch.Tensor:
    """wave: (T,) or (B, T) mono float -> (B, 1, 128, frames), normalised per sample."""
    if wave.dim() == 1:
        wave = wave.unsqueeze(0)
    x = _db(_mel(wave)).unsqueeze(1)
    mean = x.mean(dim=(1, 2, 3), keepdim=True)
    std = x.std(dim=(1, 2, 3), keepdim=True) + 1e-6
    return (x - mean) / std


def _block(cin, cout):
    return nn.Sequential(
        nn.Conv2d(cin, cout, 3, padding=1),
        nn.BatchNorm2d(cout),
        nn.ReLU(inplace=True),
        nn.Conv2d(cout, cout, 3, padding=1),
        nn.BatchNorm2d(cout),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(2),
    )


class MixAuditorModel(nn.Module):
    def __init__(self, n_classes: int = len(CLASSES)):
        super().__init__()
        self.features = nn.Sequential(_block(1, 16), _block(16, 32), _block(32, 64), _block(64, 128))
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.head = nn.Sequential(nn.Dropout(0.3), nn.Linear(128, n_classes))

    def forward(self, x):  # x: (B, 1, 128, frames) -> logits
        return self.head(self.pool(self.features(x)).flatten(1))
