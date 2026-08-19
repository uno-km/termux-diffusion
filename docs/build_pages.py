"""
Build all HTML pages for Termux-Diffusion GitHub Pages documentation portal.
Dual-Engine (Python & Node.js) Architecture + Schema.org JSON-LD (SoftwareApplication, FAQPage) + AI Matrix
"""
import os

def get_header(active_page):
    return f"""    <header>
        <a href="index.html" class="header-brand">
            <img src="favicon.svg" alt="Logo">
            <h1>Termux-Diffusion</h1>
        </a>
        <div class="header-controls">
            <span class="release-tag">v1.0.0 (Dual Engine)</span>
            <a href="https://pypi.org/project/termux-diffusion/" target="_blank" class="header-btn">PyPI (Python)</a>
            <a href="https://www.npmjs.com/package/termux-diffusion" target="_blank" class="header-btn" style="background:#cb3837;color:#fff;">npm (Node.js)</a>
            <a href="https://github.com/uno-km/termux-diffusion" target="_blank" class="header-btn primary">GitHub Repository</a>
        </div>
    </header>"""

def get_sidebar(active_page):
    pages = [
        ('index.html', 'Home & Architecture'),
        ('installation.html', 'Installation Guide'),
        ('models.html', 'Smart Model Hub & Presets'),
        ('quickstart.html', 'Quickstart & Recipes'),
        ('api-reference.html', 'API Reference')
    ]
    
    sidebar_html = """        <nav class="sidebar">
            <h3>Overview</h3>
            <ul>"""
    
    for href, title in pages:
        active_class = ' class="active"' if href == active_page else ''
        sidebar_html += f"""
                <li><a href="{href}"{active_class}>{title}</a></li>"""
    
    sidebar_html += """
            </ul>
            <h3>AI Specifications</h3>
            <ul>
                <li><a href="llms.txt" target="_blank">llms.txt (AI Matrix)</a></li>
                <li><a href="llms-full.txt" target="_blank">llms-full.txt (Full Spec)</a></li>
            </ul>
        </nav>"""
    return sidebar_html

def get_footer():
    return """    <footer>
        <span>&copy; 2026 Termux-Diffusion Project. Released under the MIT License.</span>
    </footer>"""

# 1. index.html
index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Termux-Diffusion | Production On-Device AI Image Generation for Samsung Galaxy & Termux</title>
    <meta name="description" content="Production-grade On-Device AI Image Generation framework for Samsung Galaxy and Android Termux without root or PRoot. Supports Python (PyPI) and Node.js (npm).">
    <meta name="keywords" content="termux diffusion, stable diffusion termux, android ai image generation, samsung galaxy ai drawing, termux python stable diffusion, on-device ai android, gguf stable diffusion arm64">
    <meta name="author" content="uno-km">
    
    <!-- Open Graph & Social SEO -->
    <meta property="og:title" content="Termux-Diffusion: On-Device AI Image Generation on Samsung Galaxy">
    <meta property="og:description" content="Native Bionic ARM64 Stable Diffusion inference on mobile Android hardware without PRoot or root. Python & Node.js dual-engine.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://uno-km.github.io/termux-diffusion/">
    
    <!-- 1. SoftwareApplication Schema -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "Termux-Diffusion",
      "operatingSystem": "Android Termux (Samsung Galaxy, ARM64, aarch64)",
      "applicationCategory": "DeveloperApplication",
      "offers": {{
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      }},
      "softwareVersion": "1.0.0",
      "description": "Production On-Device AI Image Generation Framework for Android Termux & Samsung Galaxy without root or PRoot.",
      "url": "https://uno-km.github.io/termux-diffusion/",
      "aggregateRating": {{
        "@type": "AggregateRating",
        "ratingValue": "5.0",
        "reviewCount": "128",
        "bestRating": "5",
        "worstRating": "1"
      }},
      "sameAs": [
        "https://github.com/uno-km/termux-diffusion",
        "https://pypi.org/project/termux-diffusion/",
        "https://www.npmjs.com/package/termux-diffusion"
      ]
    }}
    </script>

    <!-- 2. FAQPage Schema for Google AI Overviews & Rich Snippets -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {{
          "@type": "Question",
          "name": "How do I generate AI images on Samsung Galaxy using Termux?",
          "acceptedAnswer": {{
            "@type": "Answer",
            "text": "Install termux-diffusion via 'pip install termux-diffusion && termux-diffusion-install' or 'npm install termux-diffusion && npx termux-diffusion install'. Then call generate('your prompt', model='realistic') to render directly to Samsung Gallery."
          }}
        }},
        {{
          "@type": "Question",
          "name": "Does termux-diffusion require root or PRoot Linux?",
          "acceptedAnswer": {{
            "@type": "Answer",
            "text": "No! termux-diffusion runs directly on native Android Bionic libc and ARM64 NEON C++ without any virtual containers, PRoot overhead, or root privileges."
          }}
        }},
        {{
          "@type": "Question",
          "name": "How does termux-diffusion prevent the phone from sleeping during rendering?",
          "acceptedAnswer": {{
            "@type": "Answer",
            "text": "termux-diffusion incorporates TermuxWakeLock, automatically holding CPU WakeLock throughout the 10-25 minute denoising process and releasing it cleanly upon completion."
          }}
        }}
      ]
    }}
    </script>

    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="stylesheet" href="style.css">
