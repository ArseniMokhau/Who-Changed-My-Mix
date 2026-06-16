import torch
import torchaudio
import torch.nn as nn


class MixAuditorModel(nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fc = nn.Linear(128,1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        condenced = torch.mean(x)
        return self.sigmoid(condenced)
    
model = MixAuditorModel()
model.eval()

def analyze_audio(file_path: str) -> dict:
    try:
        waveform, sample_rate = torchaudio.load(file_path)

        transform = torchaudio.transforms.MelSpectrogram(sample_rate=sample_rate, n_fft=1024, hop_length=512, n_mels=128)
        mel_spectrogram = transform(waveform)

        with torch.no_grad():
            confidence_tensor = model(mel_spectrogram)
            confidence_score = confidence_tensor.item()
        
        is_manipulated = confidence_score > 0.5

        return{
            "status": "success",
            "manipulation_score": round(confidence_score, 4),
            "is_manipulated": is_manipulated,
            "message": "Analysis complete."
        }
    
    except Exception as ex:
        return{
            "status": "error",
            "message": str(ex)
        }
