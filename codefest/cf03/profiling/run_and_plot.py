"""
Run both GEMM kernels via NVRTC, measure GFLOP/s, and generate the roofline plot.
Saves: gemm_roofline.png in this directory.
"""

import numpy as np
import ctypes
import os
import sys
import time

# ── NVRTC compile helper ────────────────────────────────────────────────────
from cuda.bindings import nvrtc, driver

def _check(err):
    if isinstance(err, nvrtc.nvrtcResult):
        if err != nvrtc.nvrtcResult.NVRTC_SUCCESS:
            raise RuntimeError(f"NVRTC error: {nvrtc.nvrtcGetErrorString(err)[1].decode()}")
    elif isinstance(err, driver.CUresult):
        if err != driver.CUresult.CUDA_SUCCESS:
            raise RuntimeError(f"CUDA driver error: {err}")
    return err

def compile_kernel(src: str, name: str) -> bytes:
    err, prog = nvrtc.nvrtcCreateProgram(src.encode(), name.encode(), 0, [], [])
    _check(err)
    opts = [b"--gpu-architecture=compute_86",  # RTX 3050 Ti = Ampere sm_86
            b"-default-device"]
    compile_err = nvrtc.nvrtcCompileProgram(prog, len(opts), opts)[0]
    if compile_err != nvrtc.nvrtcResult.NVRTC_SUCCESS:
        _, log_size = nvrtc.nvrtcGetProgramLogSize(prog)
        log = b" " * log_size
        nvrtc.nvrtcGetProgramLog(prog, log)
        raise RuntimeError(f"Compile failed:\n{log.decode()}")
    _, ptx_size = nvrtc.nvrtcGetPTXSize(prog)
    ptx = b" " * ptx_size
    nvrtc.nvrtcGetPTX(prog, ptx)
    nvrtc.nvrtcDestroyProgram(prog)
    return ptx

# ── CUDA driver setup ───────────────────────────────────────────────────────
_check(driver.cuInit(0))
err, dev = driver.cuDeviceGet(0)
_check(err)
err, ctx = driver.cuCtxCreate(None, 0, dev)
_check(err)

def get_device_name():
    err, name = driver.cuDeviceGetName(256, dev)
    return name.decode().strip().rstrip("\x00")

gpu_name = get_device_name()
print(f"GPU: {gpu_name}")

# ── Kernel source (header-only, no main) ────────────────────────────────────
NAIVE_SRC = r"""
extern "C" __global__ void gemm_naive(const float* A, const float* B, float* C, int n) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row < n && col < n) {
        float sum = 0.0f;
        for (int k = 0; k < n; ++k)
            sum += A[row * n + k] * B[k * n + col];
        C[row * n + col] = sum;
    }
}
"""

TILED_SRC = r"""
#define T 8
extern "C" __global__ void gemm_tiled(const float* A, const float* B, float* C, int n) {
    __shared__ float As[T][T];
    __shared__ float Bs[T][T];
    int row = blockIdx.y * T + threadIdx.y;
    int col = blockIdx.x * T + threadIdx.x;
    float sum = 0.0f;
    int num_tiles = (n + T - 1) / T;
    for (int t = 0; t < num_tiles; ++t) {
        int a_col = t * T + threadIdx.x;
        As[threadIdx.y][threadIdx.x] = (row < n && a_col < n) ? A[row * n + a_col] : 0.0f;
        int b_row = t * T + threadIdx.y;
        Bs[threadIdx.y][threadIdx.x] = (b_row < n && col < n) ? B[b_row * n + col] : 0.0f;
        __syncthreads();
        for (int k = 0; k < T; ++k)
            sum += As[threadIdx.y][k] * Bs[k][threadIdx.x];
        __syncthreads();
    }
    if (row < n && col < n)
        C[row * n + col] = sum;
}
"""

# ── Compile ─────────────────────────────────────────────────────────────────
print("Compiling kernels via NVRTC...")
naive_ptx = compile_kernel(NAIVE_SRC, "gemm_naive.cu")
tiled_ptx = compile_kernel(TILED_SRC, "gemm_tiled.cu")
print("Compiled OK")

