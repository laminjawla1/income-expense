from django.contrib import admin
from .models import Zone


class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'supervisor', 'limit']
    search_fields = ['name', 'supervisor__username',]
admin.site.register(Zone, ZoneAdmin)