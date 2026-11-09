from django.contrib import admin

from .models import QARecord

@admin.register(QARecord)
class QARecordAdmin(admin.ModelAdmin):
    list_display = ["question", "model_name", "latency_ms", "created_at"]
    search_fields = ["question"]
    readonly_fields = ["question", "answer", "sources", "model_name", "latency_ms", "created_at"]
    def has_add_permission(self, request):
        return False
