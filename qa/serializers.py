from rest_framework import serializers

from .models import QARecord


class AskRequestSerializer(serializers.Serializer):
    """Validates POST /api/ask/ input."""

    question = serializers.CharField(max_length=2000)


class QARecordSerializer(serializers.ModelSerializer):
    """Response body and history items."""

    class Meta:
        model = QARecord
        fields = ["id", "question", "answer", "sources", "model_name", "latency_ms", "created_at"]
