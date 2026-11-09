from django.db import models


class QARecord(models.Model):
    """One answered question: the persistent history the assessment requires."""

    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)
    model_name = models.CharField(max_length=255)
    latency_ms = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return self.question[:60]
