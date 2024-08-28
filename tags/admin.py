from django.contrib import admin
from .models import Tag

@admin.register(Tag)
class tagAdmin(admin.ModelAdmin):
    search_fields = ['label']

# Register your models here.
