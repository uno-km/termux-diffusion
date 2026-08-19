/**
 * TypeScript Type Definitions for termux-diffusion
 */

export interface ModelPresetInfo {
  repo_id: string;
  filename: string;
  alias: string;
  description: string;
  size_mb: number;
  default_steps: number;
  default_cfg: number;
}

export interface CachedModelInfo {
  name: string;
  path: string;
  size_mb: number;
  mtime: Date;
}

export interface GenerateOptions {
  prompt: string;
  model?: 'realistic' | 'speed' | 'sdxs' | 'turbo' | 'anime' | string;
  negativePrompt?: string;
  steps?: number;
  cfgScale?: number;
  width?: number;
  height?: number;
  seed?: number;
  threads?: number;
  output?: string;
  exportGallery?: boolean;
  timeout?: number;
}

export interface GenerationResult {
  path: string;
  galleryPath: string | null;
  prompt: string;
  model: string;
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
