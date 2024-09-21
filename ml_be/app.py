from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape news articles from Wired's Security Category
def scrape_wired(category):
    url = f'https://www.wired.com/category/{category}/'
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        return {"error": "Failed to retrieve the page"}, 500

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the articles (summary and images) using the relevant CSS classes
    articles = soup.find_all('div', class_='SummaryItemWrapper-iwvBff')

    # Prepare a list to hold the scraped data
    news_data = []

    # Loop through each article and extract the relevant information
    for article in articles:
        title = article.find('h3',class_="SummaryItemHedBase-hiFYpQ").get_text() if article.find('h3',class_="SummaryItemHedBase-hiFYpQ") else 'No Title'
        summary = article.find('div',class_="SummaryItemDek-CRfsi").get_text() if article.find('div',class_="SummaryItemDek-CRfsi") else 'No Summary'
        # Extract the image URL from the 'ResponsiveImageContainer-eybHBd' class
        image_container = article.find('img', class_='ResponsiveImageContainer-eybHBd')
        image_url = image_container['src'] if image_container and image_container['src'] else 'No Image'

        # Append the article details to the list
        news_data.append({
            "title": title,
            "summary": summary,
            "image": image_url
        })

    return news_data

# Flask route to return the scraped data as JSON
@app.route('/scrape_wired_security', methods=['GET'])
def get_wired_security():
    news = scrape_wired("security")
    return jsonify(news), 200

@app.route('/scrape_wired_politics', methods=['GET'])
def get_wired_politics():
    news = scrape_wired("politics")
    return jsonify(news), 200

@app.route('/scrape_wired_business', methods=['GET'])
def get_wired_business():
    news = scrape_wired("business")
    return jsonify(news), 200

@app.route('/scrape_wired_science', methods=['GET'])
def get_wired_science():
    news = scrape_wired("science")
    return jsonify(news), 200

@app.route('/scrape_wired_culture', methods=['GET'])
def get_wired_culture():
    news = scrape_wired("culture")
    return jsonify(news), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