def load_function(ptx: bytes, fn_name: str):
    err, module = driver.cuModuleLoadData(ptx)
    _check(err)
    err, func = driver.cuModuleGetFunction(module, fn_name.encode())
    _check(err)
    return func

naive_fn = load_function(naive_ptx, "gemm_naive")
tiled_fn = load_function(tiled_ptx, "gemm_tiled")

# ── Allocate device memory ───────────────────────────────────────────────────
N = 1024
size = N * N * 4  # float32

h_A = np.random.rand(N, N).astype(np.float32)
h_B = np.random.rand(N, N).astype(np.float32)

err, d_A = driver.cuMemAlloc(size); _check(err)
err, d_B = driver.cuMemAlloc(size); _check(err)
err, d_C = driver.cuMemAlloc(size); _check(err)

_check(driver.cuMemcpyHtoD(d_A, h_A.ctypes.data_as(ctypes.c_void_p), size))
_check(driver.cuMemcpyHtoD(d_B, h_B.ctypes.data_as(ctypes.c_void_p), size))

# ── CUDA event timing helper ─────────────────────────────────────────────────
def time_kernel_ms(func, grid, block, args, n_runs=3):
    from cuda.bindings import driver as drv
    # warmup
    _check(drv.cuLaunchKernel(func, *grid, *block, 0, 0, args, 0))
    _check(drv.cuCtxSynchronize())

    err, start = drv.cuEventCreate(0); _check(err)
    err, stop  = drv.cuEventCreate(0); _check(err)

    _check(drv.cuEventRecord(start, 0))
    for _ in range(n_runs):
        _check(drv.cuLaunchKernel(func, *grid, *block, 0, 0, args, 0))
    _check(drv.cuEventRecord(stop, 0))
    _check(drv.cuEventSynchronize(stop))

    err, ms = drv.cuEventElapsedTime(start, stop); _check(err)
    drv.cuEventDestroy(start)
    drv.cuEventDestroy(stop)
    return ms / n_runs

# ── Benchmark naive ──────────────────────────────────────────────────────────
n_val = ctypes.c_int(N)
args_naive = [
    ctypes.c_void_p(int(d_A)),
    ctypes.c_void_p(int(d_B)),
    ctypes.c_void_p(int(d_C)),
    n_val,
]
args_naive_ptrs = (ctypes.c_void_p * len(args_naive))(
    *[ctypes.addressof(a) for a in args_naive]
)

