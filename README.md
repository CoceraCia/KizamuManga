<p align="center"><img width="300" alt="KizamuManga" src="https://github.com/user-attachments/assets/153c6620-7461-4ffe-a399-69aa9f03b885" /></p>

# 📚 KizamuManga  ![State](https://img.shields.io/badge/state-v1.0.1-green) ![License](https://img.shields.io/badge/license-MIT-blue.svg)

**KizamuManga** is a command-line tool to **search, download, and convert manga chapters into CBZ files** from different online sources.

## ✨ Main Features

- 🔎 **Interactive search** for manga and chapter selection directly from the terminal.
- ⚡ **Asynchronous downloads** with concurrency control, automatic CBZ export, and cleanup of temporary files.
- 🖼️ **Optional image processing**: grayscale conversion, margin cropping, and proportional resizing.
- 🌐 **Multi-source support** (WeebCentral, InManga, and LeerMangaEsp) with an extensible scraping system based on Playwright.
- 📊 **Progress indicators and rotating logs** for easy tracking of execution.

## ⚡ Quick Start

1. Install the program package via pip
```bash
pip install kizamu-manga
```

2. Install the playwright browsers
```bash
playwright install
```

3. start searching or installing a manga

```bash
kizamumanga search "One Piece"
kizamumanga install "One Piece"
```

## 🧾 Requirements

- Python **3.9 or higher**.
- Dependencies listed in `requirements.txt`.
- Playwright installed along with its browsers (`playwright install`).
- Access to the supported websites to fetch online chapters.

## ⚙️ Installation
### Option 1: Install from PyPI (recommended)
If you just want to use the tool:
```bash
pip install kizamu-manga
playwright install
```
### Option 2: Install from source
```bash
# Clone the repository
git clone https://github.com/<your-user>/kizamu-manga.git
cd kizamu-manga

# (Optional) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

## 🔧 Configuration

The `config.toml` file (at the project root) allows customization of parameters such as:

| Key                    | Description                                                      |
| ---------------------- | ---------------------------------------------------------------- |
| `cbz_path`           | Destination folder for CBZ files (default: `Documents/manga_downloads`).  |
| `website`            | Active source (`weeb_central` -> stable, `inmanga`-> unstable, `leermangaesp`) -> stable |
| `multiple_tasks`     | Maximum number of concurrent downloads.                          |
| `color`              | Export in color (`true`) or grayscale (`false`).             |
| `cropping_mode`      | Enable automatic margin cropping.                                |
| `width` / `height` | Target resolution; leave empty to keep original size.            |

You can also modify configuration directly from the terminal. Here are some common use cases:

### Change scraper source and concurrency:
```bash
  kizamumanga config scraper --website "inmanga" --multiple_tasks 5
```
- This switches the active scraper to inmanga and sets the maximum number of parallel download tasks to 5.
### Change output folder for CBZ files: 
```bash
  kizamumanga config paths --cbz_path "./my_manga"
```
- This updates the destination directory where downloaded CBZ files are stored.
### Apply a predefined resolution profile:
Currently supported device presets: boox_go_7 (more coming soon).
```bash
  kizamumanga config dimensions --device "boox_go_7"
```
- This automatically assigns width/height settings based on the Boox Go 7 device preset.
### Manually set output resolution: 
```bash
  kizamumanga config dimensions --width 1080 --height 1440
```
- This forces a custom resolution (1080×1440 px), overriding any preset device profile.
### Export in grayscale with margin cropping enabled: 
```bash
  kizamumanga config output --color false --cropping_mode true
```
- This configures exported images to be grayscale and have automatic margin cropping applied.


## 🕹️ Basic Usage

- Search for manga: `kizamumanga search "One Piece"`
- Download all chapters: `kizamumanga install "One Piece"`
- Download a specific chapter or range:
  - `kizamumanga install "One Piece" 5`
  - `kizamumanga install "One Piece" 10-15`

By default CBZ files are saved in:
- Linux/Mac: `$HOME/Documents/manga_downloads`
- Windows: `%USERPROFILE%\Documents\manga_downloads`

You can change the location by using `kizamumanga config paths --cbz_path "./my_manga"`.

## 🔄 Internal Workflow

1. The **Runner** validates arguments, loads configuration, and sets up the selected scraper.
2. Manga and chapter lists are fetched using **Playwright + BeautifulSoup**.
3. Each chapter is downloaded via `aiohttp`, optionally processed, and packed into a **CBZ**.

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

## 📜 License

This project is under the license [MIT](LICENSE).
