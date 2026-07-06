import requests

def get_news(category):

    url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=5db3fba8ee0f452a93aa304bc8a9c1d1"

    response = requests.get(url)

    data = response.json()

    articles = data["articles"]

    return articles