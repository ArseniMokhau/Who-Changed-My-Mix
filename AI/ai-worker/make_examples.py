import random
import sys
from pathlib import Path
 
import librosa
import soundfile as sf
 
from dataset import list_audio
 
SR = 22050
CLIP_SEC = 20
RATES = [1.15, 0.85, 1.25]        # >1 faster, <1 slower
STEPS = [3, -3, 2]                # semitones
 
src, dst = sys.argv[1], Path(sys.argv[2] if len(sys.argv) > 2 else "examples")
dst.mkdir(parents=True, exist_ok=True)
 
files = list_audio(src)
random.seed(7)
for i, path in enumerate(random.sample(files, 3), start=1):
    dur = librosa.get_duration(path=path)
    offset = max(0, dur / 2 - CLIP_SEC / 2)   # clip from the middle of the song
    y, _ = librosa.load(path, sr=SR, mono=True, offset=offset, duration=CLIP_SEC)
 
    stretched = librosa.effects.time_stretch(y, rate=RATES[i - 1])
    shifted = librosa.effects.pitch_shift(y, sr=SR, n_steps=STEPS[i - 1])
 
    sf.write(dst / f"song{i}_original.wav", y, SR)
    sf.write(dst / f"song{i}_stretch_x{RATES[i-1]}.wav", stretched, SR)
    sf.write(dst / f"song{i}_pitch_{STEPS[i-1]:+d}st.wav", shifted, SR)
    print(f"song{i}: {Path(path).name}")
