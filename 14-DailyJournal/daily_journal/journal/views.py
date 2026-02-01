from django.utils import timezone
from datetime import timedelta

def index(request):
    if request.user.is_authenticated:
        # Calculate stats for dashboard
        total_entries = JournalEntry.objects.filter(author=request.user).count()
        
        # Entries from this month
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        recent_entries = JournalEntry.objects.filter(
            author=request.user, 
            date_created__gte=start_of_month
        ).count()
        
        # Today's entries
        today = timezone.now().date()
        today_entries = JournalEntry.objects.filter(
            author=request.user, 
            date_created__date=today
        ).count()
        
        context = {
            'recent_entries': recent_entries,
            'today_entries': today_entries,
        }
        return render(request, 'journal/index.html', context)
    
    return render(request, 'journal/index.html')