BLK = 16
grid_naive  = (N // BLK, N // BLK, 1)
block_naive = (BLK, BLK, 1)

ms_naive = time_kernel_ms(naive_fn, grid_naive, block_naive, args_naive_ptrs)
flops = 2.0 * N**3
gflops_naive = flops / (ms_naive * 1e-3) / 1e9
print(f"gemm_naive:  {ms_naive:.3f} ms  →  {gflops_naive:.1f} GFLOP/s")

# ── Benchmark tiled ──────────────────────────────────────────────────────────
T_val = 8
grid_tiled  = (N // T_val, N // T_val, 1)
block_tiled = (T_val, T_val, 1)

ms_tiled = time_kernel_ms(tiled_fn, grid_tiled, block_tiled, args_naive_ptrs)  # same args
gflops_tiled = flops / (ms_tiled * 1e-3) / 1e9
print(f"gemm_tiled:  {ms_tiled:.3f} ms  →  {gflops_tiled:.1f} GFLOP/s")

# ── Arithmetic intensity ─────────────────────────────────────────────────────
# Naive: reads N^2*(N+N)*4 bytes (no reuse), writes N^2*4 bytes
bytes_naive = 2 * N**3 * 4 + N**2 * 4   # reads A+B per output, plus writes C
ai_naive    = flops / bytes_naive

# Tiled T=8: DRAM traffic reduced by N/T = 128 vs naive read traffic
bytes_tiled = (2 * N**3 * 4 / (N / T_val)) + N**2 * 4
ai_tiled    = flops / bytes_tiled

print(f"\nArithmetic intensity: naive={ai_naive:.3f} FLOP/byte, tiled={ai_tiled:.3f} FLOP/byte")

# ── GPU hardware ceilings (RTX 3050 Ti Laptop) ──────────────────────────────
peak_bw_GBs   = 192.0   # GB/s  (GDDR6 128-bit @ 12 Gbps)
peak_fp32_GFLOPS = 8680.0  # GFLOP/s

# ── Roofline plot ─────────────────────────────────────────────────────────────
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ai_range = np.logspace(-2, 3, 500)
roofline  = np.minimum(ai_range * peak_bw_GBs, peak_fp32_GFLOPS)
ridge_pt  = peak_fp32_GFLOPS / peak_bw_GBs

fig, ax = plt.subplots(figsize=(8, 5))
ax.loglog(ai_range, roofline, "k-", linewidth=2, label=f"Roofline ({gpu_name})")
ax.axvline(ridge_pt, color="gray", linestyle="--", linewidth=1, label=f"Ridge point ({ridge_pt:.1f} FLOP/B)")

# Kernel points
ax.scatter([ai_naive], [gflops_naive], color="red",  s=120, zorder=5,
           label=f"Naive: {gflops_naive:.0f} GFLOP/s  (AI={ai_naive:.3f})")
ax.scatter([ai_tiled], [gflops_tiled], color="blue", s=120, zorder=5,
           label=f"Tiled T=8: {gflops_tiled:.0f} GFLOP/s  (AI={ai_tiled:.2f})")

# Annotate
ax.annotate(f"  naive\n  {gflops_naive:.0f} GFLOP/s",
            xy=(ai_naive, gflops_naive), fontsize=9, color="red")
ax.annotate(f"  tiled\n  {gflops_tiled:.0f} GFLOP/s",
            xy=(ai_tiled, gflops_tiled), fontsize=9, color="blue")

# Ceilings
ax.axhline(peak_fp32_GFLOPS, color="green", linestyle=":", linewidth=1.2,
           label=f"Peak compute: {peak_fp32_GFLOPS:.0f} GFLOP/s")
ax.axhline(peak_bw_GBs, color="orange", linestyle=":", linewidth=1.2,
           label=f"Peak BW ceiling at AI=1: {peak_bw_GBs:.0f} GB/s")

ax.set_xlabel("Arithmetic Intensity (FLOP/byte)", fontsize=12)
ax.set_ylabel("Performance (GFLOP/s)", fontsize=12)
ax.set_title("Roofline Model — 1024×1024 FP32 GEMM\nNVIDIA RTX 3050 Ti Laptop GPU", fontsize=12)
ax.legend(fontsize=8, loc="upper left")
ax.grid(True, which="both", linestyle="--", alpha=0.4)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemm_roofline.png")
plt.tight_layout()
plt.savefig(out_path, dpi=150)
print(f"\nRoofline plot saved to: {out_path}")

# ── Nsight-style summary ──────────────────────────────────────────────────────
print("\n=== Nsight Compute Summary (NVRTC measured) ===")
print(f"{'Kernel':<20} {'Time(ms)':>10} {'GFLOP/s':>10} {'AI':>8} {'Bound'}")
print("-" * 60)
for name, ms, gf, ai in [
    ("gemm_naive",    ms_naive, gflops_naive, ai_naive),
    ("gemm_tiled_T8", ms_tiled, gflops_tiled, ai_tiled),
]:
    bound = "memory" if ai < ridge_pt else "compute"
    bw_achieved = (bytes_naive if "naive" in name else bytes_tiled) / (ms * 1e-3) / 1e9
    print(f"{name:<20} {ms:>10.3f} {gf:>10.1f} {ai:>8.3f}  {bound}")

# ── Free ─────────────────────────────────────────────────────────────────────
driver.cuMemFree(d_A); driver.cuMemFree(d_B); driver.cuMemFree(d_C)
driver.cuCtxDestroy(ctx)
