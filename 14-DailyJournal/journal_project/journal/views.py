from django.shortcuts import render, redirect, get_object_or_404
from .models import Entry
from .forms import EntryForm

def home(request):
    entries = Entry.objects.order_by('-created_at')
    return render(request, 'journal/home.html', {'entries': entries})

def add_entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EntryForm()
    return render(request, 'journal/add_entry.html', {'form': form})

def edit_entry(request, id):
    entry = get_object_or_404(Entry, id=id)
    if request.method == "POST":
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EntryForm(instance=entry)
    return render(request, 'journal/edit_entry.html', {'form': form, 'entry': entry})

def delete_entry(request, id):
    entry = get_object_or_404(Entry, id=id)
    entry.delete()
    return redirect('home')
