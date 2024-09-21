from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_articles(user_read_article, all_articles):
    # Extract titles and summaries for vectorization
    documents = [article['summary'] for article in all_articles]

    # Vectorize the text using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Get the index of the article the user just read
    user_article_index = documents.index(user_read_article['summary'])

    # Compute similarity scores
    similarity_scores = cosine_similarity(tfidf_matrix[user_article_index], tfidf_matrix)

    # Get indices of similar articles (excluding the one user just read)
    similar_indices = similarity_scores.argsort()[0][-6:-1]  # Top 5 similar articles

    # Recommend similar articles
    recommended_articles = [all_articles[i] for i in similar_indices]

    return recommended_articles


