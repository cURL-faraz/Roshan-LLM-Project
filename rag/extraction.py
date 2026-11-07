"""DOCX → plain text. Pure Python: no Django imports, so it can be tested and reused anywhere."""

from typing import BinaryIO

from docx import Document as DocxDocument
from docx.opc.exceptions import PackageNotFoundError
from docx.table import Table
from docx.text.paragraph import Paragraph
from zipfile import BadZipFile


class DocumentExtractionError(Exception):
    """Raised when a file cannot be read as a DOCX or contains no text."""

def extract_docx_text(file: BinaryIO) -> str:
    """Return the full text of a DOCX file, with paragraphs and tables in document order.

    Args:
        file: a binary file-like object (an open file, BytesIO, or a Django UploadedFile).

    Returns:
        The text, with blocks separated by newlines and whitespace trimmed.

    Raises:
        DocumentExtractionError: the file is not a valid DOCX, or it has no extractable text.
    """
    try:
        try:
            doc = DocxDocument(file)
        except (BadZipFile, PackageNotFoundError, KeyError) as exc:
            raise DocumentExtractionError("The file is not a valid word(.docx) document.") from exc
        blocks = []
        for block in doc.iter_inner_content():
            if isinstance(block, Paragraph):
                paragraph = block.text.strip()
                if paragraph:
                    blocks.append(paragraph)
            elif isinstance(block, Table): 
                for row in block.rows:
                    cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if cells:
                        blocks.append(" | ".join(cells))
        if not blocks:
            raise DocumentExtractionError("The document contains no text.")
        return "\n".join(blocks)
    finally:
        file.seek(0)
    
