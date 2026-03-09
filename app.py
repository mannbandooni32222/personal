import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Website Scraper", layout="wide")

st.title("🌐 Website Email & Social Media Scraper")
st.write("Extract emails and social links from public websites.")

# ----------------------------
# INPUT
# ----------------------------
urls_input = st.text_area(
    "Enter website URLs (one per line)",
    height=200,
    placeholder="example.com\nhttps://example.org"
)

extract_btn = st.button("🚀 Start Scraping")

# ----------------------------
# SCRAPER FUNCTION
# ----------------------------
def scrape_website(url, session):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        response = session.get(url, timeout=8)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            html
        )

        email = emails[0] if emails else "Not found"

        insta = soup.find("a", href=re.compile("instagram.com"))
        fb = soup.find("a", href=re.compile("facebook.com"))
        linkedin = soup.find("a", href=re.compile("linkedin.com"))

        return {
            "Website": url,
            "Email": email,
            "Instagram": insta["href"] if insta else "Not found",
            "Facebook": fb["href"] if fb else "Not found",
            "LinkedIn": linkedin["href"] if linkedin else "Not found"
        }

    except Exception:
        return {
            "Website": url,
            "Email": "Error",
            "Instagram": "Error",
            "Facebook": "Error",
            "LinkedIn": "Error"
        }

# ----------------------------
# RUN SCRAPER
# ----------------------------
if extract_btn:

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if not urls:
        st.error("Please enter at least one website.")
        st.stop()

    results = []

    progress = st.progress(0)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    with ThreadPoolExecutor(max_workers=15) as executor:

        futures = [executor.submit(scrape_website, url, session) for url in urls]

        for i, future in enumerate(as_completed(futures)):
            results.append(future.result())
            progress.progress((i + 1) / len(urls))

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

# ----------------------------
# HIDE STREAMLIT UI
# ----------------------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
