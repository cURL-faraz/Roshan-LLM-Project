from rest_framework import viewsets

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """list, create, retrieve, update, partial_update and destroy for documents."""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