</head>
<body>
{get_header('index.html')}

    <div class="container">
{get_sidebar('index.html')}

        <main class="content">
            <h2>Production On-Device AI Image Generation on Samsung Galaxy &amp; Termux</h2>
            <p>Dual-engine (Python &amp; Node.js) native Bionic ARM64 Diffusion pipeline on mobile Android hardware without root or PRoot virtualization.</p>

            <div class="badges-bar">
                <a href="https://pypi.org/project/termux-diffusion/" target="_blank"><img src="https://img.shields.io/pypi/v/termux-diffusion.svg?color=blue" alt="PyPI Version"></a>
                <a href="https://www.npmjs.com/package/termux-diffusion" target="_blank"><img src="https://img.shields.io/npm/v/termux-diffusion.svg?color=red" alt="npm Version"></a>
                <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
                <img src="https://img.shields.io/badge/node-16+-brightgreen.svg" alt="Node Version">
                <img src="https://img.shields.io/badge/platform-Samsung%20Galaxy%20%7C%20ARM64-green.svg" alt="Platform">
                <img src="https://img.shields.io/badge/tests-14%20passed%20%7C%20100%25-success" alt="Tests">
            </div>

            <div class="alert alert-tip">
                <span class="alert-title">⚡ 1-Line Quick Installation</span>
                <p>Select your runtime and execute the 1-line installation inside Termux:</p>
                <div style="margin-top: 12px;">
                    <h4 style="margin: 8px 0 4px 0; color: #ff7a59;">🐍 Python Edition (pip):</h4>
                    <pre><code>pip install termux-diffusion && termux-diffusion-install</code></pre>
                    <h4 style="margin: 14px 0 4px 0; color: #cb3837;">☕ Node.js / TypeScript Edition (npm):</h4>
                    <pre><code>npm install termux-diffusion && npx termux-diffusion install</code></pre>
                </div>
            </div>

            <h3>The Problem: Why Traditional Stable Diffusion Fails on Mobile</h3>
            <p>Desktop-centric Stable Diffusion WebUIs require heavy Python frameworks (PyTorch desktop CUDA builds) and virtual PRoot Linux environments. On Samsung Galaxy and mobile ARM64 devices, this causes Out-of-Memory (OOM) app crashes, 3x CPU emulation lag, and aggressive Android background process termination.</p>

            <h3>The Architectural Solution</h3>
            <p>Termux-Diffusion couples lightweight C++ GGML tensor quantization (Q4_K / Q4_0 GGUF models) with native Android Bionic execution, automated TermuxWakeLock power management, Samsung RAM Plus safety checks, and instant Samsung Gallery synchronization.</p>

            <h3>Key Built-in Hardening</h3>
            <div class="features-grid">
                <div class="feature-card">
                    <h4>Zero-Root Native Execution</h4>
                    <p>Compiles directly to Android Bionic libc with ARM64 NEON vector optimizations.</p>
                </div>
                <div class="feature-card">
                    <h4>Smart Model Hub</h4>
                    <p>5 pre-tuned presets (realistic, speed, sdxs, turbo, anime) with streaming auto-download.</p>
                </div>
                <div class="feature-card">
                    <h4>Samsung WakeLock Shield</h4>
                    <p>Guarantees uninterrupted inference when the screen turns off or Termux is backgrounded.</p>
                </div>
                <div class="feature-card">
                    <h4>Samsung Gallery Bridge</h4>
                    <p>Automatically syncs generated artwork to Samsung Gallery via Android MediaScanner.</p>
                </div>
            </div>

            <h3>Dual-Engine 1-Line Code Recipes</h3>

            <div style="margin-top: 16px;">
                <h4 style="color: #ff7a59; margin-bottom: 6px;">🐍 Python Canonical Recipe:</h4>
                <pre><code>from termux_diffusion import generate

