/**
 * TypeScript Type Definitions for termux-diffusion v1.1.0
 */

export interface ModelPresetInfo {
  repo_id: string;
  filename: string;
  alias: string;
  description: string;
  size_mb: number;
  default_steps: number;
  default_cfg: number;
  sha256?: string | null;
}

export interface CachedModelInfo {
  name: string;
  path: string;
  size_mb: number;
  mtime: Date;
  is_valid_gguf?: boolean;
}

export interface HardwareProfile {
  cpuArch: string;
  cpuCores: number;
  hasDotprod: boolean;
  hasFp16: boolean;
  hasI8mm: boolean;
  hasSve: boolean;
  socName: string;
  gpuName: string;
  vulkanAvailable: boolean;
  vulkanLibPath: string | null;
  openclAvailable: boolean;
  openclLibPath: string | null;
  recommendedBackend: 'cpu' | 'vulkan' | 'opencl';
  recommendedNgl: number;
  cmakeExtraFlags: string[];
}

export interface MemoryInfo {
  mem_total_mb: number;
  mem_available_mb: number;
  swap_total_mb: number;
  swap_free_mb: number;
  effective_total_mb: number;
  effective_available_mb: number;
}

export interface MemorySafetyResult {
  safe: boolean;
  message: string;
}

export interface GenerateOptions {
  prompt: string;
  model?: 'realistic' | 'speed' | 'sdxs' | 'turbo' | 'anime' | string;
  device?: 'cpu' | 'gpu' | 'opencl' | 'vulkan' | 'auto' | string;
  negativePrompt?: string;
  steps?: number;
  cfgScale?: number;
  width?: number;
  height?: number;
  seed?: number;
  threads?: number;
  output?: string;
  exportGallery?: boolean;
  lowRamGuard?: boolean;
  timeout?: number;
}

export interface GenerationResult {
  path: string;
  galleryPath: string | null;
  prompt: string;
  model: string;
  device?: string;
  steps: number;
  cfgScale: number;
  elapsedSec: number;
}

export interface RegisterModelOptions {
  repo_id?: string;
  repoId?: string;
  filename: string;
  alias?: string;
  description?: string;
  steps?: number;
  default_steps?: number;
  cfg?: number;
  default_cfg?: number;
  sha256?: string;
}

export const DEFAULT_PRESETS: Record<string, ModelPresetInfo>;

export function setCacheDir(customPath: string): string;
export function getCacheDir(): string;
export function registerModel(name: string, options: RegisterModelOptions): void;
export function listPresets(): Record<string, ModelPresetInfo>;
export function isModelCached(modelNameOrPath: string, cacheDir?: string): boolean;
export function listCachedModels(cacheDir?: string): CachedModelInfo[];
export function clearCache(cacheDir?: string, modelName?: string): number;
export function downloadModel(modelNameOrUrl: string, options?: { cacheDir?: string; force?: boolean }): Promise<string>;
export function resolveModelPath(modelNameOrPath: string, cacheDir?: string): Promise<string>;
export function locateSdCli(): string | null;
export function exportToAndroidGallery(sourcePath: string, destinationName?: string): string;
export function generate(options: GenerateOptions | string): Promise<GenerationResult>;
export function detectHardwareProfile(): HardwareProfile;
export function resolveDeviceBackend(requestedDevice?: string): { effectiveDevice: string; nglLayers: number };
export function getSdCliGpuArgs(device: string, ngl: number): string[];
export function validateGgufFile(filePath: string): boolean;
export function getMemoryInfo(): MemoryInfo;
export function checkMemorySafety(requiredMb?: number): MemorySafetyResult;
export function getOptimalThreadCount(): number;
