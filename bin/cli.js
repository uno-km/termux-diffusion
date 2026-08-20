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
  -m, --model <name>  Model preset name (default: realistic)
  -s, --steps <num>   Denoising steps (default: 10)
  -c, --cfg <num>     CFG guidance scale (default: 4.0)
  -o, --output <path> Destination output filename
`);
}

function runInstall() {
  console.log('[Start] [termux-diffusion] Running automated provisioner for native Bionic C++ engine...');
  const isTermux = fs.existsSync('/data/data/com.termux');
  if (isTermux) {
    console.log('[Package] Checking required packages via pkg (clang, cmake, git, termux-api)...');
    try {
      spawnSync('pkg', ['install', '-y', 'clang', 'cmake', 'git', 'termux-api', 'wget'], { stdio: 'inherit' });
    } catch (_) {}
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

  console.log('[Config] Configuring CMake build with ARM64 optimizations...');
  spawnSync('cmake', [
    '..',
    '-DCMAKE_BUILD_TYPE=Release',
    '-DSD_BUILD_EXAMPLES=ON',
    '-DGGML_OPENMP=OFF',
    '-DCMAKE_C_FLAGS=-O3 -D_GNU_SOURCE',
    '-DCMAKE_CXX_FLAGS=-O3 -D_GNU_SOURCE'
  ], { cwd: buildDir, stdio: 'inherit' });

  console.log('[Build] Compiling native Bionic binary with clang (make -j4)...');
  spawnSync('make', ['-j4'], { cwd: buildDir, stdio: 'inherit' });

  const binDir = path.join(os.homedir(), '.cache', 'termux-diffusion', 'bin');
  if (!fs.existsSync(binDir)) fs.mkdirSync(binDir, { recursive: true });
  const compiled = path.join(buildDir, 'bin', 'sd-cli');
  const target = path.join(binDir, 'sd-cli');

  if (fs.existsSync(compiled)) {
    fs.copyFileSync(compiled, target);
    fs.chmodSync(target, 0o755);
    console.log(`[Done] [termux-diffusion] Engine provisioned successfully at: ${target}`);
  } else {
    console.error('[FAIL] Could not find compiled sd-cli binary in build directory.');
    process.exit(1);
  }
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
    let steps, cfg, output;

    for (let i = 2; i < args.length; i++) {
      if (args[i] === '-m' || args[i] === '--model') model = args[++i];
      if (args[i] === '-s' || args[i] === '--steps') steps = parseInt(args[++i], 10);
      if (args[i] === '-c' || args[i] === '--cfg') cfg = parseFloat(args[++i]);
      if (args[i] === '-o' || args[i] === '--output') output = args[++i];
    }

    try {
      await generate({ prompt, model, steps, cfgScale: cfg, output });
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