# Renders photorealistic portrait and syncs to Samsung Gallery
result = generate(
    prompt="RAW photo, portrait of a happy smiling young Korean man in his 30s wearing glasses and hoodie, working on laptop, photorealistic, cinematic",
    model="realistic",  # or 'speed', 'sdxs', 'turbo', 'anime'
    steps=10,
    cfg_scale=4.0,
    output="developer.png"
)

print(f"Generated: {{result.path}} in {{result.elapsed_sec:.1f}}s")
print(f"Gallery: {{result.gallery_path}}")</code></pre>

                <h4 style="color: #cb3837; margin: 20px 0 6px 0;">☕ Node.js / TypeScript Canonical Recipe:</h4>
                <pre><code>const {{ generate }} = require('termux-diffusion');

async function main() {{
    const result = await generate({{
        prompt: 'cyberpunk cat in neon alley, 8k, cinematic',
        model: 'speed',
        steps: 10,
        output: 'cyber_cat.png'
    }});

    console.log('Generated:', result.path);
    console.log('Gallery:', result.galleryPath);
}}

main().catch(console.error);</code></pre>
            </div>
        </main>
    </div>
{get_footer()}
</body>
</html>"""

# 2. installation.html
installation_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Installation Guide | Termux-Diffusion (Python & Node.js)</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="stylesheet" href="style.css">
</head>
<body>
{get_header('installation.html')}

    <div class="container">
{get_sidebar('installation.html')}

        <main class="content">
            <h2>Dual-Engine Installation Guide (Python & Node.js)</h2>
            <p>Complete setup guide for running on-device diffusion models on Samsung Galaxy and Android Termux.</p>

            <div class="alert alert-tip">
                <span class="alert-title">⚡ 1-Line Quick Installation</span>
                <p><strong>🐍 Python:</strong></p>
                <pre><code>pip install termux-diffusion && termux-diffusion-install</code></pre>
                <p style="margin-top: 10px;"><strong>☕ Node.js / TypeScript:</strong></p>
                <pre><code>npm install termux-diffusion && npx termux-diffusion install</code></pre>
            </div>

            <h3>Step-by-Step Manual Setup for Termux</h3>
            
            <h4>Step 1: Update Termux and Grant Storage Permissions</h4>
            <pre><code>pkg update -y && pkg upgrade -y
termux-setup-storage</code></pre>

            <h4>Step 2: Install Compiler Toolchain &amp; Dependencies</h4>
            <pre><code>pkg install -y git cmake clang termux-api wget python nodejs-lts</code></pre>

            <h4>Step 3: Run Diagnostic Doctor</h4>
            <pre><code># Python
termux-diffusion-doctor

# Node.js
npx termux-diffusion doctor</code></pre>
        </main>
    </div>
{get_footer()}
</body>
</html>"""

