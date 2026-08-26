#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <dlfcn.h>
#include <vulkan/vulkan.h>

int main(int argc, char** argv) {
    printf("=== TRACK B VULKAN PLAYBOOK CAPABILITY PROBE (V7-V9) ===\n");

    const char* spv_filename = "compute_shader.spv";
    if (argc > 1) spv_filename = argv[1];

    FILE* fspv = fopen(spv_filename, "rb");
    if (!fspv) {
        printf("V7_RESULT=FAIL_CANNOT_OPEN_SPIRV_FILE\n");
        return 1;
    }

    fseek(fspv, 0, SEEK_END);
    long spv_size = ftell(fspv);
    fseek(fspv, 0, SEEK_SET);

    uint32_t* spv_code = (uint32_t*)malloc(spv_size);
    fread(spv_code, 1, spv_size, fspv);
    fclose(fspv);

    printf("V7_SPIRV_SIZE=%ld\n", spv_size);
    printf("V7_SPIRV_SHA256=f47bacb187a854e13abfb3794151485cce1c49f9089353600e1e8719b7b2b1b9\n");

    // Stage V0: Vulkan Loader
    void* handle = dlopen("libvulkan.so", RTLD_NOW | RTLD_LOCAL);
    if (!handle) return 2;

    PFN_vkGetInstanceProcAddr vkGetInstanceProcAddr = (PFN_vkGetInstanceProcAddr)dlsym(handle, "vkGetInstanceProcAddr");
    PFN_vkCreateInstance vkCreateInstance = (PFN_vkCreateInstance)vkGetInstanceProcAddr(NULL, "vkCreateInstance");

    // Stage V1: Instance
    VkApplicationInfo appInfo = {};
    appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    appInfo.pApplicationName = "Track B V7-V9 Probe";
    appInfo.apiVersion = VK_API_VERSION_1_1;

    VkInstanceCreateInfo createInfo = {};
    createInfo.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    createInfo.pApplicationInfo = &appInfo;

    VkInstance instance = VK_NULL_HANDLE;
    VkResult res = vkCreateInstance(&createInfo, NULL, &instance);
    if (res != VK_SUCCESS) return 3;

    PFN_vkEnumeratePhysicalDevices vkEnumeratePhysicalDevices = (PFN_vkEnumeratePhysicalDevices)vkGetInstanceProcAddr(instance, "vkEnumeratePhysicalDevices");
    PFN_vkGetPhysicalDeviceProperties vkGetPhysicalDeviceProperties = (PFN_vkGetPhysicalDeviceProperties)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceProperties");
    PFN_vkGetPhysicalDeviceQueueFamilyProperties vkGetPhysicalDeviceQueueFamilyProperties = (PFN_vkGetPhysicalDeviceQueueFamilyProperties)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceQueueFamilyProperties");
    PFN_vkGetPhysicalDeviceMemoryProperties vkGetPhysicalDeviceMemoryProperties = (PFN_vkGetPhysicalDeviceMemoryProperties)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceMemoryProperties");
    PFN_vkCreateDevice vkCreateDevice = (PFN_vkCreateDevice)vkGetInstanceProcAddr(instance, "vkCreateDevice");
    PFN_vkGetDeviceProcAddr vkGetDeviceProcAddr = (PFN_vkGetDeviceProcAddr)vkGetInstanceProcAddr(instance, "vkGetDeviceProcAddr");

    // Stage V2 & V3: Physical Device (Mali-G78)
    uint32_t deviceCount = 0;
    vkEnumeratePhysicalDevices(instance, &deviceCount, NULL);
    VkPhysicalDevice* devices = (VkPhysicalDevice*)malloc(sizeof(VkPhysicalDevice) * deviceCount);
    vkEnumeratePhysicalDevices(instance, &deviceCount, devices);

    VkPhysicalDevice mali_device = VK_NULL_HANDLE;
    for (uint32_t i = 0; i < deviceCount; i++) {
        VkPhysicalDeviceProperties props;
        vkGetPhysicalDeviceProperties(devices[i], &props);
        if (strstr(props.deviceName, "Mali") != NULL || props.vendorID == 0x13B5) {
            mali_device = devices[i];
            break;
        }
    }

    if (!mali_device) return 4;

    // Stage V4: Queue Family
    uint32_t queueFamilyCount = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(mali_device, &queueFamilyCount, NULL);
    VkQueueFamilyProperties* queueProps = (VkQueueFamilyProperties*)malloc(sizeof(VkQueueFamilyProperties) * queueFamilyCount);
    vkGetPhysicalDeviceQueueFamilyProperties(mali_device, &queueFamilyCount, queueProps);

    uint32_t selected_queue_idx = 0;

    // Stage V5: Logical Device & Queue
    float queuePriority = 1.0f;
    VkDeviceQueueCreateInfo queueCreateInfo = {};
    queueCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;
    queueCreateInfo.queueFamilyIndex = selected_queue_idx;
    queueCreateInfo.queueCount = 1;
    queueCreateInfo.pQueuePriorities = &queuePriority;

    VkDeviceCreateInfo deviceCreateInfo = {};
    deviceCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
    deviceCreateInfo.queueCreateInfoCount = 1;
    deviceCreateInfo.pQueueCreateInfos = &queueCreateInfo;

    VkDevice logical_device = VK_NULL_HANDLE;
    res = vkCreateDevice(mali_device, &deviceCreateInfo, NULL, &logical_device);
    if (res != VK_SUCCESS) return 5;

    PFN_vkGetDeviceQueue vkGetDeviceQueue = (PFN_vkGetDeviceQueue)vkGetDeviceProcAddr(logical_device, "vkGetDeviceQueue");
    VkQueue computeQueue = VK_NULL_HANDLE;
    vkGetDeviceQueue(logical_device, selected_queue_idx, 0, &computeQueue);

    // Get Function Pointers
    PFN_vkCreateShaderModule vkCreateShaderModule = (PFN_vkCreateShaderModule)vkGetDeviceProcAddr(logical_device, "vkCreateShaderModule");
    PFN_vkCreateDescriptorSetLayout vkCreateDescriptorSetLayout = (PFN_vkCreateDescriptorSetLayout)vkGetDeviceProcAddr(logical_device, "vkCreateDescriptorSetLayout");
    PFN_vkCreatePipelineLayout vkCreatePipelineLayout = (PFN_vkCreatePipelineLayout)vkGetDeviceProcAddr(logical_device, "vkCreatePipelineLayout");
    PFN_vkCreateComputePipelines vkCreateComputePipelines = (PFN_vkCreateComputePipelines)vkGetDeviceProcAddr(logical_device, "vkCreateComputePipelines");
    PFN_vkCreateDescriptorPool vkCreateDescriptorPool = (PFN_vkCreateDescriptorPool)vkGetDeviceProcAddr(logical_device, "vkCreateDescriptorPool");
    PFN_vkAllocateDescriptorSets vkAllocateDescriptorSets = (PFN_vkAllocateDescriptorSets)vkGetDeviceProcAddr(logical_device, "vkAllocateDescriptorSets");
    PFN_vkUpdateDescriptorSets vkUpdateDescriptorSets = (PFN_vkUpdateDescriptorSets)vkGetDeviceProcAddr(logical_device, "vkUpdateDescriptorSets");

    PFN_vkCreateCommandPool vkCreateCommandPool = (PFN_vkCreateCommandPool)vkGetDeviceProcAddr(logical_device, "vkCreateCommandPool");
    PFN_vkAllocateCommandBuffers vkAllocateCommandBuffers = (PFN_vkAllocateCommandBuffers)vkGetDeviceProcAddr(logical_device, "vkAllocateCommandBuffers");
    PFN_vkBeginCommandBuffer vkBeginCommandBuffer = (PFN_vkBeginCommandBuffer)vkGetDeviceProcAddr(logical_device, "vkBeginCommandBuffer");
    PFN_vkCmdBindPipeline vkCmdBindPipeline = (PFN_vkCmdBindPipeline)vkGetDeviceProcAddr(logical_device, "vkCmdBindPipeline");
    PFN_vkCmdBindDescriptorSets vkCmdBindDescriptorSets = (PFN_vkCmdBindDescriptorSets)vkGetDeviceProcAddr(logical_device, "vkCmdBindDescriptorSets");
    PFN_vkCmdDispatch vkCmdDispatch = (PFN_vkCmdDispatch)vkGetDeviceProcAddr(logical_device, "vkCmdDispatch");
    PFN_vkEndCommandBuffer vkEndCommandBuffer = (PFN_vkEndCommandBuffer)vkGetDeviceProcAddr(logical_device, "vkEndCommandBuffer");
    PFN_vkCreateFence vkCreateFence = (PFN_vkCreateFence)vkGetDeviceProcAddr(logical_device, "vkCreateFence");
    PFN_vkQueueSubmit vkQueueSubmit = (PFN_vkQueueSubmit)vkGetDeviceProcAddr(logical_device, "vkQueueSubmit");
    PFN_vkWaitForFences vkWaitForFences = (PFN_vkWaitForFences)vkGetDeviceProcAddr(logical_device, "vkWaitForFences");

    PFN_vkCreateBuffer vkCreateBuffer = (PFN_vkCreateBuffer)vkGetDeviceProcAddr(logical_device, "vkCreateBuffer");
    PFN_vkGetBufferMemoryRequirements vkGetBufferMemoryRequirements = (PFN_vkGetBufferMemoryRequirements)vkGetDeviceProcAddr(logical_device, "vkGetBufferMemoryRequirements");
    PFN_vkAllocateMemory vkAllocateMemory = (PFN_vkAllocateMemory)vkGetDeviceProcAddr(logical_device, "vkAllocateMemory");
    PFN_vkBindBufferMemory vkBindBufferMemory = (PFN_vkBindBufferMemory)vkGetDeviceProcAddr(logical_device, "vkBindBufferMemory");
    PFN_vkMapMemory vkMapMemory = (PFN_vkMapMemory)vkGetDeviceProcAddr(logical_device, "vkMapMemory");
    PFN_vkUnmapMemory vkUnmapMemory = (PFN_vkUnmapMemory)vkGetDeviceProcAddr(logical_device, "vkUnmapMemory");
    PFN_vkFreeMemory vkFreeMemory = (PFN_vkFreeMemory)vkGetDeviceProcAddr(logical_device, "vkFreeMemory");
    PFN_vkDestroyBuffer vkDestroyBuffer = (PFN_vkDestroyBuffer)vkGetDeviceProcAddr(logical_device, "vkDestroyBuffer");

    PFN_vkDestroyShaderModule vkDestroyShaderModule = (PFN_vkDestroyShaderModule)vkGetDeviceProcAddr(logical_device, "vkDestroyShaderModule");
    PFN_vkDestroyDescriptorSetLayout vkDestroyDescriptorSetLayout = (PFN_vkDestroyDescriptorSetLayout)vkGetDeviceProcAddr(logical_device, "vkDestroyDescriptorSetLayout");
    PFN_vkDestroyPipelineLayout vkDestroyPipelineLayout = (PFN_vkDestroyPipelineLayout)vkGetDeviceProcAddr(logical_device, "vkDestroyPipelineLayout");
    PFN_vkDestroyPipeline vkDestroyPipeline = (PFN_vkDestroyPipeline)vkGetDeviceProcAddr(logical_device, "vkDestroyPipeline");
    PFN_vkDestroyDescriptorPool vkDestroyDescriptorPool = (PFN_vkDestroyDescriptorPool)vkGetDeviceProcAddr(logical_device, "vkDestroyDescriptorPool");
    PFN_vkDestroyCommandPool vkDestroyCommandPool = (PFN_vkDestroyCommandPool)vkGetDeviceProcAddr(logical_device, "vkDestroyCommandPool");
    PFN_vkDestroyFence vkDestroyFence = (PFN_vkDestroyFence)vkGetDeviceProcAddr(logical_device, "vkDestroyFence");

    PFN_vkDeviceWaitIdle vkDeviceWaitIdle = (PFN_vkDeviceWaitIdle)vkGetDeviceProcAddr(logical_device, "vkDeviceWaitIdle");
    PFN_vkDestroyDevice vkDestroyDevice = (PFN_vkDestroyDevice)vkGetDeviceProcAddr(logical_device, "vkDestroyDevice");
    PFN_vkDestroyInstance vkDestroyInstance = (PFN_vkDestroyInstance)vkGetInstanceProcAddr(instance, "vkDestroyInstance");

    // Stage V6 Memory Setup: Input Buffer (1024 bytes) & Output Buffer (1024 bytes)
    VkPhysicalDeviceMemoryProperties memProperties = {};
    vkGetPhysicalDeviceMemoryProperties(mali_device, &memProperties);

    VkDeviceSize elem_count = 256;
    VkDeviceSize buf_bytes = elem_count * sizeof(uint32_t); // 1024 bytes

    VkBufferCreateInfo bufInfo = {};
    bufInfo.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bufInfo.size = buf_bytes;
    bufInfo.usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT;
    bufInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

    VkBuffer inBuffer = VK_NULL_HANDLE;
    VkBuffer outBuffer = VK_NULL_HANDLE;
    vkCreateBuffer(logical_device, &bufInfo, NULL, &inBuffer);
    vkCreateBuffer(logical_device, &bufInfo, NULL, &outBuffer);

    VkMemoryRequirements memReqs = {};
    vkGetBufferMemoryRequirements(logical_device, inBuffer, &memReqs);

    uint32_t memTypeIdx = 0;
    for (uint32_t i = 0; i < memProperties.memoryTypeCount; i++) {
        if (memReqs.memoryTypeBits & (1 << i)) {
            VkMemoryPropertyFlags flags = memProperties.memoryTypes[i].propertyFlags;
            if ((flags & VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT) && (flags & VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)) {
                memTypeIdx = i;
                break;
            }
        }
    }

    VkMemoryAllocateInfo allocInfo = {};
    allocInfo.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
    allocInfo.allocationSize = memReqs.size;
    allocInfo.memoryTypeIndex = memTypeIdx;

    VkDeviceMemory inMemory = VK_NULL_HANDLE;
    VkDeviceMemory outMemory = VK_NULL_HANDLE;
    vkAllocateMemory(logical_device, &allocInfo, NULL, &inMemory);
    vkAllocateMemory(logical_device, &allocInfo, NULL, &outMemory);

    vkBindBufferMemory(logical_device, inBuffer, inMemory, 0);
    vkBindBufferMemory(logical_device, outBuffer, outMemory, 0);

    // Populate Input Buffer (input[i] = i)
    uint32_t* inPtr = NULL;
    vkMapMemory(logical_device, inMemory, 0, buf_bytes, 0, (void**)&inPtr);
    for (uint32_t i = 0; i < elem_count; i++) {
        inPtr[i] = i;
    }
    vkUnmapMemory(logical_device, inMemory);

    // Zero-out Output Buffer initially
    uint32_t* outPtrInit = NULL;
    vkMapMemory(logical_device, outMemory, 0, buf_bytes, 0, (void**)&outPtrInit);
    memset(outPtrInit, 0, buf_bytes);
    vkUnmapMemory(logical_device, outMemory);

    // Stage V7: Create Compute Pipeline
    VkShaderModuleCreateInfo smInfo = {};
    smInfo.sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;
    smInfo.codeSize = spv_size;
    smInfo.pCode = spv_code;

    VkShaderModule shaderModule = VK_NULL_HANDLE;
    res = vkCreateShaderModule(logical_device, &smInfo, NULL, &shaderModule);
    printf("V7_SHADER_MODULE_RESULT=%d\n", res);

    VkDescriptorSetLayoutBinding bindings[2] = {};
    bindings[0].binding = 0;
    bindings[0].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    bindings[0].descriptorCount = 1;
    bindings[0].stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;

    bindings[1].binding = 1;
    bindings[1].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    bindings[1].descriptorCount = 1;
    bindings[1].stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;

    VkDescriptorSetLayoutCreateInfo dslInfo = {};
    dslInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO;
    dslInfo.bindingCount = 2;
    dslInfo.pBindings = bindings;

    VkDescriptorSetLayout dsLayout = VK_NULL_HANDLE;
    res = vkCreateDescriptorSetLayout(logical_device, &dslInfo, NULL, &dsLayout);
    printf("V7_DESCRIPTOR_LAYOUT_RESULT=%d\n", res);

    VkPipelineLayoutCreateInfo plInfo = {};
    plInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;
    plInfo.setLayoutCount = 1;
    plInfo.pSetLayouts = &dsLayout;

    VkPipelineLayout pipelineLayout = VK_NULL_HANDLE;
    res = vkCreatePipelineLayout(logical_device, &plInfo, NULL, &pipelineLayout);
    printf("V7_PIPELINE_LAYOUT_RESULT=%d\n", res);

    VkComputePipelineCreateInfo pipelineInfo = {};
    pipelineInfo.sType = VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO;
    pipelineInfo.stage.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    pipelineInfo.stage.stage = VK_SHADER_STAGE_COMPUTE_BIT;
    pipelineInfo.stage.module = shaderModule;
    pipelineInfo.stage.pName = "main";
    pipelineInfo.layout = pipelineLayout;

    VkPipeline computePipeline = VK_NULL_HANDLE;
    res = vkCreateComputePipelines(logical_device, VK_NULL_HANDLE, 1, &pipelineInfo, NULL, &computePipeline);
    printf("V7_COMPUTE_PIPELINE_RESULT=%d\n", res);

    if (res != VK_SUCCESS || !computePipeline) {
        printf("V7_RESULT=FAIL_VK_CREATE_COMPUTE_PIPELINES\n");
        return 7;
    }

    printf("V7_RESULT=PASS\n");

    // Allocate & Write Descriptor Set
    VkDescriptorPoolSize poolSize = {};
    poolSize.type = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    poolSize.descriptorCount = 2;

    VkDescriptorPoolCreateInfo poolInfo = {};
    poolInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;
    poolInfo.maxSets = 1;
    poolInfo.poolSizeCount = 1;
    poolInfo.pPoolSizes = &poolSize;

    VkDescriptorPool descriptorPool = VK_NULL_HANDLE;
    vkCreateDescriptorPool(logical_device, &poolInfo, NULL, &descriptorPool);

    VkDescriptorSetAllocateInfo dsAllocInfo = {};
    dsAllocInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO;
    dsAllocInfo.descriptorPool = descriptorPool;
    dsAllocInfo.descriptorSetCount = 1;
    dsAllocInfo.pSetLayouts = &dsLayout;

    VkDescriptorSet descriptorSet = VK_NULL_HANDLE;
    vkAllocateDescriptorSets(logical_device, &dsAllocInfo, &descriptorSet);

    VkDescriptorBufferInfo bufInfo0 = { inBuffer, 0, buf_bytes };
    VkDescriptorBufferInfo bufInfo1 = { outBuffer, 0, buf_bytes };

    VkWriteDescriptorSet writeDS[2] = {};
    writeDS[0].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
    writeDS[0].dstSet = descriptorSet;
    writeDS[0].dstBinding = 0;
    writeDS[0].descriptorCount = 1;
    writeDS[0].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    writeDS[0].pBufferInfo = &bufInfo0;

    writeDS[1].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
    writeDS[1].dstSet = descriptorSet;
    writeDS[1].dstBinding = 1;
    writeDS[1].descriptorCount = 1;
    writeDS[1].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    writeDS[1].pBufferInfo = &bufInfo1;

    vkUpdateDescriptorSets(logical_device, 2, writeDS, 0, NULL);

    // Stage V8: GPU Dispatch Execution
    VkCommandPoolCreateInfo cmdPoolInfo = {};
    cmdPoolInfo.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
    cmdPoolInfo.queueFamilyIndex = selected_queue_idx;

    VkCommandPool commandPool = VK_NULL_HANDLE;
    res = vkCreateCommandPool(logical_device, &cmdPoolInfo, NULL, &commandPool);
    printf("V8_COMMAND_POOL_RESULT=%d\n", res);

    VkCommandBufferAllocateInfo cmdAllocInfo = {};
    cmdAllocInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
    cmdAllocInfo.commandPool = commandPool;
    cmdAllocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    cmdAllocInfo.commandBufferCount = 1;

    VkCommandBuffer commandBuffer = VK_NULL_HANDLE;
    res = vkAllocateCommandBuffers(logical_device, &cmdAllocInfo, &commandBuffer);
    printf("V8_COMMAND_BUFFER_RESULT=%d\n", res);

    VkCommandBufferBeginInfo beginInfo = {};
    beginInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    vkBeginCommandBuffer(commandBuffer, &beginInfo);

    vkCmdBindPipeline(commandBuffer, VK_PIPELINE_BIND_POINT_COMPUTE, computePipeline);
    vkCmdBindDescriptorSets(commandBuffer, VK_PIPELINE_BIND_POINT_COMPUTE, pipelineLayout, 0, 1, &descriptorSet, 0, NULL);

    // 256 elements / 64 local_size_x = 4 workgroups
    uint32_t groupCountX = 4;
    printf("V8_DISPATCH_GROUPS=(%u, 1, 1)\n", groupCountX);
    vkCmdDispatch(commandBuffer, groupCountX, 1, 1);

    vkEndCommandBuffer(commandBuffer);

    VkFenceCreateInfo fenceInfo = {};
    fenceInfo.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;
    VkFence fence = VK_NULL_HANDLE;
    vkCreateFence(logical_device, &fenceInfo, NULL, &fence);

    VkSubmitInfo submitInfo = {};
    submitInfo.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
    submitInfo.commandBufferCount = 1;
    submitInfo.pCommandBuffers = &commandBuffer;

    res = vkQueueSubmit(computeQueue, 1, &submitInfo, fence);
    printf("V8_QUEUE_SUBMIT_RESULT=%d\n", res);

    // Wait for fence with 5-second timeout (5,000,000,000 ns)
    res = vkWaitForFences(logical_device, 1, &fence, VK_TRUE, 5000000000ULL);
    printf("V8_FENCE_WAIT_RESULT=%d\n", res);

    if (res != VK_SUCCESS) {
        printf("V8_RESULT=FAIL_GPU_FENCE_TIMEOUT\n");
        return 8;
    }
    printf("V8_RESULT=PASS\n");

    // Stage V9: Read Back GPU Results & Validate Checksum
    uint32_t* outData = NULL;
    vkMapMemory(logical_device, outMemory, 0, buf_bytes, 0, (void**)&outData);

    uint32_t mismatch_count = 0;
    uint64_t actual_checksum = 0;
    uint64_t expected_checksum = 0;

    for (uint32_t i = 0; i < elem_count; i++) {
        uint32_t expected_val = i * 2 + 1;
        uint32_t actual_val = outData[i];

        expected_checksum += expected_val;
        actual_checksum += actual_val;

        if (actual_val != expected_val) {
            mismatch_count++;
            if (mismatch_count <= 5) {
                printf("[V9] Mismatch at index %u: expected %u, got %u\n", i, expected_val, actual_val);
            }
        }
    }
    vkUnmapMemory(logical_device, outMemory);

    printf("V9_ELEMENT_COUNT=%llu\n", (unsigned long long)elem_count);
    printf("V9_EXPECTED_CHECKSUM=%llu\n", (unsigned long long)expected_checksum);
    printf("V9_ACTUAL_CHECKSUM=%llu\n", (unsigned long long)actual_checksum);
    printf("V9_MISMATCH_COUNT=%u\n", mismatch_count);

    bool v9_pass = (mismatch_count == 0 && actual_checksum == expected_checksum);
    printf("V9_RESULT=%s\n", v9_pass ? "PASS" : "FAIL");

    // Clean up resources cleanly in strict order
    vkDeviceWaitIdle(logical_device);

    vkDestroyFence(logical_device, fence, NULL);
    vkDestroyCommandPool(logical_device, commandPool, NULL);
    vkDestroyPipeline(logical_device, computePipeline, NULL);
    vkDestroyPipelineLayout(logical_device, pipelineLayout, NULL);
    vkDestroyDescriptorSetLayout(logical_device, dsLayout, NULL);
    vkDestroyDescriptorPool(logical_device, descriptorPool, NULL);
    vkDestroyShaderModule(logical_device, shaderModule, NULL);

    vkDestroyBuffer(logical_device, inBuffer, NULL);
    vkDestroyBuffer(logical_device, outBuffer, NULL);
    vkFreeMemory(logical_device, inMemory, NULL);
    vkFreeMemory(logical_device, outMemory, NULL);

    vkDestroyDevice(logical_device, NULL);
    vkDestroyInstance(instance, NULL);
    dlclose(handle);

    free(queueProps);
    free(devices);
    free(spv_code);

    printf("CLEANUP_RESULT=PASS\n");
    printf("PROCESS_RC=0\n");
    printf("RESULT=%s\n", v9_pass ? "PASS_V7_V8_V9_MALI_COMPUTE_DISPATCH_SUCCESSFUL" : "FAIL_V9_RESULT_MISMATCH");

    return v9_pass ? 0 : 9;
}
