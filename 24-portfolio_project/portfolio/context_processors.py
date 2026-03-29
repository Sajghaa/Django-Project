from .models import SiteInfo, Category, Service

def site_info(request):
    """Context processor to add site info to all templates"""
    try:
        info = SiteInfo.objects.first()
    except:
        info = None
    
    return {
        'site_info': info,
    }

def categories(request):
    """Add categories to all templates"""
    categories = Category.objects.all()
    return {
        'categories': categories,
    }

def services_nav(request):
    """Add services to all templates for navigation"""
    services = Service.objects.filter(is_active=True)
    return {
        'services_nav': services,
    }