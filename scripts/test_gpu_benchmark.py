import time
import termux_diffusion as td

engine = td.load(model="sdxs", device="gpu")

print("=== [TEST 1] 4-Step 256x256 Benchmark ===")
t0 = time.time()
res_4step = engine.generate(
    prompt="a cute red cat, high quality, photorealistic",
    steps=4,
    width=256,
    height=256,
    output="s25_adreno830_4step_256.png"
)
t_4step = time.time() - t0
print(f"[RESULT 1] 4-Step 256x256: {t_4step:.2f}s | Result: {res_4step}")

print("\n=== [TEST 2] 4-Step 512x512 Benchmark ===")
t1 = time.time()
res_512 = engine.generate(
    prompt="a cute red cat, high quality, photorealistic",
    steps=4,
    width=512,
    height=512,
    output="s25_adreno830_4step_512.png"
)
t_512 = time.time() - t1
print(f"[RESULT 2] 4-Step 512x512: {t_512:.2f}s | Result: {res_512}")
