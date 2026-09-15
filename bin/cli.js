#!/usr/bin/env node
/**
 * AMEVA Standard Node.js CLI Runner for termux_diffusion.
 * Automatically resolves Python 3 environment and dispatches to python -m termux_diffusion.
 */
const { spawn } = require('child_process');

function findPython() {
  const candidates = [
    process.env.PYTHON,
    '/data/data/com.termux/files/usr/bin/python3',
    '/data/data/com.termux/files/usr/bin/python',
    'python3',
    'python'
  ].filter(Boolean);

  return candidates[0] || 'python3';
}

const pythonBin = findPython();
const args = ['-m', 'termux_diffusion', ...process.argv.slice(2)];

const child = spawn(pythonBin, args, {
  stdio: 'inherit',
  env: process.env
});

child.on('error', (err) => {
  console.error(`[${'termux_diffusion'}] Failed to spawn python process (${pythonBin}):`, err.message);
  process.exit(1);
});

child.on('exit', (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
  } else {
    process.exit(code || 0);
  }
});
