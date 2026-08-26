cmake_minimum_required(VERSION 3.10)
project(track_b_v10_matmul C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SD_CPP_DIR "C:/Users/ATSAdmin/Documents/UNO/small_prj/termux-diffusion/thirdparty/stable-diffusion.cpp")

add_definitions(
    -DGGML_USE_VULKAN
    -DVULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1
    -DGGML_VERSION="1.0.0"
    -DGGML_COMMIT="97d2990"
)

include_directories(
    ${SD_CPP_DIR}/ggml/include
    ${SD_CPP_DIR}/ggml/src
    ${SD_CPP_DIR}/ggml/src/ggml-vulkan
    "C:/Users/ATSAdmin/Documents/UNO/small_prj/termux-diffusion/gpu-probe-suite/v10-cmake"
)

file(GLOB SHADER_SRCS "shaders_cpp/*.cpp")

add_executable(track_b_v10_matmul
    "${SD_CPP_DIR}/ggml/src/ggml.c"
    "${SD_CPP_DIR}/ggml/src/ggml-alloc.c"
    "${SD_CPP_DIR}/ggml/src/ggml-quants.c"
    "${SD_CPP_DIR}/ggml/src/ggml-threading.cpp"
    "${SD_CPP_DIR}/ggml/src/ggml-backend.cpp"
    "${SD_CPP_DIR}/ggml/src/ggml-backend-meta.cpp"
    ggml-vulkan.cpp
    track_b_v10_matmul.cpp
    ${SHADER_SRCS}
)

target_link_libraries(track_b_v10_matmul dl)
