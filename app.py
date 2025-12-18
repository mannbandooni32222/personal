import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(
    page_title="Website Scraper",
    layout="wide"
)

HISTORY_FILE = Path("history.json")

# ---------------------------
# HISTORY HELPERS
# ---------------------------
def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------------------
# SCRAPER FUNCTION
# ---------------------------
def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=10, headers=headers)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # 1 Email only
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            html
        )
        email = emails[0] if emails else "Not found"

        # Social links
        insta = soup.find("a", href=re.compile("instagram.com"))
        fb = soup.find("a", href=re.compile("facebook.com"))
        linkedin = soup.find("a", href=re.compile("linkedin.com"))

        return {
            "Website": url,
            "Email": email,
            "Instagram": insta["href"] if insta else "Not found",
            "Facebook": fb["href"] if fb else "Not found",
            "LinkedIn": linkedin["href"] if linkedin else "Not found",
            "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except:
        return {
            "Website": url,
            "Email": "Error",
            "Instagram": "Error",
            "Facebook": "Error",
            "LinkedIn": "Error",
            "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# ---------------------------
# UI
# ---------------------------
st.title("🌐 Website Email & Social Media Scraper")

urls_input = st.text_area(
    "Enter website URLs (one per line)",
    height=200,
    placeholder="example.com\nhttps://example.org"
)

scrape_btn = st.button("🚀 Start Scraping")

# ---------------------------
# SCRAPING
# ---------------------------
if scrape_btn:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if not urls:
        st.error("Please enter at least one website.")
        st.stop()

    results = []
    history = load_history()

    with st.spinner("Scraping websites..."):
        for url in urls:
            data = scrape_website(url)
            results.append(data)
            history.append(data)

    save_history(history)

    df = pd.DataFrame(results)

    st.success(f"Scraped {len(df)} websites")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button(
        "⬇ Download CSV",
        csv,
        "scraped_results.csv",
        "text/csv"
    )

# ---------------------------
# HISTORY SECTION
# ---------------------------
st.markdown("---")
st.subheader("📜 Scrape History")

history_data = load_history()

if history_data:
    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True)

    csv_history = history_df.to_csv(index=False)
    st.download_button(
        "⬇ Download Full History CSV",
        csv_history,
        "full_history.csv",
        "text/csv"
    )
else:
    st.info("No history yet.")

# ---------------------------
# HIDE STREAMLIT UI
# ---------------------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
