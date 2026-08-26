#include <iostream>
#include <vector>
#include <cmath>
#include <cstring>
#include <iomanip>

#include "ggml.h"
#include "ggml-alloc.h"
#include "ggml-backend.h"
#include "ggml-vulkan.h"

int main() {
    std::cout << "=== TRACK B V10 GGML-VULKAN TENSOR OPERATION PROBE (MATMUL 32x32 FP32) ===" << std::endl;

    const int M = 32;
    const int K = 32;
    const int N = 32;
    const int elem_count = M * N;

    // 1. Prepare Host Input Data
    std::vector<float> h_A(M * K);
    std::vector<float> h_B(K * N);
    std::vector<float> h_C_cpu(M * N, 0.0f);
    std::vector<float> h_C_gpu(M * N, 0.0f);

    for (int i = 0; i < M * K; ++i) {
        h_A[i] = static_cast<float>((i % 7) + 1) * 0.1f;
    }
    for (int i = 0; i < K * N; ++i) {
        h_B[i] = static_cast<float>((i % 5) + 1) * 0.2f;
    }

    // 2. CPU Reference GGML MulMat: C[i0, i1] = sum_k(A[i0, k] * B[i1, k])
    for (int i1 = 0; i1 < N; ++i1) {
        for (int i0 = 0; i0 < M; ++i0) {
            float sum = 0.0f;
            for (int k = 0; k < K; ++k) {
                sum += h_A[i0 * K + k] * h_B[i1 * K + k];
            }
            h_C_cpu[i1 * M + i0] = sum;
        }
    }

    // 3. Initialize Vulkan Backend
    ggml_backend_t backend = nullptr;
    std::string device_name = "UNKNOWN";

    size_t dev_count = ggml_backend_vk_get_device_count();
    std::cout << "V10_AVAILABLE_VK_DEVICES=" << dev_count << std::endl;

    for (size_t i = 0; i < dev_count; ++i) {
        char name[128] = {0};
        ggml_backend_vk_get_device_description(i, name, sizeof(name));
        std::cout << "[V10] VK Device #" << i << ": " << name << std::endl;
        if (!backend) {
            backend = ggml_backend_vk_init(i);
            if (backend) {
                device_name = name;
            }
        }
    }

    if (!backend) {
        std::cout << "V10_BACKEND_SELECTED=NONE" << std::endl;
        std::cout << "V10_GRAPH_COMPUTE_RESULT=FAIL_VK_INIT" << std::endl;
        std::cout << "RESULT=FAIL_GGML_VULKAN_INIT" << std::endl;
        return 1;
    }

    std::cout << "V10_BACKEND_REQUESTED=vulkan" << std::endl;
    std::cout << "V10_BACKEND_SELECTED=vulkan" << std::endl;
    std::cout << "V10_DEVICE_NAME=" << device_name << std::endl;
    std::cout << "V10_CPU_FALLBACK=FALSE" << std::endl;
    std::cout << "V10_OPERATION=mul_mat" << std::endl;
    std::cout << "V10_MATRIX_SHAPE=32x32" << std::endl;
    std::cout << "V10_DATA_TYPE=FP32" << std::endl;

    // 4. Build GGML Tensor Graph
    size_t ctx_size = ggml_tensor_overhead() * 16 + ggml_graph_overhead();
    struct ggml_init_params params = {
        /* .mem_size   = */ ctx_size,
        /* .mem_buffer = */ NULL,
        /* .no_alloc   = */ true,
    };

    struct ggml_context * ctx = ggml_init(params);

    // ggml_mul_mat(ctx, a, b) computes A^T * B or A * B depending on memory layout
    // In ggml: tensor a is transposed in layout (K, M), tensor b is (K, N) -> result is (N, M)
    struct ggml_tensor * tensor_A = ggml_new_tensor_2d(ctx, GGML_TYPE_F32, K, M);
    struct ggml_tensor * tensor_B = ggml_new_tensor_2d(ctx, GGML_TYPE_F32, K, N);
    struct ggml_tensor * tensor_C = ggml_mul_mat(ctx, tensor_A, tensor_B);

    struct ggml_cgraph * gf = ggml_new_graph(ctx);
    ggml_build_forward_expand(gf, tensor_C);

    // Allocate backend buffer
    ggml_gallocr_t galloc = ggml_gallocr_new(ggml_backend_get_default_buffer_type(backend));
    if (!ggml_gallocr_alloc_graph(galloc, gf)) {
        std::cout << "V10_GRAPH_COMPUTE_RESULT=FAIL_GRAPH_ALLOC" << std::endl;
        ggml_backend_free(backend);
        return 2;
    }

    // Set Tensor Data (Note: A is stored in row-major layout matching ggml tensor_A dimensions)
    ggml_backend_tensor_set(tensor_A, h_A.data(), 0, ggml_nbytes(tensor_A));
    ggml_backend_tensor_set(tensor_B, h_B.data(), 0, ggml_nbytes(tensor_B));

    // Compute Graph strictly on Vulkan GPU
    enum ggml_status status = ggml_backend_graph_compute(backend, gf);
    if (status != GGML_STATUS_SUCCESS) {
        std::cout << "V10_GRAPH_COMPUTE_RESULT=FAIL_GRAPH_COMPUTE" << std::endl;
        ggml_gallocr_free(galloc);
        ggml_backend_free(backend);
        return 3;
    }

    std::cout << "V10_GRAPH_COMPUTE_RESULT=PASS" << std::endl;

    // Readback GPU results
    ggml_backend_tensor_get(tensor_C, h_C_gpu.data(), 0, ggml_nbytes(tensor_C));

    // 5. Compare CPU vs GPU Results
    uint32_t mismatch_count = 0;
    uint32_t nan_count = 0;
    uint32_t inf_count = 0;
    double max_abs_err = 0.0;
    double sum_abs_err = 0.0;
    double tolerance = 1e-3;

    for (int i = 0; i < elem_count; ++i) {
        float val_gpu = h_C_gpu[i];
        float val_cpu = h_C_cpu[i];

        if (std::isnan(val_gpu)) nan_count++;
        if (std::isinf(val_gpu)) inf_count++;

        double err = std::abs(static_cast<double>(val_gpu) - static_cast<double>(val_cpu));
        if (err > max_abs_err) max_abs_err = err;
        sum_abs_err += err;

        if (err > tolerance || std::isnan(val_gpu) || std::isinf(val_gpu)) {
            mismatch_count++;
        }

        if (i < 8) {
            std::cout << "[V10] Sample [" << i << "] CPU=" << val_cpu << " GPU=" << val_gpu << " delta=" << err << std::endl;
        }
    }

    double mean_abs_err = sum_abs_err / elem_count;

    std::cout << "V10_ELEMENT_COUNT=" << elem_count << std::endl;
    std::cout << "V10_MISMATCH_COUNT=" << mismatch_count << std::endl;
    std::cout << "V10_MAX_ABS_ERROR=" << std::scientific << std::setprecision(6) << max_abs_err << std::endl;
    std::cout << "V10_MEAN_ABS_ERROR=" << std::scientific << std::setprecision(6) << mean_abs_err << std::endl;
    std::cout << "V10_NAN_COUNT=" << nan_count << std::endl;
    std::cout << "V10_INF_COUNT=" << inf_count << std::endl;
    std::cout << "V10_TOLERANCE=1.000000e-03" << std::endl;

    // Clean up
    ggml_gallocr_free(galloc);
    ggml_free(ctx);
    ggml_backend_free(backend);

    std::cout << "V10_CLEANUP_RESULT=PASS" << std::endl;
    std::cout << "PROCESS_RC=0" << std::endl;

    bool v10_pass = (mismatch_count == 0 && nan_count == 0 && inf_count == 0);
    std::cout << "RESULT=" << (v10_pass ? "PASS_V10_ADRENO_GGML_MATMUL_SUCCESSFUL" : "FAIL_V10_TENSOR_MISMATCH") << std::endl;

    return v10_pass ? 0 : 4;
}
