#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <dlfcn.h>
#include <vulkan/vulkan.h>

int main() {
    printf("=== TRACK B VULKAN PLAYBOOK CAPABILITY PROBE (V0-V3) ===\n");

    // Stage V0: Android System Vulkan Loader
    printf("[V0] Opening system libvulkan.so via dlopen...\n");
    void* handle = dlopen("libvulkan.so", RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        printf("[V0] FAIL: Failed to dlopen libvulkan.so: %s\n", dlerror());
        return 1;
    }
    printf("[V0] SUCCESS: libvulkan.so loaded at %p\n", handle);

    PFN_vkGetInstanceProcAddr vkGetInstanceProcAddr = (PFN_vkGetInstanceProcAddr)dlsym(handle, "vkGetInstanceProcAddr");
    if (!vkGetInstanceProcAddr) {
        printf("[V0] FAIL: vkGetInstanceProcAddr not found in libvulkan.so\n");
        return 2;
    }

    PFN_vkCreateInstance vkCreateInstance = (PFN_vkCreateInstance)vkGetInstanceProcAddr(NULL, "vkCreateInstance");
    PFN_vkEnumeratePhysicalDevices vkEnumeratePhysicalDevices = NULL;

    // Stage V1: Create Vulkan Instance
    printf("[V1] Creating Vulkan Instance...\n");
    VkApplicationInfo appInfo = {};
    appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    appInfo.pApplicationName = "Track B Mali Probe";
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
        printf("[V1] FAIL: vkCreateInstance returned VkResult=%d\n", res);
        return 3;
    }
    printf("[V1] SUCCESS: Vulkan Instance created (%p)\n", (void*)instance);

    vkEnumeratePhysicalDevices = (PFN_vkEnumeratePhysicalDevices)vkGetInstanceProcAddr(instance, "vkEnumeratePhysicalDevices");
    PFN_vkGetPhysicalDeviceProperties vkGetPhysicalDeviceProperties = (PFN_vkGetPhysicalDeviceProperties)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceProperties");

    // Stage V2: Enumerate Physical Devices
    printf("[V2] Enumerating Physical Devices...\n");
    uint32_t deviceCount = 0;
    res = vkEnumeratePhysicalDevices(instance, &deviceCount, NULL);
    if (res != VK_SUCCESS || deviceCount == 0) {
        printf("[V2] FAIL: vkEnumeratePhysicalDevices returned count=%u, VkResult=%d\n", deviceCount, res);
        return 4;
    }
    printf("[V2] SUCCESS: Found %u physical device(s)\n", deviceCount);

    VkPhysicalDevice* devices = (VkPhysicalDevice*)malloc(sizeof(VkPhysicalDevice) * deviceCount);
    vkEnumeratePhysicalDevices(instance, &deviceCount, devices);

    // Stage V3: Inspect Physical Device & Mali-G78 Selection
    printf("[V3] Inspecting Physical Devices for Mali-G78 Hardware GPU...\n");
    bool mali_found = false;
    for (uint32_t i = 0; i < deviceCount; i++) {
        VkPhysicalDeviceProperties props;
        vkGetPhysicalDeviceProperties(devices[i], &props);

        const char* type_str = "UNKNOWN";
        if (props.deviceType == VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU) type_str = "INTEGRATED_GPU";
        else if (props.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU) type_str = "DISCRETE_GPU";
        else if (props.deviceType == VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU) type_str = "VIRTUAL_GPU";
        else if (props.deviceType == VK_PHYSICAL_DEVICE_TYPE_CPU) type_str = "CPU_SOFTWARE_RASTERIZER";

        printf("  Device #%u: '%s'\n", i, props.deviceName);
        printf("    Type       : %s (%d)\n", type_str, props.deviceType);
        printf("    Vendor ID  : 0x%04x\n", props.vendorID);
        printf("    Device ID  : 0x%04x\n", props.deviceID);
        printf("    Driver Ver : 0x%08x\n", props.driverVersion);
        printf("    API Ver    : %u.%u.%u\n",
               VK_VERSION_MAJOR(props.apiVersion),
               VK_VERSION_MINOR(props.apiVersion),
               VK_VERSION_PATCH(props.apiVersion));

        if (strstr(props.deviceName, "Mali") != NULL || props.vendorID == 0x13B5) {
            mali_found = true;
            printf("    >>> MALI HARDWARE GPU DETECTED: %s <<<\n", props.deviceName);
        }
    }

    free(devices);
    PFN_vkDestroyInstance vkDestroyInstance = (PFN_vkDestroyInstance)vkGetInstanceProcAddr(instance, "vkDestroyInstance");
    vkDestroyInstance(instance, NULL);
    dlclose(handle);

    if (mali_found) {
        printf("[V3] RESULT: PASS - Mali-G78 Hardware Physical Device Successfully Enumerated!\n");
        return 0;
    } else {
        printf("[V3] RESULT: FAIL - Mali Hardware GPU NOT Enumerated (Only Software Rasterizer / No Hardware HAL Driver Found)\n");
        return 5;
    }
}
