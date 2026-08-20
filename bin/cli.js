#!/usr/bin/env node
/**
 * CLI Entry point for termux-diffusion on Node.js / npm
 */

'use strict';

const {
  generate,
  downloadModel,
  listPresets,
  listCachedModels,
  clearCache,
  locateSdCli,
  detectHardwareProfile,
  DEFAULT_PRESETS
} = require('../index');
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const args = process.argv.slice(2);
const command = args[0];

function printHelp() {
  console.log(`
[Render] termux-diffusion CLI (v1.0.0) - On-Device AI Image Generation for Samsung Galaxy & Termux

Usage:
  npx termux-diffusion <command> [options]

Commands:
  generate <prompt>   Generate AI image from prompt (e.g. npx termux-diffusion generate "happy cat")
  install             Provision and compile native Bionic C++ engine (sd-cli)
  doctor              Run 7-tier pre-flight diagnostic checks
  models              List available presets and locally cached GGUF models
  download <model>    Pre-download a model preset (realistic, speed, sdxs, turbo, anime)
  clear-cache         Delete cached models to reclaim storage space

Options:
  -m, --model <name>       Model preset name (default: realistic)
  -n, --negative <text>    Negative prompt
  -d, --device <dev>       Computing device (cpu, gpu, vulkan, opencl, auto)
  -s, --steps <num>        Denoising steps (default: 10)
  -c, --cfg <num>          CFG guidance scale (default: 4.0)
  -t, --threads <num>      CPU threads (default: auto-detected big cores)
  -o, --output <path>      Destination output filename
  --seed <num>             RNG seed (-1 for random)
  --sampler <name>         Sampling method (euler, euler_a, heun, dpm++2m, lcm)
  --schedule <name>        Noise schedule (default, discrete, karras, exponential, ays)
  --vae-tiling             Enable VAE tiling for ~70% lower peak memory
  -i, --init-img <path>    Source image for Img2Img synthesis
  --strength <num>         Img2Img strength (0.0 to 1.0, default: 0.75)
  --lora-dir <path>        Directory containing LoRA adapter weights
  --clip-skip <num>        CLIP layers to skip (1 or 2)
  --control-net <path>     Path to ControlNet model
  --control-image <path>   Path to ControlNet guide image
  --control-strength <num> ControlNet strength (0.0 to 2.0, default: 0.9)
  --taesd <path>           Path to Tiny AutoEncoder (TAESD) model
`);
}

function runInstall() {
  console.log('[Start] [termux-diffusion] Running automated provisioner for native Bionic C++ engine...');
  const isTermux = fs.existsSync('/data/data/com.termux');
  if (isTermux) {
    console.log('[Package] Checking required packages via pkg (clang, make, cmake, git, termux-api, vulkan-loader, opencl-headers)...');
    try {
      spawnSync('pkg', ['install', '-y', 'clang', 'make', 'cmake', 'git', 'termux-api', 'wget', 'vulkan-loader', 'vulkan-headers', 'vulkan-tools', 'opencl-headers'], { stdio: 'inherit' });
    } catch (_) {}
  }

  const binPath = provisionEngine(true);
  console.log(`\n[SUCCESS] Native Bionic C++ engine ready: ${binPath}`);
}

function runDoctor() {
  console.log('=================================================================');
  console.log('[Doctor] [termux-diffusion] Node.js Pre-flight Diagnostic Doctor');
  console.log('=================================================================');

  const isTermux = fs.existsSync('/data/data/com.termux');
  console.log(`1. Platform: ${isTermux ? 'Android Termux [OK]' : 'Non-Termux Host [INFO]'}`);
  console.log(`2. Architecture: ${process.arch} (${process.arch === 'arm64' ? 'ARM64 [OK]' : 'Non-ARM64 [INFO]'})`);

  const storageOk = fs.existsSync(path.join(os.homedir(), 'storage'));
  console.log(`3. Android Storage: ${storageOk ? 'Configured [OK]' : 'Missing [WARN] (Run termux-setup-storage)'}`);

  const sdCli = locateSdCli();
  console.log(`4. Native C++ Engine: ${sdCli ? `${sdCli} [OK]` : 'Not Found [FAIL] (Run npx termux-diffusion install)'}`);

  const hw = detectHardwareProfile();
  console.log(`6. Hardware Profile: SoC=${hw.socName}, GPU=${hw.gpuName}, Vulkan=${hw.vulkanAvailable ? 'Available [OK]' : 'Not Found [WARN]'}`);
  if (hw.npuProfile && hw.npuProfile.available) {
    console.log(`   -> NPU Hardware: Detected (${hw.npuProfile.dspArchitecture}, ${hw.npuProfile.topsRating} TOPS) [v2.0 QNN runtime pending]`);
  }
  console.log(`   -> Active Backend: ${hw.recommendedBackend.toUpperCase()} (Offload layers: ${hw.recommendedNgl})`);

  if (isTermux) {
    console.log('7. Android 12+ Background Stability Guard:');
    console.log('   -> Tip: If generation crashes when Termux is in background, enable');
    console.log('          "Developer Options > Disable child process restrictions"');
    console.log('          or run: adb shell "/system/bin/device_config put activity_manager max_phantom_processes 2147483647"');
  }

  console.log('=================================================================');
}

