import os
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

long_description = ""
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="termux-diffusion",
    version="1.0.0",
    description="Production On-Device AI Image Generation Framework for Android Termux & Samsung Galaxy (Dual-Engine Python & Node.js)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="uno-km (쌩초보코딩단)",
    author_email="hosequelbo@gmail.com",
    url="https://github.com/uno-km/termux-diffusion",
    project_urls={
        "Documentation": "https://uno-km.github.io/termux-diffusion/",
        "npm Package": "https://www.npmjs.com/package/termux-diffusion",
        "Bug Tracker": "https://github.com/uno-km/termux-diffusion/issues",
        "Source": "https://github.com/uno-km/termux-diffusion",
    },
    keywords=[
        "stable-diffusion", "diffusion", "termux", "android", "samsung-galaxy",
        "edge-ai", "on-device-ai", "image-generation", "gguf", "arm64",
        "bionic-libc", "snapdragon", "exynos", "text-to-image", "txt2img",
        "mobile-ai", "quantization", "generative-ai", "vulkan", "opencl",
        "offline-ai", "private-ai", "ai-art", "comfyui-alternative", "webui-alternative"
    ],
    packages=find_packages(),
    package_data={
        "termux_diffusion": ["py.typed"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "termux-diffusion = termux_diffusion.cli:main",
            "termux-diffusion-install = termux_diffusion.cli:run_install_cli",
            "termux-diffusion-doctor = termux_diffusion.cli:run_doctor_cli",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Android",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
    ],
)
