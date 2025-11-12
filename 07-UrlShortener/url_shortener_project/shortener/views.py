from django.shortcuts import render, redirect, get_object_or_404
from .models import ShortURL

def home(request):
    if request.method == 'POST':
        original_url = request.POST.get('url')
        short_obj = ShortURL.objects.create(original_url=original_url)
        return render(request, 'shortener/home.html', {'short_code': short_obj.short_code})
    return render(request, 'shortener/home.html')


def redirect_url(request, code):
    short_obj = get_object_or_404(ShortURL, short_code=code)
    return redirect(short_obj.original_url)
