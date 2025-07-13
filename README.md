# 📘 Facebook Lead Scraper

A simple tool to scrape Facebook business pages for:

- **Name**  
- **Email**  
- **Phone number**  
- **Website**  

---

## 🚀 Prerequisites

- **Python 3.7+** installed  
  Download: https://www.python.org/downloads/

- **Git** (optional, but recommended)

---

## 🛠️ Setup

### Linux / macOS

1. Make the setup script executable:  
   ```bash
   chmod +x setup.sh
   ```
2. Run it:  
   ```bash
   ./setup.sh
   ```

### Windows

1. Double-click **`setup.bat`**, or run in a Command Prompt:  
   ```bat
   setup.bat
   ```

This will:

1. Create a virtual environment (`venv/`)  
2. Activate it  
3. Upgrade `pip`  
4. Install dependencies from `requirements.txt`  
5. Install Playwright and its browser binaries  

---

## ▶️ Running the App

Once setup is complete, start the UI:

```bash
python facebook_scraper_ui.py
```

1. **First launch** will prompt you to log in to Facebook.  
2. Enter your **email** & **password** (saved locally in `saved_credentials.json`).  
3. Complete any usual 2-factor or cookie consents.  

---

## 🧩 How It Works

1. You enter a **search term** (e.g. “restaurant”).  
2. The scraper finds Facebook business pages matching that term.  
3. It visits each page’s **About** section and extracts:
   - Name  
   - Email  
   - Phone  
   - Website  
   - Page URL  
   - About URL  
4. Results are shown in the UI and saved to `facebook_scraped_data.csv`.

---

## ⚠️ Usage Guidelines

- Respect Facebook’s rate limits and terms of service.  
- Do **not** abuse—keep requests reasonable.  
- This is intended for personal or testing purposes only.

---

## 📂 Project Structure

```text
├── setup.sh                   # Linux/macOS setup script
├── setup.bat                  # Windows setup script
├── requirements.txt           # Python dependencies
├── facebook_scraper_ui.py     # Main application
├── saved_credentials.json     # (auto-generated on first login)
└── facebook_scraped_data.csv  # (output file)
```

---

## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch  
3. Submit a Pull Request  

Happy scraping! 🕷️  
