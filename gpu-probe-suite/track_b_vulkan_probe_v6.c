#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <dlfcn.h>
#include <vulkan/vulkan.h>

int main() {
    printf("=== TRACK B VULKAN PLAYBOOK CAPABILITY PROBE (V0-V6) ===\n");

    // Stage V0: Android System Vulkan Loader
    void* handle = dlopen("libvulkan.so", RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        printf("[V0] FAIL: dlopen libvulkan.so failed: %s\n", dlerror());
        return 1;
    }

    PFN_vkGetInstanceProcAddr vkGetInstanceProcAddr = (PFN_vkGetInstanceProcAddr)dlsym(handle, "vkGetInstanceProcAddr");
    if (!vkGetInstanceProcAddr) return 2;

    PFN_vkCreateInstance vkCreateInstance = (PFN_vkCreateInstance)vkGetInstanceProcAddr(NULL, "vkCreateInstance");

    // Stage V1: Create Vulkan Instance
    VkApplicationInfo appInfo = {};
    appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    appInfo.pApplicationName = "Track B Mali V6 Probe";
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

    // Stage V2 & V3: Physical Device Selection (Mali-G78)
    uint32_t deviceCount = 0;
    vkEnumeratePhysicalDevices(instance, &deviceCount, NULL);
    VkPhysicalDevice* devices = (VkPhysicalDevice*)malloc(sizeof(VkPhysicalDevice) * deviceCount);
    vkEnumeratePhysicalDevices(instance, &deviceCount, devices);

    VkPhysicalDevice mali_device = VK_NULL_HANDLE;
    VkPhysicalDeviceProperties mali_props = {};
    for (uint32_t i = 0; i < deviceCount; i++) {
        VkPhysicalDeviceProperties props;
        vkGetPhysicalDeviceProperties(devices[i], &props);
        if (strstr(props.deviceName, "Mali") != NULL || props.vendorID == 0x13B5) {
            mali_device = devices[i];
            mali_props = props;
            break;
        }
    }

    if (!mali_device) {
        printf("RESULT=FAIL_MALI_NOT_FOUND\n");
        free(devices);
        return 4;
    }

    // Stage V4: Queue Family Selection
    uint32_t queueFamilyCount = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(mali_device, &queueFamilyCount, NULL);
    VkQueueFamilyProperties* queueProps = (VkQueueFamilyProperties*)malloc(sizeof(VkQueueFamilyProperties) * queueFamilyCount);
    vkGetPhysicalDeviceQueueFamilyProperties(mali_device, &queueFamilyCount, queueProps);

    int selected_queue_idx = -1;
    for (uint32_t i = 0; i < queueFamilyCount; i++) {
        if ((queueProps[i].queueFlags & VK_QUEUE_COMPUTE_BIT) && queueProps[i].queueCount >= 1) {
            selected_queue_idx = (int)i;
            break;
        }
    }

    // Stage V5: Logical Device Creation
    float queuePriority = 1.0f;
    VkDeviceQueueCreateInfo queueCreateInfo = {};
    queueCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;
    queueCreateInfo.queueFamilyIndex = (uint32_t)selected_queue_idx;
    queueCreateInfo.queueCount = 1;
    queueCreateInfo.pQueuePriorities = &queuePriority;

    VkDeviceCreateInfo deviceCreateInfo = {};
    deviceCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
    deviceCreateInfo.queueCreateInfoCount = 1;
    deviceCreateInfo.pQueueCreateInfos = &queueCreateInfo;

    VkDevice logical_device = VK_NULL_HANDLE;
    res = vkCreateDevice(mali_device, &deviceCreateInfo, NULL, &logical_device);
    if (res != VK_SUCCESS) {
        printf("RESULT=FAIL_VK_CREATE_DEVICE\n");
        free(queueProps);
        free(devices);
        return 5;
    }

    PFN_vkCreateBuffer vkCreateBuffer = (PFN_vkCreateBuffer)vkGetDeviceProcAddr(logical_device, "vkCreateBuffer");
    PFN_vkGetBufferMemoryRequirements vkGetBufferMemoryRequirements = (PFN_vkGetBufferMemoryRequirements)vkGetDeviceProcAddr(logical_device, "vkGetBufferMemoryRequirements");
    PFN_vkAllocateMemory vkAllocateMemory = (PFN_vkAllocateMemory)vkGetDeviceProcAddr(logical_device, "vkAllocateMemory");
    PFN_vkBindBufferMemory vkBindBufferMemory = (PFN_vkBindBufferMemory)vkGetDeviceProcAddr(logical_device, "vkBindBufferMemory");
    PFN_vkMapMemory vkMapMemory = (PFN_vkMapMemory)vkGetDeviceProcAddr(logical_device, "vkMapMemory");
    PFN_vkUnmapMemory vkUnmapMemory = (PFN_vkUnmapMemory)vkGetDeviceProcAddr(logical_device, "vkUnmapMemory");
    PFN_vkFlushMappedMemoryRanges vkFlushMappedMemoryRanges = (PFN_vkFlushMappedMemoryRanges)vkGetDeviceProcAddr(logical_device, "vkFlushMappedMemoryRanges");
    PFN_vkFreeMemory vkFreeMemory = (PFN_vkFreeMemory)vkGetDeviceProcAddr(logical_device, "vkFreeMemory");
    PFN_vkDestroyBuffer vkDestroyBuffer = (PFN_vkDestroyBuffer)vkGetDeviceProcAddr(logical_device, "vkDestroyBuffer");
    PFN_vkDeviceWaitIdle vkDeviceWaitIdle = (PFN_vkDeviceWaitIdle)vkGetDeviceProcAddr(logical_device, "vkDeviceWaitIdle");
    PFN_vkDestroyDevice vkDestroyDevice = (PFN_vkDestroyDevice)vkGetDeviceProcAddr(logical_device, "vkDestroyDevice");
    PFN_vkDestroyInstance vkDestroyInstance = (PFN_vkDestroyInstance)vkGetInstanceProcAddr(instance, "vkDestroyInstance");

    // Stage V6: Physical Device Memory Properties
    VkPhysicalDeviceMemoryProperties memProperties = {};
    vkGetPhysicalDeviceMemoryProperties(mali_device, &memProperties);

    printf("V6_MEMORY_HEAP_COUNT=%u\n", memProperties.memoryHeapCount);
    printf("V6_MEMORY_TYPE_COUNT=%u\n", memProperties.memoryTypeCount);

    for (uint32_t i = 0; i < memProperties.memoryTypeCount; i++) {
        VkMemoryType type = memProperties.memoryTypes[i];
        printf("[V6] Memory Type #%u: heapIndex=%u, flags=0x%08x (HostVisible:%s, HostCoherent:%s, DeviceLocal:%s)\n",
               i, type.heapIndex, type.propertyFlags,
               (type.propertyFlags & VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT) ? "YES" : "NO",
               (type.propertyFlags & VK_MEMORY_PROPERTY_HOST_COHERENT_BIT) ? "YES" : "NO",
               (type.propertyFlags & VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT) ? "YES" : "NO");
    }

    // 6. Create 64 KiB Storage Buffer
    VkDeviceSize buffer_size = 64 * 1024; // 64 KiB
    VkBufferCreateInfo bufferCreateInfo = {};
    bufferCreateInfo.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bufferCreateInfo.size = buffer_size;
    bufferCreateInfo.usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT;
    bufferCreateInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

    printf("V6_BUFFER_SIZE=%llu\n", (unsigned long long)buffer_size);
    printf("V6_BUFFER_USAGE=STORAGE_BUFFER_BIT (0x02)\n");

    VkBuffer buffer = VK_NULL_HANDLE;
    res = vkCreateBuffer(logical_device, &bufferCreateInfo, NULL, &buffer);
    printf("V6_CREATE_BUFFER_RESULT=%d (VK_SUCCESS=0)\n", res);
    if (res != VK_SUCCESS) {
        printf("RESULT=FAIL_VK_CREATE_BUFFER\n");
        return 6;
    }

    // Get Buffer Memory Requirements
    VkMemoryRequirements memReqs = {};
    vkGetBufferMemoryRequirements(logical_device, buffer, &memReqs);

    printf("V6_REQUIREMENT_SIZE=%llu\n", (unsigned long long)memReqs.size);
    printf("V6_REQUIREMENT_ALIGNMENT=%llu\n", (unsigned long long)memReqs.alignment);
    printf("V6_MEMORY_TYPE_BITS=0x%08x\n", memReqs.memoryTypeBits);

    // Find suitable Memory Type Index (Prefer HOST_VISIBLE + HOST_COHERENT)
    int selected_mem_type_idx = -1;
    VkMemoryPropertyFlags selected_mem_flags = 0;
    bool host_visible = false;
    bool host_coherent = false;

    for (uint32_t i = 0; i < memProperties.memoryTypeCount; i++) {
        if (memReqs.memoryTypeBits & (1 << i)) {
            VkMemoryPropertyFlags flags = memProperties.memoryTypes[i].propertyFlags;
            if ((flags & VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT) && (flags & VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)) {
                selected_mem_type_idx = (int)i;
                selected_mem_flags = flags;
                host_visible = true;
                host_coherent = true;
                break;
            } else if ((flags & VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT) && selected_mem_type_idx == -1) {
                selected_mem_type_idx = (int)i;
                selected_mem_flags = flags;
                host_visible = true;
                host_coherent = false;
            }
        }
    }

    if (selected_mem_type_idx == -1) {
        printf("V6_SELECTED_MEMORY_TYPE_INDEX=-1\n");
        printf("RESULT=FAIL_NO_HOST_VISIBLE_MEMORY_TYPE\n");
        vkDestroyBuffer(logical_device, buffer, NULL);
        return 7;
    }

    printf("V6_SELECTED_MEMORY_TYPE_INDEX=%d\n", selected_mem_type_idx);
    printf("V6_SELECTED_MEMORY_FLAGS=0x%08x\n", selected_mem_flags);
    printf("V6_HOST_VISIBLE=%s\n", host_visible ? "TRUE" : "FALSE");
    printf("V6_HOST_COHERENT=%s\n", host_coherent ? "TRUE" : "FALSE");

    // Allocate Device Memory
    VkMemoryAllocateInfo allocInfo = {};
    allocInfo.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
    allocInfo.allocationSize = memReqs.size;
    allocInfo.memoryTypeIndex = (uint32_t)selected_mem_type_idx;

    VkDeviceMemory deviceMemory = VK_NULL_HANDLE;
    res = vkAllocateMemory(logical_device, &allocInfo, NULL, &deviceMemory);
    printf("V6_ALLOCATE_MEMORY_RESULT=%d (VK_SUCCESS=0)\n", res);
    if (res != VK_SUCCESS) {
        printf("RESULT=FAIL_VK_ALLOCATE_MEMORY\n");
        vkDestroyBuffer(logical_device, buffer, NULL);
        return 8;
    }

    // Bind Buffer to Memory
    res = vkBindBufferMemory(logical_device, buffer, deviceMemory, 0);
    printf("V6_BIND_BUFFER_RESULT=%d (VK_SUCCESS=0)\n", res);
    if (res != VK_SUCCESS) {
        printf("RESULT=FAIL_VK_BIND_BUFFER_MEMORY\n");
        vkFreeMemory(logical_device, deviceMemory, NULL);
        vkDestroyBuffer(logical_device, buffer, NULL);
        return 9;
    }

    // Map Memory and Write Deterministic Test Pattern
    void* mappedData = NULL;
    res = vkMapMemory(logical_device, deviceMemory, 0, memReqs.size, 0, &mappedData);
    printf("V6_MAP_MEMORY_RESULT=%d (VK_SUCCESS=0)\n", res);
    if (res != VK_SUCCESS || !mappedData) {
        printf("RESULT=FAIL_VK_MAP_MEMORY\n");
        vkFreeMemory(logical_device, deviceMemory, NULL);
        vkDestroyBuffer(logical_device, buffer, NULL);
        return 10;
    }

    // Write uint32 pattern
    uint32_t num_elements = (uint32_t)(buffer_size / sizeof(uint32_t));
    uint32_t* ptr = (uint32_t*)mappedData;
    for (uint32_t i = 0; i < num_elements; i++) {
        ptr[i] = i * 0x01010101;
    }

    bool flush_req = !host_coherent;
    printf("V6_FLUSH_REQUIRED=%s\n", flush_req ? "TRUE" : "FALSE");
    if (flush_req) {
        VkMappedMemoryRange range = {};
        range.sType = VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE;
        range.memory = deviceMemory;
        range.offset = 0;
        range.size = memReqs.size;
        vkFlushMappedMemoryRanges(logical_device, 1, &range);
    }

    // Read Back and Verify Pattern
    bool write_verify_ok = true;
    for (uint32_t i = 0; i < num_elements; i++) {
        if (ptr[i] != i * 0x01010101) {
            write_verify_ok = false;
            printf("Pattern mismatch at index %u: expected 0x%08x, got 0x%08x\n", i, i * 0x01010101, ptr[i]);
            break;
        }
    }
    printf("V6_PATTERN_WRITE_VERIFY=%s\n", write_verify_ok ? "PASS" : "FAIL");

    vkUnmapMemory(logical_device, deviceMemory);

    // Resource Cleanup
    vkDestroyBuffer(logical_device, buffer, NULL);
    vkFreeMemory(logical_device, deviceMemory, NULL);

    vkDeviceWaitIdle(logical_device);
    vkDestroyDevice(logical_device, NULL);
    vkDestroyInstance(instance, NULL);
    dlclose(handle);

    free(queueProps);
    free(devices);

    printf("V6_CLEANUP_RESULT=PASS\n");
    printf("PROCESS_RC=0\n");
    printf("RESULT=PASS_V6_MALI_MEMORY_ALLOCATION_AND_HOST_MAPPING\n");

    return 0;
}
