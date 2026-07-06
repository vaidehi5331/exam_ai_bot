import os
import requests

def get_news(category):

    api_key = os.getenv("NEWS_API_KEY")

    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={api_key}"

    response = requests.get(url)

    data = response.json()

    articles = data.get("articles", [])

    return articles