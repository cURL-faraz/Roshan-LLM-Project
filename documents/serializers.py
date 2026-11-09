from rest_framework import serializers

from rag.extraction import DocumentExtractionError, extract_docx_text

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """API input and output for documents. Upload validation mirrors DocumentAdminForm."""

    class Meta:
        model = Document
        fields = ["id", "title", "file", "extracted_text", "created_at", "updated_at"]
        read_only_fields = ["extracted_text", "created_at", "updated_at"]

    def validate(self, attrs: dict) -> dict:
        """Extract text when a new file arrives; a title-only PATCH has no file and keeps the old text."""
        file = attrs.get("file")
        if file:
            try:
                attrs["extracted_text"] = extract_docx_text(file)
            except DocumentExtractionError as exc:
                raise serializers.ValidationError({"file": str(exc)}) from exc
        return attrs
