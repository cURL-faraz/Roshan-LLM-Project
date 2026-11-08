"""Keep the Chroma index in sync with Document rows, whichever code path changed them."""

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from rag.pipeline import delete_document, index_document

from .models import Document

persist_directory = str(settings.CHROMA_DIR)
model_name = settings.EMBEDDING_MODEL


@receiver(post_save, sender=Document)
def index_on_save(sender, instance: Document, **kwargs) -> None:
    """After the DB transaction commits, (re)index this document."""
    document_id = instance.id
    title = instance.title
    text = instance.extracted_text
    transaction.on_commit(lambda: index_document(document_id=document_id, title=title, text=text, persist_directory=persist_directory, model_name=model_name), robust=True)   
    

@receiver(post_delete, sender=Document)
def remove_on_delete(sender, instance: Document, **kwargs) -> None:
    """After the DB transaction commits, remove this document's chunks."""
    document_id = instance.id
    transaction.on_commit(lambda: delete_document(document_id=document_id, persist_directory=persist_directory, model_name=model_name), robust=True)   
