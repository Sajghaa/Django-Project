from django.http import HttpResponse

def home(request):
    return HttpResponse('<h1>Hello Django! Welcome to your first project!</h1>')