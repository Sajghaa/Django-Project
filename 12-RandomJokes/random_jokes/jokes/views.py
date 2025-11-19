import random
from django.shortcuts import render

JOKES = [
    "Why don’t scientists trust atoms? Because they make up everything!",
    "I told my computer I needed a break… and it said 'No problem, I’ll go to sleep.'",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why was the math book sad? It had too many problems.",
    "Why don’t skeletons fight each other? They don’t have the guts.",
    "Why do Java developers wear glasses? Because they can’t C#.",
    "What do you call fake spaghetti? An impasta!",
    "Why did the smartphone need glasses? It lost all its contacts!"
]

def home(request):
    joke = random.choice(JOKES)
    return render(request, "jokes/home.html", {"joke": joke})
