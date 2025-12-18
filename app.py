import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Website Email & Social Scraper",
    layout="wide"
)

st.title("🌐 Website Email & Social Media Scraper")
st.write("Scrape public websites to extract email, Instagram & Facebook links.")

# -------------------------
# INPUT
# -------------------------
urls_input = st.text_area(
    "Enter website URLs (one per line)",
    height=200,
    placeholder="example.com\nhttps://example.org"
)

extract_btn = st.button("🚀 Start Scraping")

# -------------------------
# SCRAPER FUNCTION
# -------------------------
def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, timeout=10, headers=headers)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # Email (1 only)
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            html
        )
        email = emails[0] if emails else "Not found"

        # Instagram
        insta = soup.find("a", href=re.compile("instagram.com"))
        instagram = insta["href"] if insta else "Not found"

        # Facebook
        fb = soup.find("a", href=re.compile("facebook.com"))
        facebook = fb["href"] if fb else "Not found"

        return email, instagram, facebook

    except Exception as e:
        return "Error", "Error", "Error"

# -------------------------
# RUN SCRAPER
# -------------------------
if extract_btn:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if not urls:
        st.error("Please enter at least one website URL.")
        st.stop()

    results = []

    with st.spinner("Scraping websites..."):
        for url in urls:
            email, ig, fb = scrape_website(url)
            results.append({
                "Website": url,
                "Email": email,
                "Instagram": ig,
                "Facebook": fb
            })

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

# -------------------------
# HIDE STREAMLIT UI
# -------------------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
