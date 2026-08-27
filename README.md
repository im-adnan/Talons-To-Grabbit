<div align="center">

# 🦅 Talons

**Universal Media Extractor Plugin for [Grabbit](https://github.com/grabbit)**  
*Engineered specifically for macOS Apple Silicon (ARM64)*

[![Platform](https://img.shields.io/badge/platform-macOS%20Apple%20Silicon-black.svg?style=flat-square&logo=apple)](https://apple.com)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=flat-square&logo=python)](https://python.org)
[![Powered By](https://img.shields.io/badge/powered%20by-yt--dlp-red.svg?style=flat-square&logo=youtube)](https://github.com/yt-dlp/yt-dlp)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

</div>

---

## Overview

**Talons** is a high-performance media stream extraction plugin for **Grabbit**. It enables universal video, audio, and stream resolution matching across thousands of online media sources by leveraging the latest open-source [yt-dlp](https://github.com/yt-dlp/yt-dlp) engine.

Rather than relying on outdated monolithic binaries, Talons dynamically synchronizes directly with the upstream `yt-dlp` repository, ensuring you always have cutting-edge extractor definitions and stream format support.

---

## ⚡ Key Features

- **macOS Apple Silicon Native**: Optimized for ARM64 architecture on macOS (M1/M2/M3/M4+).
- **Direct Upstream Sync**: Fetches and embeds fresh `yt-dlp` Python package directly from the official repository.
- **Smart Stream Selection**: Automatically chooses the highest quality direct HTTPS streams (MP4/M4A), prioritizing Apple-native containers and hardware-accelerated playback.
- **Audio-Only Mode**: Intelligent audio extraction with bitrate ranking and AAC/M4A/MP3 container preference.
- **Zero Binary Bloat**: Pure Python module execution with negligible storage overhead.
- **Automated Releases**: Built and published automatically via GitHub Actions.

---

## 📋 Requirements

- **macOS**: macOS 12.0 (Monterey) or higher on **Apple Silicon (ARM64)**
- **Grabbit**: Latest version of Grabbit Download Manager
- **Python**: Python 3.10+ (macOS system Python or Homebrew `/opt/homebrew/bin/python3`)

---

## 🚀 Installation

### Option 1: Download Prebuilt Release (Recommended)
1. Go to the [Releases](https://github.com/grabbit/grabbit-ytdlp-plugin/releases) section.
2. Download the latest `talons.gda` bundle.
3. Open Grabbit, navigate to **Settings / Plugins**, and select **Install Plugin** -> choose `talons.gda`.

### Option 2: Build from Source
```bash
# 1. Clone the repository
git clone https://github.com/grabbit/grabbit-ytdlp-plugin.git
cd grabbit-ytdlp-plugin

# 2. Build the talons.gda package
./build/build.sh
```
The packaged `talons.gda` plugin bundle will be generated in `build/talons.gda`.

---

## 🛠️ Building & Updating Upstream yt-dlp

### Fetching Fresh Upstream yt-dlp Code
To pull the latest `yt-dlp` code directly from their public open-source repository:
```bash
./build/fetch-ytdlp.sh
```

### Packaging the Plugin
To package the plugin into a `.gda` bundle:
```bash
./build/build.sh
```

---

## 📁 Repository Structure

```
grabbit-ytdlp-plugin/
├── .github/
│   └── workflows/
│       └── release.yml          # GitHub Actions CI/CD release workflow
├── build/
│   ├── build.sh                 # Packaging script -> build/talons.gda
│   └── fetch-ytdlp.sh           # Fetches latest upstream yt-dlp from GitHub
├── plugin/
│   ├── icon.svg                 # Branded Talons vector icon
│   ├── plugin.json              # Grabbit plugin manifest
│   ├── run.sh                   # Unix runner entrypoint
│   ├── extractor.py             # Stream filtering and metadata extraction engine
│   └── yt-dlp/                  # Bundled upstream yt_dlp Python package
├── .gitignore                   # Git hygiene & artifact exclusions
├── LICENSE                      # MIT License
└── README.md                    # Project documentation
```

---

## 🔍 Troubleshooting

- **Python Not Found**: Ensure Python 3 is installed and available in PATH (`which python3` or `brew install python`).
- **Site-Specific DRM or Captchas**: Some sites may require browser cookies. Ensure your Grabbit settings allow cookie access if required.
- **Updating Extractors**: Run `./build/fetch-ytdlp.sh` to refresh the embedded `yt-dlp` package whenever video sites update their player algorithms.

---

## 📄 License

Distributed under the [MIT License](LICENSE). Powered by the open-source [yt-dlp](https://github.com/yt-dlp/yt-dlp) project.
