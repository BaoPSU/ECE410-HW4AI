// gemm_tiled.cu — tiled CUDA GEMM using shared memory, tile size T=8
// Compile: nvcc -O2 -o gemm_tiled gemm_tiled.cu
// Usage:   ./gemm_tiled

#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

#define N 1024
#define T 8

__global__ void gemm_tiled_kernel(const float *A, const float *B, float *C, int n) {
    __shared__ float As[T][T];
    __shared__ float Bs[T][T];

    int row = blockIdx.y * T + threadIdx.y;
    int col = blockIdx.x * T + threadIdx.x;
    float sum = 0.0f;

    int num_tiles = (n + T - 1) / T;
    for (int t = 0; t < num_tiles; ++t) {
        // Load tile from A
        int a_col = t * T + threadIdx.x;
        As[threadIdx.y][threadIdx.x] = (row < n && a_col < n) ? A[row * n + a_col] : 0.0f;
        // Load tile from B
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

int main(void) {
    size_t bytes = (size_t)N * N * sizeof(float);

    float *h_A = (float *)malloc(bytes);
    float *h_B = (float *)malloc(bytes);
    float *h_C = (float *)malloc(bytes);

    for (int i = 0; i < N * N; ++i) {
        h_A[i] = (float)(rand() % 100) / 100.0f;
        h_B[i] = (float)(rand() % 100) / 100.0f;
    }

    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, bytes);
    cudaMalloc(&d_B, bytes);
    cudaMalloc(&d_C, bytes);

    cudaMemcpy(d_A, h_A, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, bytes, cudaMemcpyHostToDevice);

    dim3 block(T, T);
    dim3 grid((N + T - 1) / T, (N + T - 1) / T);

    // Warmup
    gemm_tiled_kernel<<<grid, block>>>(d_A, d_B, d_C, N);
    cudaDeviceSynchronize();

    // Timed run
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);
    gemm_tiled_kernel<<<grid, block>>>(d_A, d_B, d_C, N);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float ms = 0.0f;
    cudaEventElapsedTime(&ms, start, stop);

    double flops = 2.0 * (double)N * (double)N * (double)N;
    double gflops = flops / (ms * 1e-3) / 1e9;

    printf("gemm_tiled (T=%d): N=%d, time=%.3f ms, %.2f GFLOP/s\n", T, N, ms, gflops);

    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    cudaMemcpy(h_C, d_C, bytes, cudaMemcpyDeviceToHost);
    cudaFree(d_A); cudaFree(d_B); cudaFree(d_C);
    free(h_A); free(h_B); free(h_C);
    return 0;
}
