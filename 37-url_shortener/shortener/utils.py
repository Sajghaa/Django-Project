import re
from urllib.parse import urlparse
import user_agents
from django.utils import timezone
from .models import Click

def validate_url(url):
    """Validate if URL is properly formatted"""
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, url) is not None

def extract_domain(url):
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc

def parse_user_agent(user_agent_string):
    """Parse user agent to extract browser, OS, device type"""
    if not user_agent_string:
        return {'browser': 'Unknown', 'os': 'Unknown', 'device': 'Unknown'}
    
    ua = user_agents.parse(user_agent_string)
    
    return {
        'browser': ua.browser.family,
        'os': ua.os.family,
        'device': 'Mobile' if ua.is_mobile else 'Tablet' if ua.is_tablet else 'Desktop'
    }

def is_unique_click(url, ip_address, session_id, hours=1):
    """Check if click is unique (not from same IP in last hour)"""
    from django.utils import timezone
    from datetime import timedelta
    
    time_threshold = timezone.now() - timedelta(hours=hours)
    
    # Check for recent click from same IP or session
    recent_click = Click.objects.filter(
        url=url,
        clicked_at__gte=time_threshold
    ).filter(
        models.Q(ip_address=ip_address) | models.Q(session_id=session_id)
    ).exists()
    
    return not recent_click

def generate_qr_code(url):
    """Generate QR code for URL (optional)"""
    try:
        import qrcode
        from io import BytesIO
        import base64
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except ImportError:
        return None