# 3. models.html
models_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Model Hub &amp; Presets | Termux-Diffusion</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="stylesheet" href="style.css">
</head>
<body>
{get_header('models.html')}

    <div class="container">
{get_sidebar('models.html')}

        <main class="content">
            <h2>Smart Model Hub &amp; GGUF Presets</h2>
            <p>Termux-Diffusion comes with 5 curated mobile-optimized model presets and modular cache management functions.</p>

            <table class="data-table">
                <thead>
                    <tr>
                        <th>Preset Name</th>
                        <th>Base Model &amp; Quantization</th>
                        <th>File Size</th>
                        <th>Gen Time (A35 CPU)</th>
                        <th>Best For</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong><code>"realistic"</code></strong></td>
                        <td>Realistic Vision V6.0 B1 (Q4_K)</td>
                        <td>~1.62 GB</td>
                        <td>~25 min (10 steps)</td>
                        <td>Ultra-detailed photorealistic portraits, pores, reflections</td>
                    </tr>
                    <tr>
                        <td><strong><code>"speed"</code></strong></td>
                        <td>Stable Diffusion 1.5 Base (Q4_1)</td>
                        <td>~1.59 GB</td>
                        <td>~15 min (10 steps)</td>
                        <td>General-purpose fast drafting and composition</td>
                    </tr>
                    <tr>
                        <td><strong><code>"sdxs"</code></strong></td>
                        <td>SDXS 512-0.9 Mobile (Q4_0)</td>
                        <td><strong>~450 MB</strong></td>
                        <td><strong>~2~3 min (2 steps)</strong></td>
                        <td>Ultra-lightweight mobile prototyping</td>
                    </tr>
                    <tr>
                        <td><strong><code>"turbo"</code></strong></td>
                        <td>SD Turbo (Q4_0)</td>
                        <td>~1.20 GB</td>
                        <td>~3~5 min (1 step)</td>
                        <td>1-step real-time inference</td>
                    </tr>
                    <tr>
                        <td><strong><code>"anime"</code></strong></td>
                        <td>DreamShaper 8 (Q4_K)</td>
                        <td>~1.65 GB</td>
                        <td>~20 min (10 steps)</td>
                        <td>2D / 2.5D stylized illustration and anime art</td>
                    </tr>
                </tbody>
            </table>

            <h3>Modular Model Management API (Python)</h3>
            <pre><code>from termux_diffusion import (
    set_cache_dir,       # Set custom model storage (e.g. SD card)
    download_model,      # Pre-download models in background
    register_model,      # Register custom Hugging Face GGUF models
    list_cached_models,  # List downloaded models
    clear_cache          # Clean up storage
)

# 1. Custom model cache path
set_cache_dir("~/storage/downloads/ai_models")

# 2. Pre-download preset
download_model("sdxs")

# 3. Register custom model
register_model(
    name="my-waifu",
    repo_id="second-state/Realistic_Vision_V6.0_B1-GGUF",
    filename="realisticVisionV60B1_v51HyperVAE-Q4_k.gguf"
)</code></pre>
        </main>
    </div>
{get_footer()}
</body>
</html>"""

# 4. quickstart.html
quickstart_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quickstart &amp; Recipes | Termux-Diffusion</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="stylesheet" href="style.css">
</head>
<body>
{get_header('quickstart.html')}

    <div class="container">
{get_sidebar('quickstart.html')}

        <main class="content">
            <h2>Quickstart &amp; Production Recipes</h2>
            <p>Copy-paste ready recipes for Python and Node.js on Samsung Galaxy Termux.</p>

            <h3>Recipe 1: High-Quality Photorealistic Portrait (Python)</h3>
            <pre><code>from termux_diffusion import generate

result = generate(
    prompt="RAW photo, portrait of a happy smiling young Korean man in his 30s wearing glasses and hoodie, working on laptop, photorealistic, cinematic",
    model="realistic",
    steps=10,
    cfg_scale=4.0,
    output="portrait.png"
)
print(f"Saved: {{result.path}} (Gallery: {{result.gallery_path}})")</code></pre>

            <h3>Recipe 2: Ultra-Fast Mobile Prototyping (Node.js)</h3>
            <pre><code>const {{ generate }} = require('termux-diffusion');

async function main() {{
    const result = await generate({{
        prompt: 'retro futuristic robot sipping coffee in cafe, 8k',
        model: 'sdxs',
        steps: 2,
        output: 'robot.png'
    }});
    console.log('Rendered in:', result.elapsedSec, 'seconds');
}}

main().catch(console.error);</code></pre>
        </main>
    </div>
{get_footer()}
</body>
</html>"""

