"""Keyword (BM25) search over chunks. Pure Python: no Django imports."""

from langchain_core.documents import Document as LCDocument
from rank_bm25 import BM25Okapi
import unicodedata
import re

_CHAR_MAP = str.maketrans({"ي": "ی",
                            "ك": "ک",
                            **{chr(i): str(i - ord("۰")) for i in range(ord("۰"), ord("۹") + 1)},
                            **{chr(i): str(i - ord("٠")) for i in range(ord("٠"), ord("٩") + 1)}
})


def tokenize(text: str) -> list[str]:
    """Case-folded word tokens with Arabic letter forms and digits normalized, the same for documents and questions."""
    text = unicodedata.normalize("NFKC", text)
    text = text.casefold()
    text = text.translate(_CHAR_MAP)
    return re.findall(r"\w+", text)

def bm25_search(question: str, chunks: list[LCDocument], k: int) -> list[LCDocument]:
    """Return up to k chunks that match the question, best first. Empty if nothing matches."""
    if not chunks:
        return []
    tokenized_chunks = [tokenize(chunk.page_content) for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    scores = bm25.get_scores(tokenize(question))
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [chunks[top] for top in order[:k] if scores[top] > 0]
