from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Subscriber, Newsletter
from .forms import SubscribeForm, UnsubscribeForm, NewsletterForm
from django.utils import timezone

def subscribe(request):
    """Subscribe to newsletter"""
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscriber = form.save(commit=False)
            
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                subscriber.ip_address = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
            else:
                subscriber.ip_address = request.META.get('REMOTE_ADDR')
            
            subscriber.user_agent = request.META.get('HTTP_USER_AGENT', '')
            subscriber.save()
            
            subscriber.send_confirmation_email()
            
            messages.success(request, 'Please check your email to confirm your subscription!')
            return redirect('newsletter:subscribe_success')
    else:
        form = SubscribeForm()
    
    return render(request, 'newsletter/subscribe.html', {'form': form})

def subscribe_success(request):
    """Subscription success page"""
    return render(request, 'newsletter/success.html')

def confirm_subscription(request, token):
    """Confirm subscription"""
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token, status='pending')
        subscriber.confirm_subscription()
        messages.success(request, 'Your subscription has been confirmed! Welcome to our newsletter!')
        return redirect('newsletter:subscribe_success')
    except Subscriber.DoesNotExist:
        messages.error(request, 'Invalid or expired confirmation link.')
        return redirect('newsletter:subscribe')

def unsubscribe(request, token=None):
    """Unsubscribe from newsletter"""
    if token:
        try:
            subscriber = Subscriber.objects.get(confirmation_token=token)
            subscriber.unsubscribe()
            messages.success(request, 'You have been unsubscribed from our newsletter.')
            return render(request, 'newsletter/unsubscribe.html', {'unsubscribed': True})
        except Subscriber.DoesNotExist:
            messages.error(request, 'Invalid unsubscribe link.')
    
    if request.method == 'POST':
        form = UnsubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                subscriber = Subscriber.objects.get(email=email)
                subscriber.unsubscribe()
                messages.success(request, 'You have been unsubscribed successfully.')
                return render(request, 'newsletter/unsubscribe.html', {'unsubscribed': True})
            except Subscriber.DoesNotExist:
                messages.error(request, 'Email not found.')
    else:
        form = UnsubscribeForm()
    
    return render(request, 'newsletter/unsubscribe.html', {'form': form, 'unsubscribed': False})

@staff_member_required
def newsletter_list(request):
    """List all newsletters (admin only)"""
    newsletters = Newsletter.objects.all()
    return render(request, 'newsletter/newsletter_list.html', {'newsletters': newsletters})

@staff_member_required
def newsletter_create(request):
    """Create new newsletter (admin only)"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save()
            messages.success(request, 'Newsletter created successfully!')
            return redirect('newsletter:newsletter_list')
    else:
        form = NewsletterForm()
    
    return render(request, 'newsletter/newsletter_form.html', {'form': form, 'title': 'Create Newsletter'})

@staff_member_required
def newsletter_edit(request, pk):
    """Edit newsletter (admin only)"""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter updated successfully!')
            return redirect('newsletter:newsletter_list')
    else:
        form = NewsletterForm(instance=newsletter)
    
    return render(request, 'newsletter/newsletter_form.html', {'form': form, 'title': 'Edit Newsletter'})

@staff_member_required
def newsletter_delete(request, pk):
    """Delete newsletter (admin only)"""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    
    if request.method == 'POST':
        newsletter.delete()
        messages.success(request, 'Newsletter deleted successfully!')
        return redirect('newsletter:newsletter_list')
    
    return render(request, 'newsletter/newsletter_confirm_delete.html', {'newsletter': newsletter})

@staff_member_required
def newsletter_send(request, pk):
    """Send newsletter immediately (admin only)"""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    
    if request.method == 'POST':
        # For now, just mark as sent
        newsletter.status = 'sent'
        newsletter.sent_at = timezone.now()
        newsletter.save()
        messages.success(request, f'Newsletter "{newsletter.subject}" has been sent!')
        return redirect('newsletter:newsletter_list')
    
    return render(request, 'newsletter/newsletter_send.html', {'newsletter': newsletter})