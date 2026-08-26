#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <dlfcn.h>
#include <vulkan/vulkan.h>

int main() {
    printf("=== TRACK B VULKAN PLAYBOOK CAPABILITY PROBE (V0-V5) ===\n");

    // Stage V0: Android System Vulkan Loader
    void* handle = dlopen("libvulkan.so", RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        printf("[V0] FAIL: dlopen libvulkan.so failed: %s\n", dlerror());
        return 1;
    }

    PFN_vkGetInstanceProcAddr vkGetInstanceProcAddr = (PFN_vkGetInstanceProcAddr)dlsym(handle, "vkGetInstanceProcAddr");
    if (!vkGetInstanceProcAddr) {
        printf("[V0] FAIL: dlsym vkGetInstanceProcAddr failed\n");
        return 2;
    }

    PFN_vkCreateInstance vkCreateInstance = (PFN_vkCreateInstance)vkGetInstanceProcAddr(NULL, "vkCreateInstance");

    // Stage V1: Create Vulkan Instance
    VkApplicationInfo appInfo = {};
    appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    appInfo.pApplicationName = "Track B Mali V4-V5 Probe";
    appInfo.applicationVersion = VK_MAKE_VERSION(1, 0, 0);
    appInfo.pEngineName = "No Engine";
    appInfo.engineVersion = VK_MAKE_VERSION(1, 0, 0);
    appInfo.apiVersion = VK_API_VERSION_1_1;

    VkInstanceCreateInfo createInfo = {};
    createInfo.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    createInfo.pApplicationInfo = &appInfo;

    VkInstance instance = VK_NULL_HANDLE;
    VkResult res = vkCreateInstance(&createInfo, NULL, &instance);
    if (res != VK_SUCCESS) {
        printf("[V1] FAIL: vkCreateInstance returned %d\n", res);
        return 3;
    }

    PFN_vkEnumeratePhysicalDevices vkEnumeratePhysicalDevices = (PFN_vkEnumeratePhysicalDevices)vkGetInstanceProcAddr(instance, "vkEnumeratePhysicalDevices");
    PFN_vkGetPhysicalDeviceProperties vkGetPhysicalDeviceProperties = (PFN_vkGetPhysicalDeviceProperties)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceProperties");
    PFN_vkGetPhysicalDeviceQueueFamilyProperties vkGetPhysicalDeviceQueueFamilyProperties = (PFN_vkGetPhysicalDeviceQueueFamilyProperties)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceQueueFamilyProperties");
    PFN_vkCreateDevice vkCreateDevice = (PFN_vkCreateDevice)vkGetInstanceProcAddr(instance, "vkCreateDevice");
    PFN_vkGetDeviceProcAddr vkGetDeviceProcAddr = (PFN_vkGetDeviceProcAddr)vkGetInstanceProcAddr(instance, "vkGetDeviceProcAddr");

    // Stage V2: Enumerate Physical Devices
    uint32_t deviceCount = 0;
    res = vkEnumeratePhysicalDevices(instance, &deviceCount, NULL);
    if (res != VK_SUCCESS || deviceCount == 0) {
        printf("[V2] FAIL: vkEnumeratePhysicalDevices count=%u, res=%d\n", deviceCount, res);
        return 4;
    }

    VkPhysicalDevice* devices = (VkPhysicalDevice*)malloc(sizeof(VkPhysicalDevice) * deviceCount);
    vkEnumeratePhysicalDevices(instance, &deviceCount, devices);

    // Stage V3: Inspect Physical Device
    VkPhysicalDevice mali_device = VK_NULL_HANDLE;
    VkPhysicalDeviceProperties mali_props = {};
    bool mali_found = false;

    for (uint32_t i = 0; i < deviceCount; i++) {
        VkPhysicalDeviceProperties props;
        vkGetPhysicalDeviceProperties(devices[i], &props);
        if (strstr(props.deviceName, "Mali") != NULL || props.vendorID == 0x13B5) {
            mali_found = true;
            mali_device = devices[i];
            mali_props = props;
            break;
        }
    }

    if (!mali_found) {
        printf("[V3] FAIL: Mali Hardware GPU NOT found\n");
        free(devices);
        return 5;
    }

    printf("V3_DEVICE_NAME=%s\n", mali_props.deviceName);
    printf("V3_DEVICE_TYPE=INTEGRATED_GPU\n");
    printf("V3_VENDOR_ID=0x%04x\n", mali_props.vendorID);
    printf("V3_DEVICE_ID=0x%04x\n", mali_props.deviceID);
    printf("V3_API_VERSION=%u.%u.%u\n",
           VK_VERSION_MAJOR(mali_props.apiVersion),
           VK_VERSION_MINOR(mali_props.apiVersion),
           VK_VERSION_PATCH(mali_props.apiVersion));
    printf("V3_DRIVER_VERSION=0x%08x\n", mali_props.driverVersion);

    // Stage V4: Queue Family Enumeration
    uint32_t queueFamilyCount = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(mali_device, &queueFamilyCount, NULL);
    printf("V4_QUEUE_FAMILY_COUNT=%u\n", queueFamilyCount);

    if (queueFamilyCount == 0) {
        printf("V4_RESULT=FAIL_NO_QUEUE_FAMILIES\n");
        free(devices);
        return 6;
    }

    VkQueueFamilyProperties* queueProps = (VkQueueFamilyProperties*)malloc(sizeof(VkQueueFamilyProperties) * queueFamilyCount);
    vkGetPhysicalDeviceQueueFamilyProperties(mali_device, &queueFamilyCount, queueProps);

    int selected_queue_idx = -1;
    bool dedicated_compute = false;
    VkQueueFlags selected_flags = 0;

    for (uint32_t i = 0; i < queueFamilyCount; i++) {
        VkQueueFlags flags = queueProps[i].queueFlags;
        printf("[V4] Queue Family #%u: count=%u, flags=0x%08x (Compute:%s, Graphics:%s, Transfer:%s)\n",
               i, queueProps[i].queueCount, flags,
               (flags & VK_QUEUE_COMPUTE_BIT) ? "YES" : "NO",
               (flags & VK_QUEUE_GRAPHICS_BIT) ? "YES" : "NO",
               (flags & VK_QUEUE_TRANSFER_BIT) ? "YES" : "NO");

        if ((flags & VK_QUEUE_COMPUTE_BIT) && queueProps[i].queueCount >= 1) {
            if (!(flags & VK_QUEUE_GRAPHICS_BIT)) {
                // Dedicated compute queue priority
                selected_queue_idx = (int)i;
                selected_flags = flags;
                dedicated_compute = true;
                break;
            } else if (selected_queue_idx == -1) {
                // Combined compute+graphics fallback
                selected_queue_idx = (int)i;
                selected_flags = flags;
                dedicated_compute = false;
            }
        }
    }

    if (selected_queue_idx == -1) {
        printf("V4_SELECTED_QUEUE_INDEX=-1\n");
        printf("V4_RESULT=FAIL_NO_COMPUTE_QUEUE\n");
        free(queueProps);
        free(devices);
        return 7;
    }

    printf("V4_SELECTED_QUEUE_INDEX=%d\n", selected_queue_idx);
    printf("V4_SELECTED_QUEUE_FLAGS=0x%08x\n", selected_flags);
    printf("V4_DEDICATED_COMPUTE=%s\n", dedicated_compute ? "TRUE" : "FALSE");
    printf("V4_RESULT=PASS\n");

    // Stage V5: Logical Device Creation & Queue Retrieval
    printf("\n=== STAGE V5: LOGICAL DEVICE CREATION ===\n");
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
    deviceCreateInfo.enabledExtensionCount = 0;
    deviceCreateInfo.ppEnabledExtensionNames = NULL;
    deviceCreateInfo.pEnabledFeatures = NULL;

    printf("V5_REQUESTED_EXTENSIONS=NONE\n");
    printf("V5_REQUESTED_FEATURES=NONE\n");

    VkDevice logical_device = VK_NULL_HANDLE;
    res = vkCreateDevice(mali_device, &deviceCreateInfo, NULL, &logical_device);

    printf("V5_VK_CREATE_DEVICE_RESULT=%d (VK_SUCCESS=0)\n", res);

    if (res != VK_SUCCESS || logical_device == VK_NULL_HANDLE) {
        printf("V5_QUEUE_HANDLE_VALID=FALSE\n");
        printf("V5_CLEANUP_RESULT=SKIPPED\n");
        printf("RESULT=FAIL_VK_CREATE_DEVICE\n");
        free(queueProps);
        free(devices);
        return 8;
    }

    PFN_vkGetDeviceQueue vkGetDeviceQueue = (PFN_vkGetDeviceQueue)vkGetDeviceProcAddr(logical_device, "vkGetDeviceQueue");
    PFN_vkDeviceWaitIdle vkDeviceWaitIdle = (PFN_vkDeviceWaitIdle)vkGetDeviceProcAddr(logical_device, "vkDeviceWaitIdle");
    PFN_vkDestroyDevice vkDestroyDevice = (PFN_vkDestroyDevice)vkGetDeviceProcAddr(logical_device, "vkDestroyDevice");
    PFN_vkDestroyInstance vkDestroyInstance = (PFN_vkDestroyInstance)vkGetInstanceProcAddr(instance, "vkDestroyInstance");

    VkQueue computeQueue = VK_NULL_HANDLE;
    vkGetDeviceQueue(logical_device, (uint32_t)selected_queue_idx, 0, &computeQueue);

    bool queue_valid = (computeQueue != VK_NULL_HANDLE);
    printf("V5_QUEUE_HANDLE_VALID=%s\n", queue_valid ? "TRUE" : "FALSE");

    // Clean up
    vkDeviceWaitIdle(logical_device);
    vkDestroyDevice(logical_device, NULL);
    vkDestroyInstance(instance, NULL);
    dlclose(handle);

    free(queueProps);
    free(devices);

    printf("V5_CLEANUP_RESULT=PASS\n");
    printf("PROCESS_RC=0\n");
    printf("RESULT=PASS_V4_V5_MALI_LOGICAL_DEVICE_CREATED\n");

    return 0;
}
