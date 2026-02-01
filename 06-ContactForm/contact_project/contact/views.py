from django.shortcuts import render
from .forms import ContactForm

def contact_view(request):
    success = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Instead of sending real email, just print
            print(f"📬 New message from {name} <{email}>:\n{message}\n")

            success = True
    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form, 'success': success})
