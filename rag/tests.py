"""Pure-logic tests: no database, no network, no embedding model."""

from django.test import SimpleTestCase

from langchain_core.documents import Document as LCDocument
from docx import Document as DoxcDocument
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from rag.extraction import extract_docx_text, DocumentExtractionError
from rag.fusion import reciprocal_rank_fusion
from rag.generation import generate_answer, GenerationError
from rag.retrieval import _drop_duplicate_text
from rag.sparse import tokenize, bm25_search
from io import BytesIO


def chunk(chunk_id: str, text: str):
    """Build one LangChain Document with this id and text."""
    return LCDocument(page_content=text, id=chunk_id)

class TokenizeTests(SimpleTestCase):
    def test_folds_arabic_characters_and_persian_digits(self) -> None:
        text_1 = tokenize("كتابي ۲")
        text_2 = tokenize("کتابی 2")
        self.assertEqual(text_1, text_2)
         

class Bm25SearchTests(SimpleTestCase):
    def test_empty_corpus_returns_empty_list(self) -> None:
        self.assertEqual(bm25_search("dog",[], 4), [])
    def test_rare_term_ranks_its_chunk_first(self) -> None:
        chunks = []
        for chunk_id, text in enumerate(["cats sleep all day", "dogs chase the ball", "birds build nests"], start=1):
            chunks.append(chunk(chunk_id, text))
        sparse_list = bm25_search("dogs", chunks, 4)
        self.assertEqual(sparse_list[0].id, "2")


class ReciprocalRankFusionTests(SimpleTestCase):
    def test_chunk_in_both_lists_beats_chunk_in_one(self) -> None:
        chunks = []
        for chunk_id, text in enumerate(["a", "b", "c"], start=1):
            chunks.append(chunk(chunk_id, text))
        dense_list = [chunks[0], chunks[1]]
        sparse_list = [chunks[1], chunks[2]]
        fused = reciprocal_rank_fusion([dense_list, sparse_list])
        self.assertEqual(fused[0][0].page_content, "b")
    def test_score_matches_the_formula(self) -> None:
        chunks = []
        for chunk_id, text in enumerate(["a", "b", "c"], start=1):
            chunks.append(chunk(chunk_id, text))
        dense_list = [chunks[0], chunks[1]]
        sparse_list = [chunks[1], chunks[2]]
        fused = reciprocal_rank_fusion([dense_list, sparse_list])
        self.assertAlmostEqual(fused[0][1], 123/3782)

class DropDuplicateTextTests(SimpleTestCase):
    def test_same_text_with_different_ids_is_kept_once(self) -> None:
        fused = [(chunk(1, "a"), 0.03), (chunk(2, "A"), 0.02), (chunk(3, "b"), 0.01)]
        unique_fused = _drop_duplicate_text(fused)
        self.assertEqual([chunk.id for chunk, _ in unique_fused], ["1", "3"])

class ExtractionTests(SimpleTestCase):
    def test_docx_text_is_extracted_including_persian(self) -> None:
        docx = DoxcDocument()
        docx.add_paragraph("Hello سلام")
        buffer = BytesIO()
        docx.save(buffer)
        buffer.seek(0)
        self.assertEqual(extract_docx_text(buffer), "Hello سلام")

    def test_non_docx_bytes_raise_extraction_error(self) -> None:
        with self.assertRaises(DocumentExtractionError):
            extract_docx_text(BytesIO(b"not a docx"))

class GenerateAnswerTests(SimpleTestCase):
    def test_blank_llm_reply_raises_generation_error(self) -> None:
        chunks = []
        for chunk_id, text in enumerate(["cats sleep all day", "dogs chase the ball", "birds build nests"], start=1):
            chunks.append(chunk(chunk_id, text))
        fake_llm = FakeListChatModel(responses=[""])
        with self.assertRaises(GenerationError):
            generate_answer("dog", chunks, fake_llm)
