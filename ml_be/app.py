from flask import Flask, jsonify
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
# from ml_be.recommend import recommend_articles
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
from bson import ObjectId , json_util

def recommend_articles(user_read_article, all_articles):
    # Extract titles and summaries for vectorization
    documents = [article['summary'] for article in all_articles]

    # Vectorize the text using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Get the index of the article the user just read
    try:
        user_article_index = documents.index(user_read_article['summary'])
    except ValueError:
        return []  # In case the user_read_article is not in the documents

    # Compute similarity scores
    similarity_scores = cosine_similarity(tfidf_matrix[user_article_index], tfidf_matrix)

    # Get indices of similar articles (excluding the one user just read)
    similar_indices = similarity_scores.argsort()[0][-6:-1]  # Top 5 similar articles

    # Recommend similar articles
    recommended_articles = [all_articles[i] for i in similar_indices if i != user_article_index]

    return recommended_articles

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
client = MongoClient('mongodb+srv://prathmeshrajurkar199:sryzt5xxUfQC9PWR@newsaggregator.crblc.mongodb.net/')
db = client.newsaggregator 
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
        db.articles.insert_one({
            "category":category,
            "title": title,
            "summary": summary,
            "image": image_url,
            "likes": 0
        })
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


@app.route('/api/articles', methods=['GET'])
def get_articles():
    articles = db.articles.find()  # Retrieve all articles from the MongoDB collection
    articles_list = []
    i=0
    # Iterate through MongoDB documents and prepare the data to return
    for article in articles:
        id = json_util.dumps(article.get('_id'))
        articles_list.append({
            'id': str(article.get('_id')),
            'title': article.get('title', 'No Title'),
            'summary': article.get('summary', 'No Summary'),
            'image': article.get('image', 'No Image'),
            'likes': article.get('likes',0)
        })
        i=i+1

    return jsonify(articles_list)  # Return the data in JSON format

# API route to fetch articles by category (e.g., security, technology)
@app.route('/api/articles/<category>', methods=['GET'])
def get_articles_by_category(category):
    articles = db.articles.find({"category": category})  # Find articles matching the category
    articles_list = []

    for article in articles:
        articles_list.append({
            'title': article.get('title', 'No Title'),
            'summary': article.get('summary', 'No Summary'),
            'image': article.get('image', 'No Image'),
            'likes': article.get('likes',0)
        })

    return jsonify(articles_list)

@app.route(f'/api/articles/<article_id>/like', methods=['POST'])
def update_likes(article_id):
    try:
        # Convert the article_id from string to ObjectId
        # article_obj_id = ObjectId(article_id)

        # Find the article and increment the 'likes' field by 1
        db.articles.update_one(
            {'_id': ObjectId(article_id)},
            {'$inc': {'likes': 1}}  # Increment the 'likes' field by 1
        )
        
        # Fetch the updated article to return in the response
        updated_article = db.articles.find_one({'_id': article_obj_id})
        
        # Return the updated article data
        return jsonify({
            '_id': str(updated_article.get('_id')),
            'title': updated_article.get('title'),
            'likes': updated_article.get('likes', 0)  # Return updated likes
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/articles/liked', methods=['GET'])
def get_liked_articles():
    liked_articles = db.articles.find({'likes': {'$gt': 0}})  # Filter where 'likes' > 0
    articles_list = []
    
    for article in liked_articles:
        articles_list.append({
            '_id': str(ObjectId(article.get('_id'))),
            'title': article.get('title', 'No Title'),
            'summary': article.get('summary', 'No Summary'),
            'image': article.get('image', 'No Image'),
            'likes': article.get('likes', 0)  # Default to 0 if not present
        })

    return jsonify(articles_list)

@app.route('/api/articles/recommend', methods=['POST'])
def recommend_news():
    try:
        # Get the article the user read from the request data
        user_read_article_id = request.json.get('article_id')
        if not user_read_article_id:
            return jsonify({'error': 'Article ID is required'}), 400

        # Find the user's read article from MongoDB
        user_read_article = db.articles.find_one({'_id': ObjectId(user_read_article_id)})
        if not user_read_article:
            return jsonify({'error': 'Article not found'}), 404

        # Convert the MongoDB article to the format used in the recommendation system
        user_read_article = {
            '_id': str(user_read_article.get('_id')),
            'title': user_read_article.get('title', 'No Title'),
            'summary': user_read_article.get('summary', 'No Summary'),
            'image': user_read_article.get('image', 'No Image'),
            'likes': user_read_article.get('likes', 0)
        }

        # Get all articles (including liked ones)
        all_articles = get_all_articles()

        # Get recommended articles
        recommended_articles = recommend_articles(user_read_article, all_articles)

        return jsonify(recommended_articles), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


db.articles.update_one(
            {'_id': "ObjectID(66ee737787e46be19a8a3d06)"},
            {'$inc': {'likes': 1}}  # Increment the 'likes' field by 1
        )


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
