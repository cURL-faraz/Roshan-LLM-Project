from django.contrib import admin

from .models import Document 


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "file", "created_at", "updated_at")
    search_fields = ("title", )
    readonly_fields = ("extracted_text", "created_at", "updated_at")
