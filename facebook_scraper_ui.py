import gradio as gr
import re
import csv
import os
import json
import pandas as pd
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

CREDENTIAL_FILE = "saved_credentials.json"
SESSION_FILE = "fb_state.json"
OUTPUT_FILE = "facebook_scraped_data.csv"

def load_credentials():
    if os.path.exists(CREDENTIAL_FILE):
        with open(CREDENTIAL_FILE, "r") as f:
            data = json.load(f)
            return data.get("email", ""), data.get("password", "")
    return "", ""

def save_credentials(email, password):
    with open(CREDENTIAL_FILE, "w") as f:
        json.dump({"email": email, "password": password}, f)

def to_about_url(fb_url):
    parsed = urlparse(fb_url)
    return f"https://m.facebook.com{parsed.path.rstrip('/')}/about/"

def is_valid_domain(text):
    return (
        re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", text)
        and not any(ext in text for ext in [".svg", ".png", ".wasm", ".react", ".ico", ".js"])
        and "facebook.com" not in text
    )

def extract_phone(html):
    soup = BeautifulSoup(html, "html.parser")
    for span in soup.find_all("span", string=re.compile(r"\(?\d{1,4}\)?[\s.-]?\d{2,4}[\s.-]?\d{2,4}")):
        text = span.get_text().strip()
        digits = re.sub(r"\D", "", text)
        if 8 <= len(digits) <= 15:
            return text
    return ""

def extract_email(html):
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}', html)
    return match.group() if match else ""

def extract_website(html):
    soup = BeautifulSoup(html, "html.parser")
    fb_links = soup.find_all("a", href=re.compile(r"l\.php\?u="))
    for link in fb_links:
        href = link.get("href", "")
        match = re.search(r"u=([^&]+)", href)
        if match:
            decoded = unquote(match.group(1))
            parsed = urlparse(decoded)
            if is_valid_domain(parsed.netloc) and not parsed.path.endswith(".php"):
                return parsed.netloc
    candidates = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', html)
    for candidate in candidates:
        if is_valid_domain(candidate) and not candidate.endswith(".php"):
            return candidate
    return ""

def sanitize_website(value):
    if not value:
        return ""
    value = value.strip().lower()
    if "static.xx.fbcdn.net" in value or value.endswith(".php"):
        return ""
    return value

def scrape_facebook_stream(email, password, search_term, max_links):
    save_credentials(email, password)
    fieldnames = ["Name", "Email", "Phone", "Website", "Page URL", "About URL"]
    results = []

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(storage_state=SESSION_FILE) if os.path.exists(SESSION_FILE) else browser.new_context()
        page = context.new_page()

        if not os.path.exists(SESSION_FILE):
            page.goto("https://www.facebook.com/login")
            try:
                page.locator('text="Only allow essential cookies", text="A nem kötelező cookie-k elutasítása"').first.click(timeout=4000)
            except: pass
            page.fill('input[name="email"]', email)
            page.fill('input[name="pass"]', password)
            page.click('button[name="login"]')
            page.wait_for_url("https://www.facebook.com/")
            context.storage_state(path=SESSION_FILE)

        page.goto(f"https://www.facebook.com/search/pages/?q={search_term}")
        for _ in range(10):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1000)

        anchors = page.query_selector_all('a[aria-hidden="true"][tabindex="-1"]')
        links = set()
        for anchor in anchors:
            href = anchor.get_attribute("href")
            if href and "facebook.com" in href and "/groups/" not in href:
                links.add(href.split("?")[0].rstrip("/"))
        business_links = list(links)[:int(max_links)]
        total = len(business_links)

        yield gr.update(value=pd.DataFrame([])), gr.update(value=None), gr.update(value=f"Found {total} business pages. Starting scraping...")

        for i, url in enumerate(business_links, 1):
            about_url = to_about_url(url)
            try:
                page.goto(about_url)
                page.wait_for_timeout(4000)
                html = page.content()
                row = {
                    "Name": page.title().replace(" | Facebook", "").strip(),
                    "Email": extract_email(html),
                    "Phone": extract_phone(html),
                    "Website": sanitize_website(extract_website(html)),
                    "Page URL": url,
                    "About URL": about_url
                }
            except:
                row = {
                    "Name": "Error", "Email": "", "Phone": "", "Website": "",
                    "Page URL": url, "About URL": about_url
                }

            results.append(row)
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(row)

            df_now = pd.DataFrame(results)
            progress_text = f"{i} / {total} done"
            yield gr.update(value=df_now), gr.update(value=OUTPUT_FILE), gr.update(value=progress_text)

        browser.close()

# --- Gradio UI
email_default, password_default = load_credentials()

with gr.Blocks() as app:
    gr.Markdown("## 📘 Facebook Business Scraper")

    with gr.Row():
        email = gr.Textbox(label="Facebook Email", value=email_default)
        password = gr.Textbox(label="Password", type="password", value=password_default)

    search_term = gr.Textbox(label="Search Term", value="étterem")
    max_links = gr.Number(label="Max Pages (1–300)", value=10, precision=0)

    run_btn = gr.Button("Start Scraping")
    progress = gr.Textbox(label="Progress", interactive=False)
    output_table = gr.Dataframe(label="Scraped Results", wrap=True)
    download = gr.File(label="Download CSV")

    run_btn.click(scrape_facebook_stream,
                  inputs=[email, password, search_term, max_links],
                  outputs=[output_table, download, progress])

app.launch()