async function main() {
  if (!command || command === '--help' || command === '-h') {
    printHelp();
    return;
  }

  if (command === 'generate') {
    const prompt = args[1];
    if (!prompt) {
      console.error('[FAIL] Error: Prompt text is required (e.g. npx termux-diffusion generate "prompt")');
      process.exit(1);
    }
    let model = 'realistic';
    let steps, cfg, output, seed = -1, threads, device = 'cpu', negative;
    let sampler, schedule, vaeTiling = false, initImg, strength;
    let loraDir, clipSkip, controlNet, controlImage, controlStrength, taesd;

    for (let i = 2; i < args.length; i++) {
      if (args[i] === '-m' || args[i] === '--model') model = args[++i];
      if (args[i] === '-n' || args[i] === '--negative') negative = args[++i];
      if (args[i] === '-d' || args[i] === '--device') device = args[++i];
      if (args[i] === '-s' || args[i] === '--steps') steps = parseInt(args[++i], 10);
      if (args[i] === '-c' || args[i] === '--cfg') cfg = parseFloat(args[++i]);
      if (args[i] === '-t' || args[i] === '--threads') threads = parseInt(args[++i], 10);
      if (args[i] === '-o' || args[i] === '--output') output = args[++i];
      if (args[i] === '--sampler' || args[i] === '--sampling-method') sampler = args[++i];
      if (args[i] === '--schedule') schedule = args[++i];
      if (args[i] === '--vae-tiling') vaeTiling = true;
      if (args[i] === '-i' || args[i] === '--init-img') initImg = args[++i];
      if (args[i] === '--strength') strength = parseFloat(args[++i]);
      if (args[i] === '--lora-dir') loraDir = args[++i];
      if (args[i] === '--clip-skip') clipSkip = parseInt(args[++i], 10);
      if (args[i] === '--control-net') controlNet = args[++i];
      if (args[i] === '--control-image') controlImage = args[++i];
      if (args[i] === '--control-strength') controlStrength = parseFloat(args[++i]);
      if (args[i] === '--taesd') taesd = args[++i];
      if (args[i] === '--seed') {
        seed = parseInt(args[++i], 10);
        if (isNaN(seed) || seed < -1 || seed > 4294967295) {
          console.error('[FAIL] Error: --seed must be between -1 and 4294967295.');
          process.exit(1);
        }
      }
    }

    try {
      await generate({
        prompt,
        model,
        negativePrompt: negative,
        device,
        steps,
        cfgScale: cfg,
        seed,
        threads,
        output,
        samplingMethod: sampler,
        schedule,
        vaeTiling,
        initImg,
        strength,
        loraDir,
        clipSkip,
        controlNet,
        controlImage,
        controlStrength,
        taesd,
        autoProvision: true
      });
    } catch (err) {
      console.error('[FAIL] Generation error:', err.message);
      process.exit(1);
    }
  } else if (command === 'install') {
    runInstall();
  } else if (command === 'doctor') {
    runDoctor();
  } else if (command === 'models') {
    console.log('\n--- [Presets] Available Presets ---');
    for (const [k, v] of Object.entries(listPresets())) {
      console.log(`  - ${k.padEnd(12)} : ${v.description} (${v.size_mb}MB)`);
    }
    console.log('\n--- [Models] Locally Cached Models ---');
    const cached = listCachedModels();
    if (cached.length === 0) {
      console.log('  (No models cached yet. Run npx termux-diffusion download <model>)');
    }
    for (const m of cached) {
      console.log(`  - ${m.name.padEnd(25)} [${m.size_mb} MB] -> ${m.path}`);
    }
    console.log();
  } else if (command === 'download') {
    const model = args[1];
    if (!model) {
      console.error('[FAIL] Error: Model name required (e.g. npx termux-diffusion download realistic)');
      process.exit(1);
    }
    await downloadModel(model);
  } else if (command === 'clear-cache') {
    const count = clearCache();
    console.log(`[Clean] Removed ${count} cached model files.`);
  } else {
    printHelp();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
