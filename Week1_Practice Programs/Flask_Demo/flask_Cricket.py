from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# =====================================================
# PLAYWRIGHT FUNCTION
# =====================================================

def get_cricket_news(search_query):

    headlines = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        # Open Cricbuzz search
        search_url = f"https://www.cricbuzz.com/search?q={search_query}"

        page.goto(search_url)

        page.wait_for_timeout(3000)

        # Extract headlines
        elements = page.locator("h3").all()

        for item in elements[:10]:

            try:
                text = item.inner_text().strip()

                if text:
                    headlines.append(text)

            except:
                pass

        browser.close()

    return headlines

# =====================================================
# HOME ROUTE
# =====================================================

@app.route("/", methods=["GET", "POST"])

def home():

    news = []

    if request.method == "POST":

        query = request.form["query"]

        news = get_cricket_news(query)

    return render_template(
        "index.html",
        news=news
    )

# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":

    app.run(debug=True)