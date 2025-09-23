<p align="center"><img width="300" alt="KizamuManga" src="https://github.com/user-attachments/assets/153c6620-7461-4ffe-a399-69aa9f03b885" /></p>

# 📚 KizamuManga  ![Estado](https://img.shields.io/badge/state-stable-brightgreen) ![Licencia](https://img.shields.io/badge/license-MIT-blue.svg)

**KizamuManga** is a command-line tool to **search, download, and convert manga chapters into CBZ files** from different online sources.
## ✨ Main Features
- 🔎 **Interactive search** for manga and chapter selection directly from the terminal.  
- ⚡ **Asynchronous downloads** with concurrency control, automatic CBZ export, and cleanup of temporary files.  
- 🖼️ **Optional image processing**: grayscale conversion, margin cropping, and proportional resizing.  
- 🌐 **Multi-source support** (WeebCentral, InManga, and LeerMangaEsp) with an extensible scraping system based on Playwright.  
- 📊 **Progress indicators and rotating logs** for easy tracking of execution.
##⚡Quick Start
1. Clone the repository and enter the project folder
```bash
git clone https://github.com/CoceraCia/KizamuManga
```
2. Enter the project repo
```bash
cd KizamuManga
```
3. install requirements and playwright browsers
```bash
pip install -r requirements.txt && playwright install
```
4. start searching or installing a manga
```bash
python -m kizamumanga.main search "One Piece"
python -m kizamumanga.main install "One Piece"
```

## 🧾 Requirements
- Python **3.9 or higher**.  
- Dependencies listed in `requirements.txt`.  
- Playwright installed along with its browsers (`playwright install`).  
- Access to the supported websites to fetch online chapters.  
## ⚙️ Installation
1. Clone the repository and enter the project folder.  
2. (Optional) Create and activate a virtual environment.  
3. Install dependencies: `pip install -r requirements.txt`  
4. Install Playwright browsers: `playwright install`  
## 🔧 Configuration
The `config.toml` file (at the project root) allows customization of parameters such as:
| Key              | Description |
|------------------|-------------|
| `cbz_path`       | Destination folder for CBZ files (default: `manga_downloads`). |
| `website`        | Active source (`weeb_central`, `inmanga`, `leermangaesp`). |
| `multiple_tasks` | Maximum number of concurrent downloads. |
| `color`          | Export in color (`true`) or grayscale (`false`). |
| `cropping_mode`  | Enable automatic margin cropping. |
| `width` / `height` | Target resolution; leave empty to keep original size. |
You can also modify configuration from the terminal:  
- Change scraper and concurrency: `python -m kizamumanga.main config scraper --website inmanga --multiple_tasks 5`  
- Change output folder: `python -m kizamumanga.main config paths --cbz_path "./my_manga"`  
- Apply predefined resolution profile: `python -m kizamumanga.main config dimensions --device boox_go_7`  
## 🕹️ Basic Usage
- Search for manga: `python -m kizamumanga.main search "One Piece"`  
- Download all chapters: `python -m kizamumanga.main install "One Piece"`  
- Download a specific chapter or range:  
  - `python -m kizamumanga.main install "One Piece" 5`  
  - `python -m kizamumanga.main install "One Piece" 10-15`  
CBZ files are saved in the folder defined by `cbz_path`.  
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


