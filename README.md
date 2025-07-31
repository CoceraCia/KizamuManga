<p align="center"><img width="300" alt="KizamuManga" src="https://github.com/user-attachments/assets/153c6620-7461-4ffe-a399-69aa9f03b885" /></p>

**KizamuManga** is a CLI-based manga downloader built with Python.

It allows you to search and download manga chapters from supported websites and automatically bundle them into CBZ files.

⚠️  **Disclaimer** : This project is for educational purposes only. I’m currently learning Python and working on improving my skills.

Feedback, suggestions, or even constructive criticism are very welcome!

---

## 📦 Features

* Search for manga titles
* List available chapters
* Download single or multiple chapters
* Export chapters into `.cbz` format
* Supports async downloading for better performance
* YAML-based configuration system

---

## 🚀 Getting Started

### 1. Clone the repository

git clone [https://github.com/your-username/kizamumanga.git](https://github.com/your-username/kizamumanga.git)

cd kizamumanga

### 2. Set up the environment

python -m venv .venv

source .venv/bin/activate  (On Windows: .venv\Scripts\activate)

pip install -r requirements.txt

### 3. Install Playwright browsers (if using web scraping)

playwright install

---

## ⚙️ Configuration

Edit the `config.yaml` file inside the `core/` directory to change settings like:

* Default website
* Download folder
* Number of concurrent downloads

---

## 🕹️ Usage

python main.py search --name "One Piece"

python main.py install --name "One Piece" --chap 1-5

python main.py config --website weeb_central

Run `python main.py --help` to see all available options.

---

## 📂 Project Structure

kizamumanga/

├── core/              # Main logic (config, downloader, runner)

├── handlers/          # Argument and config input handling

├── scraping/          # Scraper interfaces and site implementations

├── utils/             # Support tools (spinner, ascii art, etc.)

├── config.yaml        # User configuration

├── main.py            # CLI entry point

---

## 💬 Feedback Welcome!

As I'm still learning Python and software architecture, any feedback is more than welcome.

If you have ideas, find bugs, or see things that could be improved, feel free to open an issue or contact me.

Thanks for checking it out! 😊

---

## 📄 License

MIT License
