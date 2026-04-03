from .models import SiteMessage

def admin_message(request):
    msg = SiteMessage.objects.filter(is_active=True).first()
    return {'admin_message': msg.message if msg else None}