# Track B Stage V10 Vulkan Loader Alignment & Handover Document

**Branch**: `feature/gpu`  
**Start Commit**: `34ae184661f0c0d597135278844d376b9afe915a`  
**Target Hardware**: Samsung Galaxy S21 (Exynos 2100, Mali-G78 MP14 GPU, Android 15)  
**Isolated Execution Directory**: `$HOME/tmp/track-b-v10-loader-alignment`

---

## 1. Executive Summary & Accomplished Milestones

The Loader/ICD path mismatch in `ggml-vulkan` has been **completely resolved and verified**.

### Verified Milestones
- **GGML Vulkan Loader Alignment**: **`VERIFIED`** (Aligned to Android System Loader `/system/lib64/libvulkan.so`).
- **GGML Mali-G78 Device Discovery**: **`VERIFIED`** (`MALI_G78_PRESENT_AFTER=TRUE`).
- **GGML Device Acceptance & Selection**: **`VERIFIED`** (`BACKEND_SELECTED=Vulkan`, `DEVICE_NAME=Mali-G78`, `CPU_FALLBACK=FALSE`).

```text
V10_LOADER_ALIGNMENT=PASS
V10_MALI_DEVICE_SELECTION=PASS
V10_GGML_GRAPH_DISPATCH=BLOCKED (Current Blocker)
V10_MATMUL_CORRECTNESS=NOT_EVALUATED
```

---

## 2. Milestone Progression & Ground Truth Matrix

| Pipeline Layer | Direct Probe (V0-V9) | Original GGML (V10) | Aligned GGML (Current V10) |
| :--- | :--- | :--- | :--- |
| **Vulkan Loader** | `/system/lib64/libvulkan.so` | `/data/data/com.termux/files/usr/lib/libvulkan.so.1.4.354` | `/system/lib64/libvulkan.so` (**`VERIFIED`**) |
| **Raw Device** | `Mali-G78` | `llvmpipe (CPU Renderer)` | `Mali-G78` (**`VERIFIED`**) |
| **Device Acceptance** | `PASS` | `REJECTED (No devices found)` | `PASS` (**`VERIFIED`**) |
| **Backend Selected** | `Direct Vulkan` | `NONE` | `Vulkan` (**`VERIFIED`**) |
| **CPU Fallback** | `DISABLED` | `N/A` | `DISABLED` (**`VERIFIED`**) |
| **Dispatch / Binding** | `PASS` | `NOT REACHED` | `BLOCKED (RC=134 SIGABRT)` |
| **MatMul Numerical Check**| `0 Mismatches` | `NOT REACHED` | `NOT EVALUATED` |

---

## 3. Current Blocker Analysis (`GRAPH_COMPUTE_RESULT=FAIL_DISPATCH_BINDING`, `RC=134`)

- **Execution Return Code**: `EXECUTION_RC=134` (Signal 6 `SIGABRT` / `abort()`).
- **Interpretation**: The process encountered a fatal assertion or dynamic dispatcher handle binding mismatch during descriptor set / pipeline dispatch setup.
- **Important Note**: `MISMATCH_COUNT=1024` reflects an uncomputed $32 \times 32$ tensor graph, **NOT** numerical computation error on Mali-G78.

---

## 4. Next Session Execution & Diagnostic Protocol

> **STRICT DIRECTIVE FOR NEXT AGENT**:
> - **DO NOT** modify Vulkan loader paths, API versions, device filters, or Mali capability conditions.
> - **DO NOT** revert to manual `.cpp` or `.o` file linkage.
> - **DO NOT** launch Stage V11 until Stage V10 FP32 MatMul completes with 0 mismatches.

### Single Diagnostic Task for Next Agent
Run GDB or capture backtrace on S21 under `$HOME/tmp/track-b-v10-loader-alignment/` to isolate the exact source file and line number of `EXECUTION_RC=134`:

```bash
cd $HOME/tmp/track-b-v10-loader-alignment/build_ggml
export LD_LIBRARY_PATH=$HOME/tmp/track-b-v10-loader-alignment/build_ggml/src:$HOME/tmp/track-b-v10-loader-alignment/build_ggml/src/ggml-vulkan:$HOME/tmp/track-b-v10-loader-alignment/build_ggml/src/ggml-cpu:$LD_LIBRARY_PATH
gdb --args ./bin/track_b_v10_matmul
# Inside GDB:
# (gdb) run
# (gdb) bt
# (gdb) thread apply all bt
```

Once the backtrace isolates the specific descriptor set or dynamic dispatcher function pointer binding mismatch, apply a single-point fix to the dispatch binding layer and verify FP32 MatMul accuracy ($Max/Mean\ Error < 10^{-4}$).
