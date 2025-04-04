from django.contrib import admin
from .models import Navigators,Mentorados,Horarios,Reuniao

# Register your models here.
admin.site.register(Navigators)
admin.site.register(Mentorados)
admin.site.register(Horarios)
admin.site.register(Reuniao)