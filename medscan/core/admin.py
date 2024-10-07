from django.contrib import admin

from . import models


@admin.register(models.Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("url", "created_at", "updated_at")
    search_fields = ("url",)
