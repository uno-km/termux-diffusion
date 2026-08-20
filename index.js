/**
 * termux-diffusion: Production On-Device AI Image Generation for Android Termux & Samsung Galaxy
 * Dual-Engine (Node.js & TypeScript) Native Module with Vulkan/OpenCL & NPU/TPU Hardware Acceleration
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn, spawnSync } = require('child_process');
const https = require('https');
const crypto = require('crypto');

const DEFAULT_PRESETS = {
  realistic: {
    repo_id: 'second-state/Realistic_Vision_V6.0_B1-GGUF',
    filename: 'realisticVisionV60B1_v51HyperVAE-Q4_k.gguf',
    alias: 'realistic.gguf',
    description: 'Realistic Vision V6.0 B1 (Q4_K) - Ultra-detailed photorealistic portraits',
    size_mb: 1620,
    default_steps: 10,
    default_cfg: 4.0
  },
  speed: {
    repo_id: 'gpustack/stable-diffusion-v1-5-GGUF',
    filename: 'stable-diffusion-v1-5-Q4_1.gguf',
    alias: 'lightning.gguf',
    description: 'Stable Diffusion 1.5 (Q4_1) - Fast general-purpose base model',
    size_mb: 1590,
    default_steps: 10,
    default_cfg: 4.0
  },
  sdxs: {
    repo_id: 'gpustack/SDXS-512-0.9-GGUF',
    filename: 'sdxs-512-0.9-Q4_0.gguf',
    alias: 'sdxs.gguf',
    description: 'SDXS 512-0.9 (Q4_0) - Ultra-lightweight mobile-optimized 2-3 step model (~450MB)',
    size_mb: 450,
    default_steps: 2,
    default_cfg: 2.0
  },
  turbo: {
    repo_id: 'second-state/SD-Turbo-GGUF',
    filename: 'sd-turbo-Q4_0.gguf',
    alias: 'turbo.gguf',
    description: 'SD Turbo (Q4_0) - Real-time 1-step inference model',
    size_mb: 1200,
    default_steps: 1,
    default_cfg: 1.5
  },
  anime: {
    repo_id: 'second-state/DreamShaper-8-GGUF',
    filename: 'dreamshaper-8-Q4_k.gguf',
    alias: 'anime.gguf',
    description: 'DreamShaper 8 (Q4_K) - Stylized anime & 2.5D illustration art',
    size_mb: 1650,
    default_steps: 10,
    default_cfg: 4.5
  }
};

const customRegistry = {};
let activeCacheDir = null;

// GGUF Magic Header
const GGUF_MAGIC = Buffer.from('GGUF');

function isAndroidTermux() {
  if (process.env.TERMUX_VERSION || process.env.TERMUX_APP_PID) return true;
  if (fs.existsSync('/data/data/com.termux')) return true;
  if (fs.existsSync('/data/data/com.termux/files/usr/bin/pkg')) return true;
  return false;
}

function isArm64() {
  const arch = os.arch().toLowerCase();
  return arch === 'arm64' || arch === 'aarch64';
}

function validateGgufFile(filePath) {
  try {
    const resolved = path.resolve(filePath);
    if (!fs.existsSync(resolved)) return false;
    const stat = fs.statSync(resolved);
    if (stat.size < 8) return false;
    const fd = fs.openSync(resolved, 'r');
    const buf = Buffer.alloc(8);
    fs.readSync(fd, buf, 0, 8, 0);
    fs.closeSync(fd);
    if (!buf.subarray(0, 4).equals(GGUF_MAGIC)) return false;
    const version = buf.readUInt32LE(4);
    return version >= 1 && version <= 3;
  } catch (_) {
    return false;
  }
}

function isExecutable(filePath) {
  try {
    if (!fs.existsSync(filePath)) return false;
    if (process.platform === 'win32') return true;
    fs.accessSync(filePath, fs.constants.X_OK);
    return true;
  } catch (_) {
    return false;
  }
}

function atomicReplaceFileSync(sourcePath, destPath) {
  try {
    fs.renameSync(sourcePath, destPath);
  } catch (err) {
    if (err.code === 'EEXIST' || err.code === 'EPERM' || err.code === 'EBUSY') {
      try {
        if (fs.existsSync(destPath)) {
          fs.unlinkSync(destPath);
        }
      } catch (_) {}
      try {
        fs.renameSync(sourcePath, destPath);
        return;
      } catch (_) {}
    }
    // Fallback for cross-device or persistent permission locks (EXDEV / EACCES)
    fs.copyFileSync(sourcePath, destPath);
    try {
      fs.unlinkSync(sourcePath);
    } catch (_) {}
  }
}

// ------------------------------------------------------------------------------
// Hardware Detection Module (Node.js Parity for GPU, NPU, TPU, CPU)
// ------------------------------------------------------------------------------

const VULKAN_LIB_PATHS = [
  '/system/lib64/libvulkan.so',
  '/system/lib/libvulkan.so',
  '/vendor/lib64/libvulkan.so',
  '/vendor/lib/libvulkan.so'
];

const OPENCL_LIB_PATHS = [
  '/vendor/lib64/libOpenCL.so',
  '/system/lib64/libOpenCL.so',
  '/system/vendor/lib64/libOpenCL.so',
  '/vendor/lib/libOpenCL.so',
  '/system/lib/libOpenCL.so',
  '/vendor/lib64/egl/libGLES_mali.so',
  '/system/vendor/lib64/egl/libGLES_mali.so'
];

const NPU_DRIVER_SEARCH_PATHS = [
  '/vendor/lib64/libQnnHtp.so',
  '/vendor/lib64/libQnnHtpV75.so',
  '/vendor/lib64/libQnnHtpV73.so',
  '/vendor/lib64/libqnn-htp.so',
  '/vendor/lib64/libQnnSystem.so',
  '/vendor/dsp/cdsp/libqnn_htp.so',
  '/vendor/lib64/libenn_public_api.so',
  '/vendor/lib64/libeden_nn.so',
  '/vendor/lib64/libenn_engine.so',
  '/vendor/lib64/libedgetpu.so',
  '/vendor/lib64/libtflite_edgetpu.so',
  '/system/lib64/libneuralnetworks.so',
  '/apex/com.android.neuralnetworks/lib64/libneuralnetworks.so'
];

function probeFirstExistingLib(paths) {
  for (const p of paths) {
    if (fs.existsSync(p)) {
      try {
        if (fs.statSync(p).size >= 1024) return p;
      } catch (err) {
        if (err.code === 'EACCES' || err.code === 'EPERM') {
          console.warn(`[termux-diffusion] Notice: Library found at '${p}' but read access was denied (${err.code}).`);
        }
      }
    }
  }
  return null;
}

function readCpuinfoFeatures() {
  if (!fs.existsSync('/proc/cpuinfo')) return [];
  try {
    const text = fs.readFileSync('/proc/cpuinfo', 'utf-8');
    for (const line of text.split('\n')) {
      if (line.toLowerCase().startsWith('features')) {
        const parts = line.split(':');
        if (parts.length >= 2) {
          return parts[1].trim().split(/\s+/);
        }
      }
    }
  } catch (err) {
    // Debug logging for cpuinfo parsing failures
    if (process.env.DEBUG) {
      console.debug('[termux-diffusion] Note: Could not parse /proc/cpuinfo:', err.message);
    }
  }
  return [];
}

function getAndroidProp(key) {
  try {
    const res = spawnSync('getprop', [key], { encoding: 'utf-8', timeout: 2000 });
    if (res.status === 0 && res.stdout.trim() && res.stdout.trim() !== 'unknown') {
      return res.stdout.trim();
    }
  } catch (err) {
    if (process.env.DEBUG) {
      console.debug(`[termux-diffusion] getprop '${key}' note:`, err.message);
    }
  }
  return null;
}

function detectNpuCapabilities() {
  const socName = (
    getAndroidProp('ro.hardware.chipname') ||
    getAndroidProp('ro.board.platform') ||
    getAndroidProp('ro.hardware') ||
    getAndroidProp('ro.product.board') ||
    'unknown'
  ).toLowerCase();

  const brand = (
    getAndroidProp('ro.product.brand') ||
    getAndroidProp('ro.product.manufacturer') ||
    'unknown'
  ).toLowerCase();

  const driver = probeFirstExistingLib(NPU_DRIVER_SEARCH_PATHS);

  // 1. Qualcomm Snapdragon Hexagon NPU
  if (
    socName.includes('sm8') ||
    socName.includes('sm7') ||
    socName.includes('qcom') ||
    socName.includes('snapdragon') ||
    (driver && driver.toLowerCase().includes('qnn'))
  ) {
    const is8Gen3 = socName.includes('sm8650');
    const is8Gen2 = socName.includes('sm8550');
    const is8Gen1 = socName.includes('sm8450') || socName.includes('sm8475');

    const tops = is8Gen3 ? 45.0 : is8Gen2 ? 34.0 : is8Gen1 ? 27.0 : 15.0;
    const arch = is8Gen3 ? 'Hexagon v75' : is8Gen2 ? 'Hexagon v73' : 'Hexagon v69';

    const hasDriver = driver !== null;
    return {
      available: hasDriver,
      vendor: 'Qualcomm',
      dspArchitecture: arch,
      topsRating: hasDriver ? tops : 0.0,
      supportedPrecisions: hasDriver ? ['INT8', 'INT16', 'FP16'] : [],
      driverLibrary: driver,
      recommendedDelegate: hasDriver ? 'qnn_htp' : null
    };
  }

  // 2. Samsung Exynos NPU
  if (
    socName.includes('s5e') ||
    socName.includes('exynos') ||
    brand.includes('samsung') ||
    (driver && driver.toLowerCase().includes('eden'))
  ) {
    const is2400 = socName.includes('9945') || socName.includes('s5e9945');
    const is2200 = socName.includes('9925') || socName.includes('s5e9925');
    const is1380 = socName.includes('8835') || socName.includes('s5e8835');

    const tops = is2400 ? 44.0 : is2200 ? 25.0 : is1380 ? 4.9 : 10.0;
    const arch = is2400 ? 'Samsung NPU v4' : is2200 ? 'Samsung NPU v3' : 'Samsung NPU Lite';

    const hasDriver = driver !== null;
    return {
      available: hasDriver,
      vendor: 'Samsung',
      dspArchitecture: arch,
      topsRating: hasDriver ? tops : 0.0,
      supportedPrecisions: hasDriver ? ['INT8', 'FP16'] : [],
      driverLibrary: driver,
      recommendedDelegate: hasDriver ? 'samsung_eden' : null
    };
  }

  // 3. Google Tensor TPU
  if (
    socName.includes('tensor') ||
    socName.includes('gs101') ||
    socName.includes('gs201') ||
    socName.includes('zuma') ||
    brand.includes('google')
  ) {
    const isG3 = socName.includes('zuma');
    const isG2 = socName.includes('gs201');

    const hasDriver = driver !== null;
    return {
      available: hasDriver,
      vendor: 'Google',
      dspArchitecture: isG3 ? 'EdgeTPU v3' : isG2 ? 'EdgeTPU v2' : 'EdgeTPU v1',
      topsRating: hasDriver ? (isG3 ? 35.0 : 20.0) : 0.0,
      supportedPrecisions: hasDriver ? ['INT8', 'INT16'] : [],
      driverLibrary: driver,
      recommendedDelegate: hasDriver ? 'google_edgetpu' : null
    };
  }

  // 4. Generic NNAPI
  if (driver && driver.includes('neuralnetworks')) {
    return {
      available: true,
      vendor: 'Generic',
      dspArchitecture: 'Android NNAPI HAL',
      topsRating: 5.0,
      supportedPrecisions: ['INT8', 'FP16'],
      driverLibrary: driver,
      recommendedDelegate: 'android_nnapi'
    };
  }

  return {
    available: false,
    vendor: 'Unknown',
    dspArchitecture: 'None',
    topsRating: 0.0,
    supportedPrecisions: [],
    driverLibrary: null,
    recommendedDelegate: 'cpu'
  };
}

function detectHardwareProfile() {
  const isTermux = isAndroidTermux();
  const cpuFeatures = readCpuinfoFeatures();
  const cpuCores = os.cpus().length || 1;
  const cpuArch = os.arch().toLowerCase();

  const hasDotprod = cpuFeatures.includes('asimddp');
  const hasFp16 = cpuFeatures.includes('fphp') || cpuFeatures.includes('asimdhp');
  const hasI8mm = cpuFeatures.includes('i8mm');
  const hasSve = cpuFeatures.includes('sve') || cpuFeatures.includes('sve2');

  const socName = (
    getAndroidProp('ro.hardware.chipname') ||
    getAndroidProp('ro.board.platform') ||
    getAndroidProp('ro.hardware') ||
    getAndroidProp('ro.product.board') ||
    'Unknown'
  );

  const gpuName = (
    getAndroidProp('ro.hardware.egl') ||
    getAndroidProp('ro.hardware.vulkan') ||
    'Unknown'
  );

  // Probe Vulkan
  let vulkanAvailable = false;
  let vulkanLibPath = null;
  for (const p of VULKAN_LIB_PATHS) {
    if (fs.existsSync(p)) {
      try {
        const sz = fs.statSync(p).size;
        if (sz >= 1024) {
          vulkanAvailable = true;
          vulkanLibPath = p;
          break;
        }
      } catch (err) {
        if (err.code === 'EACCES' || err.code === 'EPERM') {
          console.warn(`[termux-diffusion] Notice: Vulkan library found at '${p}' but read access was denied (${err.code}).`);
        }
      }
    }
  }

  // Probe OpenCL
  let openclAvailable = false;
  let openclLibPath = null;
  for (const p of OPENCL_LIB_PATHS) {
    if (fs.existsSync(p)) {
      try {
        const sz = fs.statSync(p).size;
        if (sz >= 1024) {
          openclAvailable = true;
          openclLibPath = p;
          break;
        }
      } catch (err) {
        if (err.code === 'EACCES' || err.code === 'EPERM') {
          console.warn(`[termux-diffusion] Notice: OpenCL library found at '${p}' but read access was denied (${err.code}).`);
        }
      }
    }
  }

  const npuProfile = detectNpuCapabilities();

  let recommendedBackend = 'cpu';
  let recommendedNgl = 0;

  if (vulkanAvailable) {
    recommendedBackend = 'vulkan';
    recommendedNgl = 99;
  } else if (openclAvailable) {
    recommendedBackend = 'opencl';
    recommendedNgl = 32;
  }

  const prefix = process.env.PREFIX || '/data/data/com.termux/files/usr';
  const cmakeExtraFlags = [];
  if (vulkanAvailable && vulkanLibPath) {
    cmakeExtraFlags.push('-DSD_VULKAN=ON');
    cmakeExtraFlags.push(`-DVulkan_LIBRARY=${vulkanLibPath}`);
    cmakeExtraFlags.push(`-DVulkan_INCLUDE_DIR=${prefix}/include`);
    cmakeExtraFlags.push('-DCMAKE_EXE_LINKER_FLAGS=-L/system/lib64 -Wl,-rpath,/system/lib64 -L/vendor/lib64 -Wl,-rpath,/vendor/lib64');
  } else if (openclAvailable && openclLibPath) {
    cmakeExtraFlags.push('-DSD_OPENCL=ON');
    cmakeExtraFlags.push(`-DOpenCL_LIBRARY=${openclLibPath}`);
    cmakeExtraFlags.push(`-DOpenCL_INCLUDE_DIR=${prefix}/include`);
    cmakeExtraFlags.push('-DCMAKE_EXE_LINKER_FLAGS=-L/vendor/lib64 -Wl,-rpath,/vendor/lib64 -L/system/lib64 -Wl,-rpath,/system/lib64');
  }

  const marchParts = ['armv8-a'];
  if (cpuArch === 'arm64' || cpuArch === 'aarch64') {
    marchParts[0] = 'armv8.2-a';
    if (hasDotprod) marchParts.push('dotprod');
    if (hasFp16) marchParts.push('fp16');
    if (hasI8mm) marchParts.push('i8mm');
  }

  if (marchParts.length > 1) {
    const marchStr = marchParts.join('+');
    cmakeExtraFlags.push(`-DCMAKE_C_FLAGS=-O3 -march=${marchStr} -D_GNU_SOURCE`);
    cmakeExtraFlags.push(`-DCMAKE_CXX_FLAGS=-O3 -march=${marchStr} -D_GNU_SOURCE`);
  } else {
    cmakeExtraFlags.push('-DCMAKE_C_FLAGS=-O3 -D_GNU_SOURCE');
    cmakeExtraFlags.push('-DCMAKE_CXX_FLAGS=-O3 -D_GNU_SOURCE');
  }

  return {
    cpuArch,
    cpuCores,
    hasDotprod,
    hasFp16,
    hasI8mm,
    hasSve,
    socName,
    gpuName,
    vulkanAvailable,
    vulkanLibPath,
    openclAvailable,
    openclLibPath,
    npuProfile,
    recommendedBackend,
    recommendedNgl,
    cmakeExtraFlags
  };
}

function resolveDeviceBackend(requestedDevice) {
  const profile = detectHardwareProfile();
  const req = (requestedDevice || 'cpu').toLowerCase().trim();

  if (req === 'auto') {
    return { effectiveDevice: profile.recommendedBackend, nglLayers: profile.recommendedNgl };
  }

  if (req === 'npu' || req === 'tpu') {
    const npuDesc = (profile.npuProfile && profile.npuProfile.available)
      ? `${profile.npuProfile.chipsetName} / ${profile.npuProfile.dspArchitecture}`
      : 'Hardware not detected';
    throw new Error(
      `[termux-diffusion] Native NPU/TPU acceleration (${npuDesc}) requires Qualcomm QNN / LiteRT C++ Graph Runtime (scheduled for v2.0 roadmap). ` +
      `Currently, full hardware acceleration is supported via Vulkan GPU (device='vulkan') and ARM NEON (device='cpu'). ` +
      `Please use device='vulkan' or device='auto'.`
    );
  }

  if (req === 'vulkan' || req === 'gpu') {
    if (profile.vulkanAvailable) {
      return { effectiveDevice: 'vulkan', nglLayers: 99 };
    }
    throw new Error(
      "[termux-diffusion] Vulkan GPU acceleration was explicitly requested (device='vulkan'), " +
      "but no accessible Vulkan driver (.so) was found on this system. " +
      "To allow automatic CPU fallback when GPU is missing, use device='auto'."
    );
  }

  if (req === 'opencl') {
    if (profile.openclAvailable) {
      return { effectiveDevice: 'opencl', nglLayers: 32 };
    }
    throw new Error(
      "[termux-diffusion] OpenCL acceleration was explicitly requested (device='opencl'), " +
      "but no accessible OpenCL driver (.so) was found on this system. " +
      "To allow automatic CPU fallback when OpenCL is missing, use device='auto'."
    );
  }

  if (req === 'cpu') {
    return { effectiveDevice: 'cpu', nglLayers: 0 };
  }

  throw new Error(`[termux-diffusion] Unknown computing device '${requestedDevice}'. Supported: 'auto', 'cpu', 'vulkan', 'opencl'.`);
}

function getSdCliGpuArgs(device, ngl) {
  if ((device === 'vulkan' || device === 'opencl' || device === 'gpu' || device === 'npu' || device === 'tpu') && ngl > 0) {
    return ['-ngl', String(ngl)];
  }
  return [];
}

// ------------------------------------------------------------------------------
// Memory & Optimal Thread Count
// ------------------------------------------------------------------------------

function getMemoryInfo() {
  const metrics = {
    mem_total_mb: 0,
    mem_available_mb: 0,
    swap_total_mb: 0,
    swap_free_mb: 0,
    effective_total_mb: 0,
    effective_available_mb: 0
  };

  if (fs.existsSync('/proc/meminfo')) {
    try {
      const text = fs.readFileSync('/proc/meminfo', 'utf-8');
      for (const line of text.split('\n')) {
        const parts = line.split(':');
        if (parts.length === 2) {
          const k = parts[0].trim();
          const v = parseInt(parts[1].trim().split(/\s+/)[0], 10);
          if (!isNaN(v)) {
            const mb = Math.floor(v / 1024);
            if (k === 'MemTotal') metrics.mem_total_mb = mb;
            else if (k === 'MemAvailable') metrics.mem_available_mb = mb;
            else if (k === 'SwapTotal') metrics.swap_total_mb = mb;
            else if (k === 'SwapFree') metrics.swap_free_mb = mb;
          }
        }
      }
      metrics.effective_total_mb = metrics.mem_total_mb + metrics.swap_total_mb;
      metrics.effective_available_mb = metrics.mem_available_mb + metrics.swap_free_mb;
      return metrics;
    } catch (err) {
      if (process.env.DEBUG) {
        console.debug('[termux-diffusion] /proc/meminfo parse note:', err.message);
      }
    }
  }

  const total = Math.floor(os.totalmem() / (1024 * 1024));
  const free = Math.floor(os.freemem() / (1024 * 1024));
  metrics.mem_total_mb = total;
  metrics.mem_available_mb = free;
  metrics.effective_total_mb = total;
  metrics.effective_available_mb = free;
  return metrics;
}

function checkMemorySafety(requiredMb = 1500) {
  const mem = getMemoryInfo();
  const avail = mem.effective_available_mb;
  if (mem.effective_total_mb === 0) {
    return { safe: true, message: 'Memory inspection bypassed on host OS.' };
  }
  if (avail < requiredMb) {
    return {
      safe: false,
      message: `Available memory (${avail} MB) is below threshold (${requiredMb} MB). Please enable Samsung RAM Plus.`
    };
  }
  return { safe: true, message: `Memory check passed: ${avail} MB available.` };
}

function getOptimalThreadCount() {
  const totalCores = os.cpus().length || 4;
  if (isArm64()) {
    if (totalCores >= 8) return 4;
    if (totalCores >= 6) return 4;
    if (totalCores >= 4) return 4;
    return Math.max(1, totalCores);
  }
  return Math.max(1, Math.min(8, totalCores > 4 ? Math.floor(totalCores / 2) : totalCores));
}

// ------------------------------------------------------------------------------
// Cache and Hub
// ------------------------------------------------------------------------------

function getCacheDir() {
  if (activeCacheDir) return activeCacheDir;
  const envCache = process.env.TERMUX_DIFFUSION_CACHE;
  const base = envCache ? path.resolve(envCache) : path.join(os.homedir(), '.cache', 'termux-diffusion');
  const modelsDir = path.join(base, 'models');
  if (!fs.existsSync(modelsDir)) {
    fs.mkdirSync(modelsDir, { recursive: true });
  }
  return modelsDir;
}

function setCacheDir(customPath) {
  const resolved = path.resolve(customPath);
  if (!fs.existsSync(resolved)) {
    fs.mkdirSync(resolved, { recursive: true });
  }
  activeCacheDir = resolved;
  return activeCacheDir;
}

function registerModel(name, options) {
  customRegistry[name] = {
    repo_id: options.repo_id || options.repoId,
    filename: options.filename,
    alias: options.alias || `${name}.gguf`,
    description: options.description || `Custom model ${name}`,
    default_steps: options.steps || options.default_steps || 10,
    default_cfg: options.cfg || options.default_cfg || 4.0,
    sha256: options.sha256 || null
  };
}

function listPresets() {
  return Object.assign({}, DEFAULT_PRESETS, customRegistry);
}

function isModelCached(modelNameOrPath, cacheDir) {
  const targetDir = cacheDir ? path.resolve(cacheDir) : getCacheDir();
  if (fs.existsSync(path.resolve(modelNameOrPath))) return true;
  if (fs.existsSync(path.join(targetDir, modelNameOrPath))) return true;

  const presets = listPresets();
  if (presets[modelNameOrPath]) {
    const alias = presets[modelNameOrPath].alias;
    if (fs.existsSync(path.join(targetDir, alias))) return true;
  }
  return false;
}

function listCachedModels(cacheDir) {
  const targetDir = cacheDir ? path.resolve(cacheDir) : getCacheDir();
  if (!fs.existsSync(targetDir)) return [];
  const files = fs.readdirSync(targetDir);
  const results = [];
  for (const f of files) {
    if (f.endsWith('.gguf')) {
      const fullPath = path.join(targetDir, f);
      const stat = fs.statSync(fullPath);
      results.push({
        name: f,
        path: fullPath,
        size_mb: Math.round((stat.size / (1024 * 1024)) * 100) / 100,
        mtime: stat.mtime,
        is_valid_gguf: validateGgufFile(fullPath)
      });
    }
  }
  return results;
}

function clearCache(cacheDir, modelName) {
  const targetDir = cacheDir ? path.resolve(cacheDir) : getCacheDir();
  if (!fs.existsSync(targetDir)) return 0;
  let count = 0;
  if (modelName) {
    const fname = modelName.endsWith('.gguf') ? modelName : `${modelName}.gguf`;
    const full = path.join(targetDir, fname);
    if (fs.existsSync(full)) {
      fs.unlinkSync(full);
      count++;
    }
  } else {
    for (const f of fs.readdirSync(targetDir)) {
      if (f.endsWith('.gguf')) {
        fs.unlinkSync(path.join(targetDir, f));
        count++;
      }
    }
  }
  return count;
}

// ------------------------------------------------------------------------------
// Download Manager with HTTP Range Resumable Transfers
// ------------------------------------------------------------------------------

async function downloadModel(modelNameOrUrl, options = {}) {
  if (typeof modelNameOrUrl === 'string' && fs.existsSync(modelNameOrUrl)) {
    return path.resolve(modelNameOrUrl);
  }

  const targetDir = options.cacheDir ? path.resolve(options.cacheDir) : getCacheDir();
  if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });

  const presets = listPresets();
  let downloadUrl, targetFilename;

  if (presets[modelNameOrUrl]) {
    const info = presets[modelNameOrUrl];
    targetFilename = info.alias || info.filename;
    downloadUrl = `https://huggingface.co/${info.repo_id}/resolve/main/${info.filename}`;
  } else if (modelNameOrUrl.startsWith('http://') || modelNameOrUrl.startsWith('https://')) {
    downloadUrl = modelNameOrUrl;
    targetFilename = modelNameOrUrl.split('?')[0].replace(/\/+$/, '').split('/').pop();
    if (!targetFilename.endsWith('.gguf')) targetFilename += '.gguf';
  } else if (modelNameOrUrl.includes('/')) {
    const parts = modelNameOrUrl.split('/');
    if (parts.length === 3) {
      targetFilename = parts[2];
      downloadUrl = `https://huggingface.co/${parts[0]}/${parts[1]}/resolve/main/${parts[2]}`;
    } else {
      throw new Error(`Custom model reference should be 'org/repo/file.gguf' or a direct URL.`);
    }
  } else {
    throw new Error(`Unknown model preset: '${modelNameOrUrl}'. Available: ${Object.keys(presets).join(', ')}`);
  }

  const finalPath = path.join(targetDir, targetFilename);
  if (fs.existsSync(finalPath) && !options.force) {
    return finalPath;
  }

  const tempPath = path.join(targetDir, `${targetFilename}.${process.pid}.part`);
  console.log(`[Download] [termux-diffusion] Downloading model '${targetFilename}' (${downloadUrl})...`);

  let redirectCount = 0;
  await new Promise((resolve, reject) => {
    function fetchUrl(currentUrl) {
      if (++redirectCount > 10) {
        return reject(new Error(`Too many HTTP redirects (exceeded limit of 10) while downloading: ${downloadUrl}`));
      }
      const headers = { 'User-Agent': 'termux-diffusion-node/1.1.0' };
      let existingBytes = 0;

      if (fs.existsSync(tempPath)) {
        try {
          existingBytes = fs.statSync(tempPath).size;
          if (existingBytes > 0) {
            headers['Range'] = `bytes=${existingBytes}-`;
          }
        } catch (err) {
          if (process.env.DEBUG) {
            console.debug('[termux-diffusion] statSync tempPath note:', err.message);
          }
        }
      }

      const req = https.get(currentUrl, { headers }, (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          return fetchUrl(res.headers.location);
        }
        if (res.statusCode === 416) {
          if (fs.existsSync(tempPath)) {
            try {
              fs.unlinkSync(tempPath);
            } catch (err) {
              console.warn('[termux-diffusion] Notice: Failed removing invalid partial download file:', err.message);
            }
          }
          return fetchUrl(currentUrl);
        }
        if ((res.statusCode === 429 || res.statusCode === 503)) {
          console.warn(`[termux-diffusion] Notice: HTTP ${res.statusCode} Rate limited. Retrying in 2.0s...`);
          setTimeout(() => fetchUrl(currentUrl), 2000);
          return;
        }
        if (res.statusCode !== 200 && res.statusCode !== 206) {
          return reject(new Error(`Failed with HTTP ${res.statusCode} from ${currentUrl}`));
        }

        const isResumed = res.statusCode === 206;
        const totalContent = parseInt(res.headers['content-length'] || '0', 10);
        const totalBytes = isResumed ? existingBytes + totalContent : totalContent;
        let downloadedBytes = isResumed ? existingBytes : 0;
        const fileStream = fs.createWriteStream(tempPath, { flags: isResumed ? 'a' : 'w' });

        fileStream.on('error', (err) => {
          res.destroy();
          reject(err);
        });

        res.on('data', (chunk) => {
          downloadedBytes += chunk.length;
          const ok = fileStream.write(chunk);
          if (!ok) {
            res.pause();
            fileStream.once('drain', () => res.resume());
          }
          if (totalBytes > 0) {
            const pct = ((downloadedBytes / totalBytes) * 100).toFixed(1);
            const mbDone = (downloadedBytes / (1024 * 1024)).toFixed(1);
            const mbTotal = (totalBytes / (1024 * 1024)).toFixed(1);
            process.stdout.write(`  [Progress] Progress: ${mbDone}MB / ${mbTotal}MB (${pct}%) [Resumed: ${isResumed ? 'Y' : 'N'}]\r`);
          }
        });

        res.on('end', () => {
          fileStream.end(() => {
            process.stdout.write('\n');
            atomicReplaceFileSync(tempPath, finalPath);
            console.log(`[OK] [termux-diffusion] Model downloaded & cached at: ${finalPath}`);
            resolve(finalPath);
          });
        });

        res.on('error', (err) => {
          fileStream.destroy();
          reject(err);
        });
      });

      req.on('error', reject);
    }

    fetchUrl(downloadUrl);
  });

  return finalPath;
}

async function resolveModelPath(modelNameOrPath, cacheDir) {
  const targetDir = cacheDir ? path.resolve(cacheDir) : getCacheDir();
  if (fs.existsSync(path.resolve(modelNameOrPath))) return path.resolve(modelNameOrPath);
  if (fs.existsSync(path.join(targetDir, modelNameOrPath))) return path.join(targetDir, modelNameOrPath);

  const presets = listPresets();
  if (presets[modelNameOrPath]) {
    const alias = presets[modelNameOrPath].alias;
    const aliasPath = path.join(targetDir, alias);
    if (fs.existsSync(aliasPath)) return aliasPath;
    return await downloadModel(modelNameOrPath, { cacheDir: targetDir });
  }

  if (modelNameOrPath.startsWith('http://') || modelNameOrPath.startsWith('https://') || modelNameOrPath.includes('/')) {
    return await downloadModel(modelNameOrPath, { cacheDir: targetDir });
  }

  throw new Error(`Could not resolve model '${modelNameOrPath}'`);
}

function locateSdCli() {
  const binDir = path.join(os.homedir(), '.cache', 'termux-diffusion', 'bin');
  const candidates = ['sd-cli', 'sd-cli.exe', 'sd', 'sd.exe'];

  for (const name of candidates) {
    const p = path.join(binDir, name);
    if (isExecutable(p)) return p;
  }

  const prefixBin = '/data/data/com.termux/files/usr/bin/sd-cli';
  if (isExecutable(prefixBin)) return prefixBin;

  for (const name of ['sd-cli', 'sd-cli.exe']) {
    const localBin = path.join(os.homedir(), '.local', 'bin', name);
    if (isExecutable(localBin)) return localBin;
  }

  const whichCmd = process.platform === 'win32' ? 'where' : 'which';
  for (const name of ['sd-cli', 'sd']) {
    const whichRes = spawnSync(whichCmd, [name], { encoding: 'utf-8' });
    if (whichRes.status === 0 && whichRes.stdout.trim()) {
      const found = whichRes.stdout.trim().split('\r\n')[0].split('\n')[0];
      if (isExecutable(found)) return found;
    }
  }
  return null;
}

function getGalaxyGalleryDir() {
  const p1 = path.join(os.homedir(), 'storage', 'pictures', 'TermuxDiffusion');
  if (fs.existsSync(path.dirname(p1))) {
    if (!fs.existsSync(p1)) fs.mkdirSync(p1, { recursive: true });
    return p1;
  }
  const fallback = path.join(getCacheDir(), 'outputs');
  if (!fs.existsSync(fallback)) fs.mkdirSync(fallback, { recursive: true });
  return fallback;
}

function exportToAndroidGallery(sourcePath, destinationName) {
  const destDir = getGalaxyGalleryDir();
  const destName = destinationName || path.basename(sourcePath);
  const destPath = path.join(destDir, destName);
  fs.copyFileSync(sourcePath, destPath);

  if (isAndroidTermux()) {
    try {
      spawnSync('am', ['broadcast', '-a', 'android.intent.action.MEDIA_SCANNER_SCAN_FILE', '-d', `file://${destPath}`], { timeout: 3000 });
    } catch (e) {
      console.warn('[termux-diffusion] Media scanner intent warning:', e.message);
    }
  }
  return destPath;
}

function provisionEngine(force = false) {
  const existing = locateSdCli();
  if (existing && !force) return existing;

  console.log('[Start] [termux-diffusion] Running automated provisioner for native Bionic C++ engine...');
  const isTermux = isAndroidTermux();
  if (isTermux) {
    console.log('[Package] Checking required packages via pkg (clang, cmake, git, termux-api)...');
    try {
      spawnSync('pkg', ['install', '-y', 'clang', 'cmake', 'git', 'termux-api', 'wget'], { stdio: 'inherit' });
    } catch (e) {
      console.warn('[termux-diffusion] pkg install warning:', e.message);
    }
  }

  const buildRoot = path.join(os.homedir(), '.cache', 'termux-diffusion', 'build_src');
  if (!fs.existsSync(buildRoot)) fs.mkdirSync(buildRoot, { recursive: true });
  const repoDir = path.join(buildRoot, 'stable-diffusion.cpp');

  if (!fs.existsSync(repoDir)) {
    console.log('[Download] Cloning stable-diffusion.cpp repository...');
    spawnSync('git', ['clone', 'https://github.com/leejet/stable-diffusion.cpp', repoDir], { stdio: 'inherit' });
  }

  console.log('[Submodule] Synchronizing submodules (ggml)...');
  spawnSync('git', ['submodule', 'update', '--init', '--recursive'], { cwd: repoDir, stdio: 'inherit' });

  const buildDir = path.join(repoDir, 'build');
  if (!fs.existsSync(buildDir)) fs.mkdirSync(buildDir, { recursive: true });

  const hw = detectHardwareProfile();
  console.log(`[Config] Configuring CMake build for SoC: ${hw.socName}, GPU: ${hw.gpuName}, Backend: ${hw.recommendedBackend}...`);

  const cmakeArgs = [
    '..',
    '-DCMAKE_BUILD_TYPE=Release',
    '-DSD_BUILD_EXAMPLES=ON',
    '-DGGML_OPENMP=OFF',
    ...hw.cmakeExtraFlags
  ];

  spawnSync('cmake', cmakeArgs, { cwd: buildDir, stdio: 'inherit' });

  const memInfo = getMemoryInfo();
  const cpus = (os.cpus() && os.cpus().length) || 2;
  const makeJobs = memInfo.totalMb < 4096 ? 1 : (memInfo.totalMb < 8192 ? Math.min(2, cpus) : Math.min(4, cpus));

  console.log(`[Build] Compiling native Bionic binary with clang (make -j${makeJobs})...`);
  spawnSync('make', [`-j${makeJobs}`], { cwd: buildDir, stdio: 'inherit' });

  const binDir = path.join(os.homedir(), '.cache', 'termux-diffusion', 'bin');
  if (!fs.existsSync(binDir)) fs.mkdirSync(binDir, { recursive: true });
  const compiled = path.join(buildDir, 'bin', 'sd-cli');
  const target = path.join(binDir, 'sd-cli');

  if (fs.existsSync(compiled)) {
    const tempTarget = path.join(binDir, `sd-cli.${process.pid}.part`);
    fs.copyFileSync(compiled, tempTarget);
    fs.chmodSync(tempTarget, 0o755);
    atomicReplaceFileSync(tempTarget, target);
    console.log(`[Done] [termux-diffusion] Engine provisioned successfully at: ${target}`);
    return target;
  }
  throw new Error('Could not find compiled sd-cli binary in build directory.');
}

const DEFAULT_QUALITY_GUARD_NEGATIVE_PROMPT = 'lowres, bad quality, blur, deformed, distorted, extra limbs, artifacts';
let activeDefaultNegativePrompt = null;

function getDefaultNegativePrompt() {
  return activeDefaultNegativePrompt;
}

function setDefaultNegativePrompt(prompt) {
  activeDefaultNegativePrompt = prompt && prompt.trim() ? prompt.trim() : null;
}

function getQualityGuardNegativePrompt() {
  return DEFAULT_QUALITY_GUARD_NEGATIVE_PROMPT;
}

async function generate(options) {
  if (typeof options === 'string') {
    options = { prompt: options };
  }
  if (!options || !options.prompt || !String(options.prompt).replace(/\x00/g, '').trim()) {
    throw new Error('Prompt is required and cannot be empty.');
  }

  if (options.signal && options.signal.aborted) {
    throw new Error('Inference aborted by signal');
  }

  const prompt = options.prompt;
  const sanitizedPrompt = String(prompt).replace(/\x00/g, '').replace(/\r\n/g, ' ').replace(/\n/g, ' ').trim();
  const model = options.model || 'realistic';
  const rawDevice = options.device || 'cpu';
  const effectiveNegative = options.negativePrompt !== undefined
    ? options.negativePrompt
    : activeDefaultNegativePrompt;
  const width = options.width || 512;
  const height = options.height || 512;
  const seed = options.seed !== undefined ? options.seed : -1;
  const threads = options.threads || getOptimalThreadCount();
  const timeout = options.timeout || 1800000;
  const lowRamGuard = options.lowRamGuard !== false;

  // Pre-flight memory safety guard
  if (lowRamGuard) {
    const memCheck = checkMemorySafety(1200);
    if (!memCheck.safe) {
      console.warn(`[termux-diffusion] Low RAM Warning: ${memCheck.message}`);
    }
  }

  const { effectiveDevice, nglLayers } = resolveDeviceBackend(rawDevice);

  const presets = listPresets();
  const steps = options.steps || (presets[model] ? presets[model].default_steps : 10);
  // Locate or Auto-provision Native sd-cli Engine FIRST (before downloading 1.5GB model weights)
  let sdCli = locateSdCli();

  if (!sdCli) {
    if (options.autoProvision) {
      console.log('[Start] [termux-diffusion] sd-cli binary not found in standard paths. Attempting auto-provisioning as requested...');
      sdCli = provisionEngine();
    } else {
      throw new Error(
        "[termux-diffusion] Native 'sd-cli' binary not found on this system. " +
        "Please run 'npx termux-diffusion install' via CLI or pass '{ autoProvision: true }' to generate()."
      );
    }
  }

  const modelPath = await resolveModelPath(model);

  const timestamp = Math.floor(Date.now() / 1000);
  const outPath = options.output ? path.resolve(options.output) : path.join(getGalaxyGalleryDir(), `ai_gen_${timestamp}.png`);

  if (!fs.existsSync(path.dirname(outPath))) {
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
  }

  const cmdArgs = [
    '-m', modelPath,
    '-p', sanitizedPrompt,
    '-W', String(width),
    '-H', String(height),
    '-t', String(threads),
    '--steps', String(steps),
    '--cfg-scale', String(options.cfgScale || (presets[model] ? presets[model].default_cfg : 4.0)),
    '-o', outPath
  ];
  if (effectiveNegative) {
    const sanitizedNeg = String(effectiveNegative).replace(/\x00/g, '').replace(/\r\n/g, ' ').replace(/\n/g, ' ').trim();
    if (sanitizedNeg) cmdArgs.push('-n', sanitizedNeg);
  }
  if (seed >= 0) cmdArgs.push('-s', String(seed));

  const gpuArgs = getSdCliGpuArgs(effectiveDevice, nglLayers);
  cmdArgs.push(...gpuArgs);

  console.log(`[Render] [termux-diffusion] Rendering with '${model}' (${steps} steps, ${threads} threads, backend: ${effectiveDevice})...`);
  const startTime = Date.now();

  // Pre-flight memory safety check
  if (!options.force) {
    const memSafety = checkMemorySafety(1200);
    if (!memSafety.safe) {
      console.warn(`[termux-diffusion] Memory Warning: ${memSafety.message}`);
      if (options.strictMemory) {
        throw new Error(`Insufficient memory to safely run diffusion model: ${memSafety.message}`);
      }
    }
  }

  let wakeLockAcquired = false;
  if (isAndroidTermux()) {
    try {
      spawnSync('termux-wake-lock', [], { timeout: 1000 });
      wakeLockAcquired = true;
    } catch (e) {
      if (process.env.DEBUG) {
        console.debug('[termux-diffusion] WakeLock acquire note:', e.message);
      }
    }
  }

  function safeKillProcess(proc, timeoutMs = 2000) {
    if (!proc || proc.killed || proc.exitCode !== null) return;
    const pid = proc.pid;
    console.warn(`[termux-diffusion] Initiating child process termination (PID: ${pid})...`);

    try {
      // Step 1: Attempt graceful SIGTERM
      proc.kill('SIGTERM');

      // Step 2: Escalate to SIGKILL if still running
      const forceKillTimer = setTimeout(() => {
        if (proc.exitCode === null && !proc.killed) {
          console.warn(`[termux-diffusion] Child process (PID: ${pid}) did not exit within ${timeoutMs}ms, escalating to SIGKILL...`);
          try {
            proc.kill('SIGKILL');
          } catch (err) {
            console.error(`[termux-diffusion] Error sending SIGKILL to PID ${pid}:`, err.message);
          }
        }
      }, timeoutMs);

      if (forceKillTimer.unref) forceKillTimer.unref();
    } catch (err) {
      console.error(`[termux-diffusion] Error during child process termination (PID: ${pid}):`, err.message);
    }
  }

  try {
    await new Promise((resolve, reject) => {
      const proc = spawn(sdCli, cmdArgs, { stdio: ['ignore', 'pipe', 'pipe'] });
      let stderrBuffer = '';

      let onAbort = null;
      if (options.signal) {
        if (options.signal.aborted) {
          safeKillProcess(proc);
          return reject(new Error('Inference aborted by signal'));
        }
        onAbort = () => {
          safeKillProcess(proc);
          reject(new Error('Inference aborted by signal'));
        };
        options.signal.addEventListener('abort', onAbort, { once: true });
      }

      proc.stdout.on('data', (d) => {
        const str = d.toString();
        if (str.toLowerCase().includes('step') || str.includes('%')) {
          process.stdout.write(`  [Step] ${str.trim()}\n`);
        }
      });

      // Drain stderr stream continuously to prevent 64KB OS pipe buffer deadlock while capping memory buffer to 10KB
      proc.stderr.on('data', (d) => {
        const str = d.toString();
        stderrBuffer += str;
        if (stderrBuffer.length > 10240) {
          stderrBuffer = stderrBuffer.slice(-10240);
        }
        if (process.env.DEBUG) {
          process.stderr.write(str);
        }
      });

      // Cleanup child process on host process termination without calling process.exit()
      const onHostExit = () => {
        safeKillProcess(proc);
      };
      process.once('exit', onHostExit);

      const timer = setTimeout(() => {
        safeKillProcess(proc);
        reject(new Error(`Inference timed out after ${timeout}ms`));
      }, timeout);

      proc.on('close', (code) => {
        clearTimeout(timer);
        process.removeListener('exit', onHostExit);
        if (onAbort && options.signal) {
          options.signal.removeEventListener('abort', onAbort);
        }
        if (code === 0 && fs.existsSync(outPath)) {
          resolve();
        } else {
          const detail = stderrBuffer.trim() ? `\nDetails: ${stderrBuffer.trim().slice(-500)}` : '';
          reject(new Error(`Engine failed with exit code ${code}.${detail}`));
        }
      });

      proc.on('error', (err) => {
        clearTimeout(timer);
        process.removeListener('exit', onHostExit);
        if (onAbort && options.signal) {
          options.signal.removeEventListener('abort', onAbort);
        }
        reject(err);
      });
    });
  } finally {
    // Release WakeLock safely
    if (wakeLockAcquired && isAndroidTermux()) {
      try {
        spawnSync('termux-wake-unlock', [], { timeout: 1000 });
      } catch (e) {
        if (process.env.DEBUG) {
          console.debug('[termux-diffusion] WakeLock release note:', e.message);
        }
      }
    }
  }

  const elapsedSec = (Date.now() - startTime) / 1000;
  let galleryPath = null;
  if (options.exportGallery !== false) {
    try {
      galleryPath = exportToAndroidGallery(outPath);
    } catch (e) {
      console.warn('[termux-diffusion] Gallery export note:', e.message);
    }
  }

  console.log(`[Done] [termux-diffusion] Image generated in ${elapsedSec.toFixed(1)}s -> ${outPath}`);
  if (galleryPath) {
    console.log(`[Gallery] [Samsung Gallery] Synchronized to: ${galleryPath}`);
  }

  return {
    path: outPath,
    galleryPath: galleryPath,
    prompt: prompt,
    model: model,
    steps: steps,
    cfgScale: cfgScale,
    elapsedSec: elapsedSec
  };
}

module.exports = {
  generate,
  downloadModel,
  resolveModelPath,
  registerModel,
  setCacheDir,
  getCacheDir,
  isModelCached,
  listCachedModels,
  clearCache,
  listPresets,
  locateSdCli,
  exportToAndroidGallery,
  detectHardwareProfile,
  detectNpuCapabilities,
  resolveDeviceBackend,
  getSdCliGpuArgs,
  validateGgufFile,
  getMemoryInfo,
  checkMemorySafety,
  getOptimalThreadCount,
  getDefaultNegativePrompt,
  setDefaultNegativePrompt,
  getQualityGuardNegativePrompt,
  DEFAULT_PRESETS
};
