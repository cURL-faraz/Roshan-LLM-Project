"""Document API tests. Indexing is mocked, so no embedding model or Chroma is needed."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from docx import Document as DocxDocument
from .models import Document
from io import BytesIO
from rest_framework.test import APITestCase
import shutil
import tempfile
from unittest.mock import patch


def docx_upload(name: str = "sample.docx", text: str = "Hello سلام"):
    """Return an in-memory .docx as a SimpleUploadedFile."""
    docx = DocxDocument()
    docx.add_paragraph(text)
    buffer = BytesIO()
    docx.save(buffer)
    return SimpleUploadedFile(name, buffer.getvalue())

TEST_MEDIA_ROOT = tempfile.mkdtemp()
@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class DocumentApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()
    
    @patch("documents.signals.index_document")
    def test_upload_returns_201_saves_text_and_indexes_once(self, index_mock) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post("/api/documents/", {"title": "sample" , "file": docx_upload()}, format="multipart")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["extracted_text"], "Hello سلام")
        index_mock.assert_called_once()

    def test_wrong_extension_returns_400_and_saves_nothing(self) -> None:
        response = self.client.post("/api/documents/", {"title": "fake", "file": docx_upload("fake.zip", "Hello")}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("file", response.data)
        self.assertEqual(Document.objects.count(), 0)
    
    def test_fake_docx_returns_400_and_saves_nothing(self) -> None:
        response = self.client.post("/api/documents/", {"title": "fake", "file": SimpleUploadedFile("fake.docx", b"Hello")}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("file", response.data)
        self.assertEqual(Document.objects.count(), 0)
    
    @patch("documents.signals.index_document")
    def test_replacing_the_file_updates_text_and_reindexes(self, index_mock) -> None:
        document = Document.objects.create(title="initial", file=docx_upload(), extracted_text="old text")
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(f"/api/documents/{document.id}/", {"file": docx_upload(text="new text")}, format="multipart")
        self.assertEqual(response.status_code, 200)
        document.refresh_from_db()
        self.assertEqual(document.extracted_text, "new text")
        self.assertEqual(response.data["extracted_text"], "new text")
        index_mock.assert_called_once()
        self.assertEqual(index_mock.call_args.kwargs["text"], "new text")
    
    @patch("documents.signals.delete_document")
    def test_delete_returns_204_and_removes_chunks(self, delete_mock) -> None:
        document = Document.objects.create(title="current", file=docx_upload(), extracted_text="current text")
        document_id = document.id
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(f"/api/documents/{document.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Document.objects.filter(pk=document_id).exists())
        delete_mock.assert_called_once()
        self.assertEqual(delete_mock.call_args.kwargs["document_id"], document_id)