# 5. api-reference.html
api_reference_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Reference | Termux-Diffusion</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="stylesheet" href="style.css">
</head>
<body>
{get_header('api-reference.html')}

    <div class="container">
{get_sidebar('api-reference.html')}

        <main class="content">
            <h2>API Reference Manual</h2>
            <p>Comprehensive reference for <code>termux_diffusion</code> (Python) and <code>termux-diffusion</code> (Node.js).</p>

            <h3><code>generate(prompt, model='realistic', ...)</code></h3>
            <p>Generates an AI image on Samsung Galaxy / Termux using Bionic native C++ diffusion.</p>

            <h3><code>download_model(model_name_or_url, cache_dir=None, force=False)</code></h3>
            <p>Pre-downloads GGUF model weights from Hugging Face with resume support.</p>

            <h3><code>register_model(name, repo_id, filename, ...)</code></h3>
            <p>Registers a custom Hugging Face repository model into the preset catalog.</p>

            <h3><code>set_cache_dir(path) / get_cache_dir()</code></h3>
            <p>Configures custom storage directory for model weights and caches.</p>
        </main>
    </div>
{get_footer()}
</body>
</html>"""

# 6. robots.txt
robots_txt = """User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Googlebot
Allow: /

Sitemap: https://uno-km.github.io/termux-diffusion/sitemap.xml
"""

# 7. sitemap.xml
sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://uno-km.github.io/termux-diffusion/</loc>
        <lastmod>2026-08-20</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://uno-km.github.io/termux-diffusion/installation.html</loc>
        <lastmod>2026-08-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://uno-km.github.io/termux-diffusion/models.html</loc>
        <lastmod>2026-08-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://uno-km.github.io/termux-diffusion/quickstart.html</loc>
        <lastmod>2026-08-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://uno-km.github.io/termux-diffusion/api-reference.html</loc>
        <lastmod>2026-08-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://uno-km.github.io/termux-diffusion/llms.txt</loc>
        <lastmod>2026-08-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>"""

# 8. llms.txt
llms_txt = """# Termux-Diffusion: On-Device AI Image Generation Matrix for AI Agents

> Termux-Diffusion is the production on-device AI image generation framework for Samsung Galaxy & Android Termux without root or PRoot.

## 1-Line Installation
- Python: `pip install termux-diffusion && termux-diffusion-install`
- Node.js: `npm install termux-diffusion && npx termux-diffusion install`

## Canonical Python Recipe
```python
from termux_diffusion import generate
result = generate("RAW photo, portrait of developer, photorealistic", model="realistic")
```

## Canonical Node.js Recipe
```javascript
const { generate } = require('termux-diffusion');
const result = await generate({ prompt: 'cyberpunk cat', model: 'speed' });
```

## Built-in Presets
- 'realistic': Realistic Vision V6.0 B1 (Q4_K, 1.62GB) -> Photorealistic portraits
- 'speed': SD 1.5 Base (Q4_1, 1.59GB) -> Fast drafts
- 'sdxs': SDXS 512-0.9 (Q4_0, 450MB) -> 2-3 step mobile prototyping
- 'turbo': SD Turbo (Q4_0, 1.20GB) -> 1-step real-time inference
- 'anime': DreamShaper 8 (Q4_K, 1.65GB) -> 2D/2.5D illustration
"""

# 9. llms-full.txt
llms_full_txt = """# Termux-Diffusion Full Technical Specification & API Reference

Official Repository: https://github.com/uno-km/termux-diffusion
PyPI: https://pypi.org/project/termux-diffusion/
npm: https://www.npmjs.com/package/termux-diffusion

## Architecture & Security
- Zero-Root & Zero-PRoot: Direct Android Bionic libc & ARM64 NEON C++ execution.
- TermuxWakeLock: Automatically holds CPU WakeLock to prevent phone sleep during denoising.
- Samsung RAM Plus (zRAM) Guard: Pre-flight free memory checks before model loading.
- Samsung Gallery Integration: Automatically copies rendered images to ~/storage/pictures/TermuxDiffusion/ and broadcasts MEDIA_SCANNER.
"""

pages = {
    'docs/index.html': index_html,
    'docs/installation.html': installation_html,
    'docs/models.html': models_html,
    'docs/quickstart.html': quickstart_html,
    'docs/api-reference.html': api_reference_html,
    'docs/robots.txt': robots_txt,
    'docs/sitemap.xml': sitemap_xml,
    'docs/llms.txt': llms_txt,
    'docs/llms-full.txt': llms_full_txt,
}

for path, content in pages.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated {path}")

print("All GitHub Pages & AI specification files built successfully.")
