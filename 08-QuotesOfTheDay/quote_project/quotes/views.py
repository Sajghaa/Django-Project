import requests
from django.shortcuts import render

def quote_view(request):
    response = requests.get("https://zenquotes.io/api/random")
    data = response.json()[0]
    quote = data["q"]
    author = data["a"]
    return render(request, "quote.html", {"quote": quote, "author": author})
