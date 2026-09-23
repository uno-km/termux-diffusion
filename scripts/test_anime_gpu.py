import time
import termux_diffusion as td

print("[TEST] Loading anime model with GPU...")
engine = td.load(model="anime", device="gpu")
print("[TEST] Running generation (4-step, 256x256)...")
res = engine.generate(
    prompt="1girl, cute anime cat ears, masterpiece",
    steps=4,
    width=256,
    height=256,
    output="s25_anime_gpu.png"
)
print(f"[TEST] Result: {res}")
