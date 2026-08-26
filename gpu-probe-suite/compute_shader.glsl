#version 450

layout(local_size_x = 64) in;

layout(set = 0, binding = 0) readonly buffer InputBuffer {
    uint values[];
} input_buffer;

layout(set = 0, binding = 1) writeonly buffer OutputBuffer {
    uint values[];
} output_buffer;

void main() {
    uint index = gl_GlobalInvocationID.x;
    output_buffer.values[index] = input_buffer.values[index] * 2u + 1u;
}
