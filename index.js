/**
 * termux-diffusion: Production On-Device AI Image Generation for Android Termux & Samsung Galaxy
 * Dual-Engine (Node.js & TypeScript) Native Module
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn, spawnSync } = require('child_process');
const https = require('https');

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

function isAndroidTermux() {
  if (process.env.TERMUX_VERSION || process.env.TERMUX_APP_PID) return true;
  if (fs.existsSync('/data/data/com.termux')) return true;
  return false;
}

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
    default_cfg: options.cfg || options.default_cfg || 4.0
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
        mtime: stat.mtime
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

async function downloadModel(modelNameOrUrl, options = {}) {
  const targetDir = options.cacheDir ? path.resolve(options.cacheDir) : getCacheDir();
  if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });

  const presets = listPresets();
  let repoId, filename, targetFilename;

  if (presets[modelNameOrUrl]) {
    const info = presets[modelNameOrUrl];
    repoId = info.repo_id;
    filename = info.filename;
    targetFilename = info.alias || filename;
  } else {
    throw new Error(`Unknown model preset: '${modelNameOrUrl}'. Available: ${Object.keys(presets).join(', ')}`);
  }

  const finalPath = path.join(targetDir, targetFilename);
  if (fs.existsSync(finalPath) && !options.force) {
    return finalPath;
  }

  const downloadUrl = `https://huggingface.co/${repoId}/resolve/main/${filename}`;
  const tempPath = path.join(targetDir, `${targetFilename}.part`);

  console.log(`📥 [termux-diffusion] Downloading model '${modelNameOrUrl}' (${downloadUrl})...`);

  await new Promise((resolve, reject) => {
    function fetchUrl(currentUrl) {
      https.get(currentUrl, { headers: { 'User-Agent': 'termux-diffusion-node/1.0.0' } }, (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          return fetchUrl(res.headers.location);
        }
        if (res.statusCode !== 200) {
          return reject(new Error(`Failed with HTTP ${res.statusCode} from ${currentUrl}`));
        }

        const totalBytes = parseInt(res.headers['content-length'] || '0', 10);
        let downloadedBytes = 0;
        const fileStream = fs.createWriteStream(tempPath);

        res.on('data', (chunk) => {
          downloadedBytes += chunk.length;
          fileStream.write(chunk);
          if (totalBytes > 0) {
            const pct = ((downloadedBytes / totalBytes) * 100).toFixed(1);
            const mbDone = (downloadedBytes / (1024 * 1024)).toFixed(1);
            const mbTotal = (totalBytes / (1024 * 1024)).toFixed(1);
            process.stdout.write(`  ⏳ Progress: ${mbDone}MB / ${mbTotal}MB (${pct}%)\r`);
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
          if (fs.existsSync(tempPath)) fs.unlinkSync(tempPath);
          reject(err);
        });
      }).on('error', reject);
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

  throw new Error(`Could not resolve model '${modelNameOrPath}'`);
}

function locateSdCli() {
  const homeCacheBin = path.join(os.homedir(), '.cache', 'termux-diffusion', 'bin', 'sd-cli');
  if (fs.existsSync(homeCacheBin)) return homeCacheBin;

  const prefixBin = '/data/data/com.termux/files/usr/bin/sd-cli';
  if (fs.existsSync(prefixBin)) return prefixBin;

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
    } catch (_) {}
  }
  return destPath;
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
  const negativePrompt = options.negativePrompt || 'woman, girl, cartoon, anime, 3d render, plastic, illustration, b&w, lowres, blur, deformed hands, extra fingers, messy face, horror';
  const width = options.width || 512;
  const height = options.height || 512;
  const seed = options.seed !== undefined ? options.seed : -1;
  const threads = options.threads || 4;
  const timeout = options.timeout || 1800000;

  const presets = listPresets();
  const steps = options.steps || (presets[model] ? presets[model].default_steps : 10);
  const cfgScale = options.cfgScale || (presets[model] ? presets[model].default_cfg : 4.0);

  const modelPath = await resolveModelPath(model);
  const sdCli = locateSdCli();

  if (!sdCli) {
    throw new Error('sd-cli engine binary not found. Please run: npx termux-diffusion install');
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

  console.log(`🎨 [termux-diffusion] Rendering with '${model}' (${steps} steps, ${threads} threads)...`);
  const startTime = Date.now();

  // Acquire WakeLock
  if (isAndroidTermux()) {
    try { spawnSync('termux-wake-lock', [], { timeout: 2000 }); } catch (_) {}
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
        proc.kill('SIGKILL');
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
      try { spawnSync('termux-wake-unlock', [], { timeout: 2000 }); } catch (_) {}
    }
  }

  const elapsedSec = (Date.now() - startTime) / 1000;
  let galleryPath = null;
  if (options.exportGallery !== false) {
    try {
      galleryPath = exportToAndroidGallery(outPath);
    } catch (_) {}
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
  DEFAULT_PRESETS
};
