/**
 * termux-diffusion: Production On-Device AI Image Generation for Android Termux & Samsung Galaxy
 * Dual-Engine (Node.js & TypeScript) Native Module with Vulkan/OpenCL Hardware Acceleration
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
    description: 'Realistic Vision V6.0 B1 (Q4_K) — Ultra-detailed photorealistic portraits',
    size_mb: 1620,
    default_steps: 10,
    default_cfg: 4.0
  },
  speed: {
    repo_id: 'gpustack/stable-diffusion-v1-5-GGUF',
    filename: 'stable-diffusion-v1-5-Q4_1.gguf',
    alias: 'lightning.gguf',
    description: 'Stable Diffusion 1.5 (Q4_1) — Fast general-purpose base model',
    size_mb: 1590,
    default_steps: 10,
    default_cfg: 4.0
  },
  sdxs: {
    repo_id: 'gpustack/SDXS-512-0.9-GGUF',
    filename: 'sdxs-512-0.9-Q4_0.gguf',
    alias: 'sdxs.gguf',
    description: 'SDXS 512-0.9 (Q4_0) — Ultra-lightweight mobile-optimized 2-3 step model (~450MB)',
    size_mb: 450,
    default_steps: 2,
    default_cfg: 2.0
  },
  turbo: {
    repo_id: 'second-state/SD-Turbo-GGUF',
    filename: 'sd-turbo-Q4_0.gguf',
    alias: 'turbo.gguf',
    description: 'SD Turbo (Q4_0) — Real-time 1-step inference model',
    size_mb: 1200,
    default_steps: 1,
    default_cfg: 1.5
  },
  anime: {
    repo_id: 'second-state/DreamShaper-8-GGUF',
    filename: 'dreamshaper-8-Q4_k.gguf',
    alias: 'anime.gguf',
    description: 'DreamShaper 8 (Q4_K) — Stylized anime & 2.5D illustration art',
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
    if (stat.size < 4) return false;
    const fd = fs.openSync(resolved, 'r');
    const buf = Buffer.alloc(4);
    fs.readSync(fd, buf, 0, 4, 0);
    fs.closeSync(fd);
    return buf.equals(GGUF_MAGIC);
  } catch (_) {
    return false;
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// Hardware Detection Module (Node.js Parity)
// ──────────────────────────────────────────────────────────────────────────────

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
  '/system/lib/libOpenCL.so'
];

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
  } catch (_) {}
  return [];
}

function getAndroidProp(key) {
  try {
    const res = spawnSync('getprop', [key], { encoding: 'utf-8', timeout: 2000 });
    if (res.status === 0 && res.stdout.trim() && res.stdout.trim() !== 'unknown') {
      return res.stdout.trim();
    }
  } catch (_) {}
  return null;
}

function detectHardwareProfile() {
  const arch = os.arch().toLowerCase();
  const cores = os.cpus().length;
  const features = readCpuinfoFeatures();

  const hasDotprod = features.includes('asimddp');
  const hasFp16 = features.includes('fphp') || features.includes('asimdhp');
  const hasI8mm = features.includes('i8mm');
  const hasSve = features.includes('sve') || features.includes('sve2');

  const socName = getAndroidProp('ro.hardware.chipname') ||
                  getAndroidProp('ro.board.platform') ||
                  getAndroidProp('ro.hardware') ||
                  'Unknown';

  const gpuName = (getAndroidProp('ro.hardware.vulkan') || 'Unknown');

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
      } catch (_) {}
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
      } catch (_) {}
    }
  }

  let recommendedBackend = 'cpu';
  let recommendedNgl = 0;

  if (vulkanAvailable) {
    recommendedBackend = 'vulkan';
    recommendedNgl = 99;
  } else if (openclAvailable) {
    recommendedBackend = 'opencl';
    recommendedNgl = 32;
  }

  const cmakeExtraFlags = [];
  if (vulkanAvailable && vulkanLibPath) {
    cmakeExtraFlags.push('-DSD_VULKAN=ON');
    cmakeExtraFlags.push(`-DVULKAN_LIBRARY=${vulkanLibPath}`);
  }

  const marchParts = ['armv8-a'];
  if (arch === 'arm64' || arch === 'aarch64') {
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
    cpuArch: arch,
    cpuCores: cores,
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

  if (req === 'vulkan' || req === 'gpu') {
    if (profile.vulkanAvailable) {
      return { effectiveDevice: 'vulkan', nglLayers: 99 };
    }
    console.warn('[termux-diffusion] Vulkan GPU requested but driver not found. Falling back to CPU.');
    return { effectiveDevice: 'cpu', nglLayers: 0 };
  }

  if (req === 'opencl') {
    if (profile.openclAvailable) {
      return { effectiveDevice: 'opencl', nglLayers: 32 };
    }
    console.warn('[termux-diffusion] OpenCL requested but driver not found. Falling back to CPU.');
    return { effectiveDevice: 'cpu', nglLayers: 0 };
  }

  return { effectiveDevice: 'cpu', nglLayers: 0 };
}

function getSdCliGpuArgs(device, ngl) {
  if ((device === 'vulkan' || device === 'opencl' || device === 'gpu') && ngl > 0) {
    return ['-ngl', String(ngl)];
  }
  return [];
}

// ──────────────────────────────────────────────────────────────────────────────
// Memory & Optimal Thread Count
// ──────────────────────────────────────────────────────────────────────────────

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
    } catch (_) {}
  }

  // OS Fallback
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

// ──────────────────────────────────────────────────────────────────────────────
// Cache and Hub
// ──────────────────────────────────────────────────────────────────────────────

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

// ──────────────────────────────────────────────────────────────────────────────
// Download Manager with HTTP Range Resumable Transfers
// ──────────────────────────────────────────────────────────────────────────────

async function downloadModel(modelNameOrUrl, options = {}) {
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

  const tempPath = path.join(targetDir, `${targetFilename}.part`);
  console.log(`📥 [termux-diffusion] Downloading model '${targetFilename}' (${downloadUrl})...`);

  await new Promise((resolve, reject) => {
    function fetchUrl(currentUrl) {
      const headers = { 'User-Agent': 'termux-diffusion-node/1.1.0' };
      let existingBytes = 0;

      if (fs.existsSync(tempPath)) {
        try {
          existingBytes = fs.statSync(tempPath).size;
          if (existingBytes > 0) {
            headers['Range'] = `bytes=${existingBytes}-`;
          }
        } catch (_) {}
      }

      const req = https.get(currentUrl, { headers }, (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          return fetchUrl(res.headers.location);
        }
        if (res.statusCode === 416) {
          // Range Not Satisfiable: restart fresh
          if (fs.existsSync(tempPath)) fs.unlinkSync(tempPath);
          return fetchUrl(currentUrl);
        }
        if (res.statusCode !== 200 && res.statusCode !== 206) {
          return reject(new Error(`Failed with HTTP ${res.statusCode} from ${currentUrl}`));
        }

        const isResumed = res.statusCode === 206;
        const totalContent = parseInt(res.headers['content-length'] || '0', 10);
        const totalBytes = isResumed ? existingBytes + totalContent : totalContent;
        let downloadedBytes = isResumed ? existingBytes : 0;
        const fileStream = fs.createWriteStream(tempPath, { flags: isResumed ? 'a' : 'w' });

        res.on('data', (chunk) => {
          downloadedBytes += chunk.length;
          fileStream.write(chunk);
          if (totalBytes > 0) {
            const pct = ((downloadedBytes / totalBytes) * 100).toFixed(1);
            const mbDone = (downloadedBytes / (1024 * 1024)).toFixed(1);
            const mbTotal = (totalBytes / (1024 * 1024)).toFixed(1);
            process.stdout.write(`  ⏳ Progress: ${mbDone}MB / ${mbTotal}MB (${pct}%) [Resumed: ${isResumed ? 'Y' : 'N'}]\r`);
          }
        });

        res.on('end', () => {
          fileStream.end(() => {
            process.stdout.write('\n');
            fs.renameSync(tempPath, finalPath);
            console.log(`✅ [termux-diffusion] Model downloaded & cached at: ${finalPath}`);
            resolve(finalPath);
          });
        });

        res.on('error', (err) => {
          fileStream.close();
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
  const homeCacheBin = path.join(os.homedir(), '.cache', 'termux-diffusion', 'bin', 'sd-cli');
  if (fs.existsSync(homeCacheBin)) return homeCacheBin;

  const prefixBin = '/data/data/com.termux/files/usr/bin/sd-cli';
  if (fs.existsSync(prefixBin)) return prefixBin;

  const localBin = path.join(os.homedir(), '.local', 'bin', 'sd-cli');
  if (fs.existsSync(localBin)) return localBin;

  const whichRes = spawnSync('which', ['sd-cli'], { encoding: 'utf-8' });
  if (whichRes.status === 0 && whichRes.stdout.trim()) {
    return whichRes.stdout.trim();
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

  console.log('🚀 [termux-diffusion] Running automated provisioner for native Bionic C++ engine...');
  const isTermux = isAndroidTermux();
  if (isTermux) {
    console.log('📦 Checking required packages via pkg (clang, cmake, git, termux-api)...');
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
    console.log('📥 Cloning stable-diffusion.cpp repository...');
    spawnSync('git', ['clone', 'https://github.com/leejet/stable-diffusion.cpp', repoDir], { stdio: 'inherit' });
  }

  console.log('🔧 Synchronizing submodules (ggml)...');
  spawnSync('git', ['submodule', 'update', '--init', '--recursive'], { cwd: repoDir, stdio: 'inherit' });

  const buildDir = path.join(repoDir, 'build');
  if (!fs.existsSync(buildDir)) fs.mkdirSync(buildDir, { recursive: true });

  const hw = detectHardwareProfile();
  console.log(`⚙️ Configuring CMake build for SoC: ${hw.socName}, GPU: ${hw.gpuName}, Backend: ${hw.recommendedBackend}...`);

  const cmakeArgs = [
    '..',
    '-DCMAKE_BUILD_TYPE=Release',
    '-DSD_BUILD_EXAMPLES=ON',
    '-DGGML_OPENMP=OFF',
    ...hw.cmakeExtraFlags
  ];

  spawnSync('cmake', cmakeArgs, { cwd: buildDir, stdio: 'inherit' });

  console.log('🔨 Compiling native Bionic binary with clang (make -j4)...');
  spawnSync('make', ['-j4'], { cwd: buildDir, stdio: 'inherit' });

  const binDir = path.join(os.homedir(), '.cache', 'termux-diffusion', 'bin');
  if (!fs.existsSync(binDir)) fs.mkdirSync(binDir, { recursive: true });
  const compiled = path.join(buildDir, 'bin', 'sd-cli');
  const target = path.join(binDir, 'sd-cli');

  if (fs.existsSync(compiled)) {
    fs.copyFileSync(compiled, target);
    fs.chmodSync(target, 0o755);
    console.log(`✨ [termux-diffusion] Engine provisioned successfully at: ${target}`);
    return target;
  }
  throw new Error('Could not find compiled sd-cli binary in build directory.');
}

async function generate(options) {
  if (typeof options === 'string') {
    options = { prompt: options };
  }
  if (!options || !options.prompt) {
    throw new Error('Prompt is required for generation');
  }

  const prompt = options.prompt;
  const model = options.model || 'realistic';
  const rawDevice = options.device || 'cpu';
  const negativePrompt = options.negativePrompt || 'woman, girl, cartoon, anime, 3d render, plastic, illustration, b&w, lowres, blur, deformed hands, extra fingers, messy face, horror';
  const width = options.width || 512;
  const height = options.height || 512;
  const seed = options.seed !== undefined ? options.seed : -1;
  const threads = options.threads || getOptimalThreadCount();
  const timeout = options.timeout || 1800000;
  const lowRamGuard = options.lowRamGuard !== false;

  // Pre-flight memory safety guard
  if (lowRamGuard) {
    const memCheck = checkMemorySafety(1000);
    if (!memCheck.safe) {
      console.warn(`[termux-diffusion] Low RAM Warning: ${memCheck.message}`);
    }
  }

  const { effectiveDevice, nglLayers } = resolveDeviceBackend(rawDevice);

  const presets = listPresets();
  const steps = options.steps || (presets[model] ? presets[model].default_steps : 10);
  const cfgScale = options.cfgScale || (presets[model] ? presets[model].default_cfg : 4.0);

  const modelPath = await resolveModelPath(model);
  let sdCli = locateSdCli();

  if (!sdCli) {
    console.log('🚀 [termux-diffusion] sd-cli binary not found in standard paths. Attempting auto-provisioning...');
    sdCli = provisionEngine();
  }

  const timestamp = Math.floor(Date.now() / 1000);
  const outPath = options.output ? path.resolve(options.output) : path.join(getGalaxyGalleryDir(), `ai_gen_${timestamp}.png`);

  if (!fs.existsSync(path.dirname(outPath))) {
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
  }

  const cmdArgs = [
    '-m', modelPath,
    '-p', prompt,
    '-W', String(width),
    '-H', String(height),
    '-t', String(threads),
    '--steps', String(steps),
    '--cfg-scale', String(cfgScale),
    '-o', outPath
  ];
  if (negativePrompt) cmdArgs.push('-n', negativePrompt);
  if (seed >= 0) cmdArgs.push('-s', String(seed));

  const gpuArgs = getSdCliGpuArgs(effectiveDevice, nglLayers);
  cmdArgs.push(...gpuArgs);

  console.log(`🎨 [termux-diffusion] Rendering with '${model}' (${steps} steps, ${threads} threads, backend: ${effectiveDevice})...`);
  const startTime = Date.now();

  // Acquire WakeLock
  if (isAndroidTermux()) {
    try { spawnSync('termux-wake-lock', [], { timeout: 2000 }); } catch (e) {
      console.warn('[termux-diffusion] WakeLock acquire note:', e.message);
    }
  }

  try {
    await new Promise((resolve, reject) => {
      const proc = spawn(sdCli, cmdArgs, { stdio: ['ignore', 'pipe', 'pipe'] });
      proc.stdout.on('data', (d) => {
        const str = d.toString();
        if (str.toLowerCase().includes('step') || str.includes('%')) {
          process.stdout.write(`  ⚡ ${str.trim()}\n`);
        }
      });

      const timer = setTimeout(() => {
        try { proc.kill('SIGKILL'); } catch (_) {}
        reject(new Error(`Inference timed out after ${timeout}ms`));
      }, timeout);

      proc.on('close', (code) => {
        clearTimeout(timer);
        if (code === 0 && fs.existsSync(outPath)) {
          resolve();
        } else {
          reject(new Error(`Engine failed with exit code ${code}`));
        }
      });
      proc.on('error', (err) => {
        clearTimeout(timer);
        reject(err);
      });
    });
  } finally {
    // Release WakeLock
    if (isAndroidTermux()) {
      try { spawnSync('termux-wake-unlock', [], { timeout: 2000 }); } catch (e) {
        console.warn('[termux-diffusion] WakeLock release note:', e.message);
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

  console.log(`✨ [termux-diffusion] Image generated in ${elapsedSec.toFixed(1)}s -> ${outPath}`);
  if (galleryPath) {
    console.log(`📱 [Samsung Gallery] Synchronized to: ${galleryPath}`);
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
  resolveDeviceBackend,
  getSdCliGpuArgs,
  validateGgufFile,
  getMemoryInfo,
  checkMemorySafety,
  getOptimalThreadCount,
  DEFAULT_PRESETS
};
