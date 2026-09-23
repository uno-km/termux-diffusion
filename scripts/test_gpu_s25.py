import time
import sys
import termux_diffusion as td

print("[TEST] Initializing engine with device='gpu'...")
t0 = time.time()
engine = td.load(model="sdxs", device="gpu")
print(f"[TEST] Engine loaded in {time.time() - t0:.2f}s")
print(f"[TEST] Binary path: {engine.get_binary_path()}")

print("[TEST] Starting generation (1 step, 256x256)...")
t1 = time.time()
res = engine.generate(
    prompt="a cute red cat, high quality",
    steps=1,
    width=256,
    height=256,
    output="s25_adreno830_gpu.png"
)
elapsed = time.time() - t1
print(f"[TEST] Generation finished in {elapsed:.2f}s!")
print(f"[TEST] Result: {res}")
