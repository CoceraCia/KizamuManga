<p align="center">
  <img width="300" alt="KizamuManga" src="https://github.com/user-attachments/assets/153c6620-7461-4ffe-a399-69aa9f03b885" />
</p>

# 📚 KizamuManga

![State](https://img.shields.io/badge/state-v1.2.0-green)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

**KizamuManga** is an educational Python CLI project created to explore web automation, scraping, asynchronous workflows, concurrency control, image processing, terminal-based configuration, and CBZ file generation.

The project was built as a personal learning experience to design, structure, document, package, and publish a complete Python command-line tool.

> This repository does not include manga pages, panels, images, or copyrighted content.

---

## ⚠️ Responsible Use

KizamuManga was created for educational purposes and to practice Python software development through a real-world automation project.

This project is intended to demonstrate technical concepts such as:

- CLI design
- Web automation
- Scraping architecture
- Asynchronous I/O
- Concurrency control
- Image processing
- CBZ packaging
- Python packaging and PyPI distribution

Users are responsible for ensuring that any use of this tool complies with applicable laws, website terms of service, copyright restrictions, and content access permissions.

Do not use this project to download, distribute, or access copyrighted material without permission.

---

## ✨ Main Features

- 🔎 **Terminal-based search workflow** with interactive selection.
- ⚡ **Asynchronous processing pipeline** using concurrent network tasks.
- 🧵 **Concurrency control** for managing multiple tasks safely.
- 🖼️ **Optional image processing**, including grayscale conversion, margin cropping, and proportional resizing.
- 📦 **CBZ generation** for packaging processed image sequences.
- ⚙️ **Configurable behavior** through a local configuration file and terminal commands.
- 🧩 **Extensible source-adapter architecture** designed to separate scraping logic from the core application.
- 📊 **Progress indicators and rotating logs** for easier execution tracking.
- 🐍 **Packaged Python CLI** published as an installable PyPI package.

---

## 🧠 What I Learned

This project helped me practice several areas of Python development beyond writing simple scripts:

- Designing a real command-line interface.
- Structuring a Python project with separated responsibilities.
- Handling asynchronous downloads and I/O-bound workflows.
- Managing configuration through both files and CLI commands.
- Working with Playwright, BeautifulSoup, aiohttp, Pillow, and OpenCV.
- Building an image-processing pipeline.
- Creating CBZ archives programmatically.
- Packaging and publishing a Python project.
- Writing clearer documentation for an open-source-style repository.

---

## ⚡ Quick Start

### 1. Install the package

```bash
pip install kizamu-manga
```

### 2. Install Playwright browsers

```bash
playwright install
```

### 3. Check the available commands

```bash
kizamumanga --help
```

You can also inspect specific command groups:

```bash
kizamumanga config --help
```

---

## 🧾 Requirements

- Python **3.9 or higher**
- Playwright and its browser dependencies
- Dependencies listed in `requirements.txt`
- Network access for web automation workflows
- Permission to access and process the content used with the tool

---

## ⚙️ Installation

### Option 1: Install from PyPI

Recommended if you want to install the packaged CLI:

```bash
pip install kizamu-manga
playwright install
```

After installation, the command should be available from your terminal:

```bash
kizamumanga --help
```

---

### Option 2: Install from source

Recommended if you want to inspect, modify, or contribute to the project:

```bash
# Clone the repository
git clone https://github.com/CoceraCia/KizamuManga.git
cd KizamuManga

# Optional: create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

# Install the package in editable mode
pip install -e .

# Install Playwright browsers
playwright install
```

You can then run the tool with:

```bash
kizamumanga --help
```

Or directly as a Python module:

```bash
python -m kizamumanga.main
```

---

## 🔧 Configuration

The project uses a `config.toml` file to customize behavior such as output paths, active source adapter, concurrency, image settings, and target dimensions.

| Key              | Description |
| ---------------- | ----------- |
| `cbz_path`       | Destination folder for generated CBZ files. |
| `website`        | Active source adapter used by the scraping layer. |
| `multiple_tasks` | Maximum number of concurrent tasks. |
| `color`          | Export images in color (`true`) or grayscale (`false`). |
| `cropping_mode`  | Enable or disable automatic margin cropping. |
| `width`          | Target output width. Leave empty to preserve original size. |
| `height`         | Target output height. Leave empty to preserve original size. |

You can also update configuration directly from the terminal.

---

### Change source adapter and concurrency

```bash
kizamumanga config scraper --website "example_source" --multiple_tasks 5
```

This updates the active source adapter and sets the maximum number of parallel tasks to `5`.

---

### Change output folder

```bash
kizamumanga config paths --cbz_path "./output"
```

This updates the destination directory where generated CBZ files are stored.

---

### Apply a predefined device profile

Currently supported device presets:

```bash
boox_go_7
```

Example:

```bash
kizamumanga config dimensions --device "boox_go_7"
```

This automatically applies width and height settings based on the selected device profile.

---

### Manually set output resolution

```bash
kizamumanga config dimensions --width 1080 --height 1440
```

This forces a custom output resolution and overrides any active device preset.

---

### Configure grayscale output and margin cropping

```bash
kizamumanga config output --color false --cropping_mode true
```

This configures the output pipeline to export images in grayscale and apply automatic margin cropping.

---

## 🕹️ Basic Usage

The CLI exposes commands for searching, selecting, processing, and packaging content through the terminal.

For safety and documentation clarity, the examples below use placeholder names.

### Search workflow

```bash
kizamumanga search "sample-title"
```

### Run the processing workflow

```bash
kizamumanga install "sample-title"
```

### Process a specific item

```bash
kizamumanga install "sample-title" 5
```

### Process a range

```bash
kizamumanga install "sample-title" 10-15
```

By default, generated CBZ files are saved in:

```bash
~/Documents/manga_downloads
```

On Windows:

```bash
%USERPROFILE%\Documents\manga_downloads
```

You can change the destination folder with:

```bash
kizamumanga config paths --cbz_path "./output"
```

---

## 🔄 Internal Workflow

The project follows a modular workflow:

1. The **CLI layer** parses arguments and routes commands.
2. The **Runner** validates input, loads configuration, and initializes the selected source adapter.
3. The **scraping layer** fetches metadata using Playwright and BeautifulSoup.
4. The **downloader** handles asynchronous network tasks using aiohttp.
5. The **image processing pipeline** optionally applies grayscale conversion, cropping, and resizing.
6. The **packaging step** creates CBZ files from the processed images.
7. Temporary files are cleaned up after successful execution.

---

## 🧱 Architecture Overview

The project is organized around separation of responsibilities:

```text
CLI command
   ↓
Argument handler
   ↓
Runner
   ↓
Source adapter
   ↓
Async downloader
   ↓
Image converter
   ↓
CBZ output
```

This design makes it easier to maintain the core workflow while keeping source-specific scraping logic isolated in adapter modules.

---

## 🗂️ Project Structure

```bash
├── config.toml
├── pyproject.toml
├── requirements.txt
└── src/
    └── kizamumanga/
        ├── main.py
        ├── handlers/
        │   └── args_handler.py
        ├── engine/
        │   ├── runner.py
        │   ├── downloader.py
        │   ├── image_converter.py
        │   └── paths.py
        ├── scraping/
        │   ├── base.py
        │   ├── weeb_central.py
        │   ├── inmanga.py
        │   └── leermangaesp.py
        └── utils/
            ├── logger.py
            ├── loading_spinner.py
            └── general_tools.py
```

---

## 📦 PyPI

The package is available on PyPI and can be installed with:

```bash
pip install kizamu-manga
```

Project package name:

```bash
kizamu-manga
```

CLI command:

```bash
kizamumanga
```

---

## 🛣️ Roadmap

Some possible future improvements:

- Add automated tests.
- Improve CLI autocompletion.
- Improve error messages and validation.
- Add more robust retry and timeout handling.
- Add safer demo data using synthetic sample images.
- Improve documentation for the internal architecture.
- Add continuous integration with GitHub Actions.
- Refactor source adapters for easier extensibility.
- Add more device presets for output dimensions.

---

## 🤝 Contributing

This project was mainly created as a personal learning project, but suggestions, improvements, and technical feedback are welcome.

If you want to contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Open a pull request explaining what you improved.

Please keep contributions aligned with the educational and responsible-use purpose of the project.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

The license applies only to the source code in this repository. It does not grant rights over third-party content, websites, images, manga, trademarks, or copyrighted material accessed outside this repository.

---

## 🙋 Author

Created by **Miguel Cocera Cia** as a personal Python learning project focused on CLI development, automation, scraping architecture, asynchronous workflows, image processing, packaging, and documentation.
