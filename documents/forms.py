from django import forms
from django.core.files.uploadedfile import UploadedFile
from .models import Document
from rag.extraction import extract_docx_text, DocumentExtractionError

class DocumentAdminForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ("title", "file")

    def clean_file(self):
        """Validate the upload by extracting its text; store the text on the instance."""
        file = self.cleaned_data["file"]
        if isinstance(file, UploadedFile):
            try:
                extracted_text = extract_docx_text(file)
            except DocumentExtractionError as exc:
                raise forms.ValidationError(str(exc)) from exc
            self.instance.extracted_text = extracted_text
        return file

