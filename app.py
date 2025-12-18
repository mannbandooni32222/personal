def extractor():
    st.title("Email & Social Media Extractor (Unlimited)")

    urls_input = st.text_area("Enter websites (one per line)")
    extract_btn = st.button("Extract")

    def extract_info(url):
        try:
            if not url.startswith("http"):
                url = "https://" + url

            html = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")

            emails = re.findall(
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
                html
            )
            email = emails[0] if emails else "Not found"

            insta = soup.find("a", href=re.compile("instagram.com"))
            fb = soup.find("a", href=re.compile("facebook.com"))

            return (
                email,
                insta["href"] if insta else "Not found",
                fb["href"] if fb else "Not found"
            )
        except:
            return "Error", "Error", "Error"

    if extract_btn:
        urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

        if not urls:
            st.error("Please enter at least one website.")
            return

        results = []

        with st.spinner("Extracting data..."):
            for url in urls:
                email, ig, fb = extract_info(url)
                results.append({
                    "Website": url,
                    "Email (1 only)": email,
                    "Instagram": ig,
                    "Facebook": fb
                })

        df = pd.DataFrame(results)

        st.success(f"Extracted {len(df)} websites")
        st.dataframe(df, use_container_width=True, height=600)

        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "results.csv",
            "text/csv"
        )
