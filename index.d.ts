/**
 * TypeScript Type Definitions for termux-diffusion v1.8.0
 * Pure CPU & Mobile Vulkan GPU On-Device Stable Diffusion / DiT Runtime for Android Termux
 */

import { EventEmitter } from 'events';

export type ProgressPhase =
  | 'init'
  | 'loading_model'
  | 'encoding_prompt'
  | 'sampling'
  | 'decoding_vae'
  | 'complete'
  | 'error';

export interface ProgressEvent {
  event: 'progress' | 'phase' | 'complete';
  phase: ProgressPhase;
  step: number;
  totalSteps: number;
  percent: number;
  etaSeconds?: number | null;
  speedSecPerIt?: number | null;
  gpuBusy?: number | null;
  rssMb?: number | null;
  outputPath?: string | null;
  elapsedSeconds?: number | null;
  timestamp: number;
}

export interface DiffusionJob extends EventEmitter, PromiseLike<GenerationResult> {
  on(event: 'progress', listener: (data: ProgressEvent) => void): this;
  on(event: 'phase', listener: (phase: ProgressPhase) => void): this;
  on(event: 'done', listener: (result: GenerationResult) => void): this;
  on(event: 'error', listener: (err: Error) => void): this;
  wait(): Promise<GenerationResult>;
  cancel(): void;
}

export interface ModelPresetInfo {
  repo_id: string;
  filename: string;
  alias: string;
  description: string;
  size_mb: number;
  default_steps: number;
  default_cfg: number;
  default_sampler?: string;
  default_schedule?: string;
  default_device?: string;
  default_vae_tiling?: boolean;
  is_dit?: boolean;
  sha256?: string | null;
}

export interface CachedModelInfo {
  name: string;
  path: string;
  size_mb: number;
  mtime: Date;
  is_valid_gguf?: boolean;
}

export interface NPUProfile {
  available: boolean;
  vendor: 'qualcomm_hexagon' | 'samsung_eden' | 'google_edge_tpu' | 'android_nnapi' | 'none';
  chipsetName: string;
  driverLibrary: string | null;
  dspArchitecture: string;
  topsRating: number;
  supportedPrecisions: string[];
  delegateType: string;
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
  npuProfile?: NPUProfile;
  recommendedBackend: 'cpu' | 'vulkan' | 'opencl' | 'npu' | 'tpu';
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
  model?: 'realistic' | 'speed' | 'sdxs' | 'turbo' | 'anime' | 'z-image-turbo' | 'z-image' | 'turbo-6b' | string;
  preset?: 'realistic' | 'speed' | 'sdxs' | 'turbo' | 'anime' | 'z-image-turbo' | 'z-image' | 'turbo-6b' | string;
  device?: 'cpu' | 'gpu' | 'opencl' | 'vulkan' | 'auto' | string;
  negativePrompt?: string;
  steps?: number;
  cfgScale?: number;
  guidance?: number;
  width?: number;
  height?: number;
  seed?: number;
  threads?: number;
  output?: string;
  samplingMethod?: string;
  schedule?: string;
  vaeTiling?: boolean;
  initImg?: string;
  strength?: number;
  loraDir?: string;
  clipSkip?: number;
  controlNet?: string;
  controlImage?: string;
  controlStrength?: number;
  taesd?: string | boolean;
  llm?: string;
  diffusionModel?: string;
  vae?: string;
  clipL?: string;
  diffusionFa?: boolean;
  offloadToCpu?: boolean;
  clipOnCpu?: boolean;
  vaeOnCpu?: boolean;
  mmap?: boolean;
  maxVram?: string;
  streamLayers?: boolean;
  paramsBackend?: string;
  vaeFormat?: 'auto' | 'flux' | 'sd3' | 'flux2' | 'wan' | string;
  strictVulkan?: boolean;
  noCache?: boolean;
  exportGallery?: boolean;
  wakeLock?: boolean;
  lowRamGuard?: boolean;
  autoProvision?: boolean;
  progress?: boolean;
  jsonProgress?: boolean;
  progressFile?: string;
  onProgress?: (event: ProgressEvent) => void;
  signal?: AbortSignal;
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

export class TermuxDiffusion {
  constructor(config?: Partial<GenerateOptions>);
  generate(options: GenerateOptions | string): DiffusionJob;
  listPresets(): Record<string, ModelPresetInfo>;
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
export function locateSdCli(backend?: string): string | null;
export function exportToAndroidGallery(sourcePath: string, destinationName?: string): string;
export function generate(options: GenerateOptions | string): DiffusionJob;
export function detectHardwareProfile(): HardwareProfile;
export function detectNpuCapabilities(): NPUProfile;
export function resolveDeviceBackend(requestedDevice?: string): { effectiveDevice: string; nglLayers: number };
export function getSdCliGpuArgs(device: string, ngl: number): string[];
export function validateGgufFile(filePath: string): boolean;
export function getMemoryInfo(): MemoryInfo;
export function getOptimalThreadCount(): number;
export function getDefaultNegativePrompt(): string | null;
export function setDefaultNegativePrompt(prompt?: string | null): void;
export function getQualityGuardNegativePrompt(): string;
