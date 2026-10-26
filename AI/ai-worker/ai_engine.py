from pathlib import Path
 
import librosa
import numpy as np
import torch
 
from model import CLASSES, SEGMENT_LEN, SR, MixAuditorModel, waveform_to_features
 
WEIGHTS = Path(__file__).parent / "weights" / "mixauditor.pt"
MAX_SEGMENTS = 20
THRESHOLD = 0.5
 
_model = None
 
 
def _load_model():
    global _model
    if _model is None:
        if not WEIGHTS.exists():
            raise FileNotFoundError(f"No trained weights at {WEIGHTS}. Run train.py first.")
        ckpt = torch.load(WEIGHTS, map_location="cpu")
        _model = MixAuditorModel()
        _model.load_state_dict(ckpt["state_dict"])
        _model.eval()
    return _model
 
 
def analyze_audio(file_path: str) -> dict:
    try:
        model = _load_model()
        y, _ = librosa.load(file_path, sr=SR, mono=True)
        if len(y) < SEGMENT_LEN:
            y = np.pad(y, (0, SEGMENT_LEN - len(y)))
 
        # evenly spaced 3 s windows across the whole track
        n = min(MAX_SEGMENTS, max(1, len(y) // SEGMENT_LEN))
        starts = np.linspace(0, len(y) - SEGMENT_LEN, n).astype(int)
        batch = torch.from_numpy(np.stack([y[s:s + SEGMENT_LEN] for s in starts]).astype(np.float32))
 
        with torch.no_grad():
            probs = torch.softmax(model(waveform_to_features(batch)), dim=1).mean(0)
 
        score = float(1.0 - probs[0])
        kind = CLASSES[int(probs.argmax())]
        return {
            "status": "success",
            "manipulation_score": round(score, 4),
            "is_manipulated": score > THRESHOLD,
            "predicted_type": kind,
            "class_probabilities": {c: round(float(p), 4) for c, p in zip(CLASSES, probs)},
            "message": "Analysis complete.",
        }
    except Exception as ex:
        return {"status": "error", "message": str(ex)}
    