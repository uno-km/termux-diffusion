#!/usr/bin/env node
/**
 * AMEVA Standard Node.js CLI Runner for termux_diffusion.
 * Automatically resolves Python 3 environment and dispatches to python -m termux_diffusion.
 */
const fs = require('fs');
const { spawn, execSync } = require('child_process');

function findPython() {
  if (process.env.PYTHON && fs.existsSync(process.env.PYTHON)) {
    return process.env.PYTHON;
  }
  const termuxBin = '/data/data/com.termux/files/usr/bin/python3';
  if (fs.existsSync(termuxBin)) {
    return termuxBin;
  }
  const termuxBinAlt = '/data/data/com.termux/files/usr/bin/python';
  if (fs.existsSync(termuxBinAlt)) {
    return termuxBinAlt;
  }
  const candidates = ['python3', 'python'];
  for (const cmd of candidates) {
    try {
      const checkCmd = process.platform === 'win32' ? `where ${cmd}` : `command -v ${cmd}`;
      const res = execSync(checkCmd, { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
      if (res) return cmd;
    } catch (_) {}
  }
  return 'python3';
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
