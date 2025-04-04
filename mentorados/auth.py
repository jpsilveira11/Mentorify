from .models import Mentorados

def validate_token(token):
    return Mentorados.objects.filter(token=token).first()