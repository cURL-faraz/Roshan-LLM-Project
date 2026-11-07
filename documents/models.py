from django.db import models
from django.core.validators import FileExtensionValidator

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(max_length=255, upload_to="documents/", validators=[FileExtensionValidator(allowed_extensions=["docx"])])
    extracted_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self) -> str:
        return self.title
