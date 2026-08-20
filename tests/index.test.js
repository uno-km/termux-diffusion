/**
 * Unit tests for termux-diffusion Node.js engine
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const os = require('os');

const {
  generate,
  DEFAULT_PRESETS,
  listPresets,
  registerModel,
  setCacheDir,
  getCacheDir,
  isModelCached,
  listCachedModels,
  clearCache,
  detectHardwareProfile,
  resolveDeviceBackend,
  getSdCliGpuArgs,
  validateGgufFile,
  getMemoryInfo,
  checkMemorySafety,
  getOptimalThreadCount,
  detectNpuCapabilities,
  getDefaultNegativePrompt,
  setDefaultNegativePrompt,
  getQualityGuardNegativePrompt
} = require('../index.js');

async function runTests() {
  console.log('[TEST] Starting Node.js Engine Unit Tests...\n');
  let passed = 0;
  let total = 0;

  async function it(name, fn) {
    total++;
    try {
      await fn();
      console.log(`  [PASS] ${name}`);
      passed++;
    } catch (err) {
      console.error(`  [FAIL] ${name}:`, err.message);
    }
  }

  // 1. Presets
  await it('DEFAULT_PRESETS contains standard mobile models', () => {
    assert(DEFAULT_PRESETS.realistic, 'realistic model preset missing');
    assert(DEFAULT_PRESETS.speed, 'speed model preset missing');
    assert(DEFAULT_PRESETS.sdxs, 'sdxs model preset missing');
    assert.strictEqual(DEFAULT_PRESETS.sdxs.size_mb, 651);
  });

  // 2. Custom Model Registration
  await it('registerModel adds custom model to catalog', () => {
    registerModel('custom-test', {
      repo_id: 'org/repo',
      filename: 'custom.gguf',
      alias: 'custom_alias.gguf',
      description: 'Test Custom Model',
      steps: 8,
      cfg: 3.5
    });
    const presets = listPresets();
    assert(presets['custom-test'], 'custom-test not found in presets');
    assert.strictEqual(presets['custom-test'].default_steps, 8);
    assert.strictEqual(presets['custom-test'].default_cfg, 3.5);
  });

  // 3. Cache directory management
  await it('setCacheDir and getCacheDir manage cache path', () => {
    const tempDir = path.join(os.tmpdir(), `td_node_test_${Date.now()}`);
    setCacheDir(tempDir);
    assert.strictEqual(getCacheDir(), path.resolve(tempDir));
    fs.rmSync(tempDir, { recursive: true, force: true });
  });

  // 4. Hardware Profile Detection
  await it('detectHardwareProfile returns valid system capability profile', () => {
    const hw = detectHardwareProfile();
    assert(typeof hw.cpuArch === 'string');
    assert(typeof hw.cpuCores === 'number');
    assert(typeof hw.vulkanAvailable === 'boolean');
    assert(typeof hw.openclAvailable === 'boolean');
    assert(Array.isArray(hw.cmakeExtraFlags));
    assert(['cpu', 'vulkan', 'opencl'].includes(hw.recommendedBackend));
  });

  // 5. Device Backend Resolution
  await it('resolveDeviceBackend correctly handles cpu, auto, and fallbacks', () => {
    const cpuRes = resolveDeviceBackend('cpu');
    assert.strictEqual(cpuRes.effectiveDevice, 'cpu');
    assert.strictEqual(cpuRes.nglLayers, 0);

    const autoRes = resolveDeviceBackend('auto');
    assert(['cpu', 'vulkan', 'opencl'].includes(autoRes.effectiveDevice));

    const gpuArgs = getSdCliGpuArgs('vulkan', 99);
    assert.deepStrictEqual(gpuArgs, ['-ngl', '99']);

    const cpuArgs = getSdCliGpuArgs('cpu', 0);
    assert.deepStrictEqual(cpuArgs, []);
  });

  // 6. GGUF Magic Header Validation
  await it('validateGgufFile accurately validates GGUF binary format', () => {
    const tempGguf = path.join(os.tmpdir(), `test_valid_${Date.now()}.gguf`);
    const tempInvalid = path.join(os.tmpdir(), `test_invalid_${Date.now()}.gguf`);

    // Write real GGUF header ("GGUF" = 0x47 0x47 0x55 0x46 + uint32 version 3)
    const validHeader = Buffer.alloc(128);
    validHeader.write('GGUF', 0, 4, 'utf-8');
    validHeader.writeUInt32LE(3, 4);
    fs.writeFileSync(tempGguf, validHeader);
    fs.writeFileSync(tempInvalid, Buffer.from('NOT_GGUF_DATA'));

    assert.strictEqual(validateGgufFile(tempGguf), true, 'Valid GGUF header failed');
    assert.strictEqual(validateGgufFile(tempInvalid), false, 'Invalid header falsely approved');

    fs.unlinkSync(tempGguf);
    fs.unlinkSync(tempInvalid);
  });

  // 7. Memory info and safety guard
  await it('getMemoryInfo and checkMemorySafety return genuine OS metrics', () => {
    const mem = getMemoryInfo();
    assert(typeof mem.mem_total_mb === 'number');
    assert(typeof mem.effective_available_mb === 'number');
    assert(mem.mem_total_mb >= 0);

    const safety = checkMemorySafety(500);
    assert(typeof safety.safe === 'boolean');
    assert(typeof safety.message === 'string');
  });

  // 9. NPU Capabilities
  await it('detectNpuCapabilities returns structured NPU capability object and raises on npu device request', () => {
    const npu = detectNpuCapabilities();
    assert(typeof npu.available === 'boolean');
    assert(typeof npu.vendor === 'string');
    assert(typeof npu.topsRating === 'number');
    assert(Array.isArray(npu.supportedPrecisions));

    assert.throws(() => {
      resolveDeviceBackend('npu');
    }, /v2\.0 roadmap/);
  });

  // 10. Negative Prompt Configuration
  await it('getDefaultNegativePrompt and setDefaultNegativePrompt manage global negative guidance', () => {
    setDefaultNegativePrompt(null);
    assert.strictEqual(getDefaultNegativePrompt(), null);

    setDefaultNegativePrompt('low quality, blurry');
    assert.strictEqual(getDefaultNegativePrompt(), 'low quality, blurry');

    const guard = getQualityGuardNegativePrompt();
    assert(guard.includes('lowres'));
    assert(guard.includes('blur'));

    setDefaultNegativePrompt(null);
    assert.strictEqual(getDefaultNegativePrompt(), null);
  });

  // 11. Cancellation Propagation (AbortSignal)
  await it('generate respects pre-aborted AbortSignal immediately', async () => {
    const controller = new AbortController();
    controller.abort();
    let caught = false;
    try {
      await generate({ prompt: 'test prompt', signal: controller.signal });
    } catch (err) {
      caught = true;
      assert(err.message.includes('aborted'));
    }
    assert.strictEqual(caught, true, 'Pre-aborted signal should reject immediately');
  });

  // 12. Library Overreach Prevention (No unexpected compilation)
  await it('generate fails fast when engine missing without autoProvision', async () => {
    let caught = false;
    try {
      await generate({ prompt: 'test prompt', autoProvision: false });
    } catch (err) {
      caught = true;
      assert(err.message.includes('sd-cli') || err.message.includes('not found') || err.message.includes('termux-diffusion'));
    }
    assert.strictEqual(caught, true, 'Should not compile without explicit autoProvision: true');
  });

  console.log(`\n[RESULT] Node.js Test Results: ${passed}/${total} Passed.`);
  if (passed !== total) {
    process.exit(1);
  }
}

runTests().catch((err) => {
  console.error('[FAIL] Test execution error:', err);
  process.exit(1);
});
