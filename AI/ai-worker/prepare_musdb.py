import subprocess, sys, shutil
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)

# MUSDB18 (.stem.mp4): stream 0 is the mixture
for f in sorted(src.rglob("*.stem.mp4")):
    out = dst / (f.name.replace(".stem.mp4", "") + ".wav")
    if out.exists():
        continue
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f),
                    "-map", "0:a:0", "-ac", "1", "-ar", "22050", str(out)], check=True)
    print("converted", out.name)

# MUSDB18-HQ (folders): copy only mixture.wav
for f in sorted(src.rglob("mixture.wav")):
    out = dst / (f.parent.name + ".wav")
    if not out.exists():
        shutil.copy(f, out)
        print("copied", out.name)