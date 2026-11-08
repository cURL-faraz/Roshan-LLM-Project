"""Task 4a check: chunk the sample DOCX, index it into a THROWAWAY Chroma dir, run 2 searches.
Run from the project root:  python -m scripts.check_index path/to/file.docx
"""

import sys
import tempfile
from pathlib import Path

from rag.chunking import chunk_text
from rag.extraction import extract_docx_text
from rag.vectorstore import get_embeddings, get_vector_store

MODEL = "intfloat/multilingual-e5-small"


def main() -> None:
    with open(Path(sys.argv[1]), "rb") as f:
        text = extract_docx_text(f)
    chunks = chunk_text(document_id=1, title="sample", text=text)
    print(f"chunks: {len(chunks)}")
    for c in chunks:
        print(f"  {c.id}  meta={c.metadata}  {c.page_content[:60]!r}")

    tok = get_embeddings(MODEL)._client.tokenizer
    longest = max(len(tok(c.page_content)["input_ids"]) for c in chunks)
    print(f"longest chunk: {longest} tokens (must stay <= 512)")

    vec = get_embeddings(MODEL).embed_query("test")
    print(f"vector dim: {len(vec)}, norm: {sum(x * x for x in vec) ** 0.5:.3f}")

    with tempfile.TemporaryDirectory() as tmp:
        store = get_vector_store(tmp, MODEL)
        store.add_documents(chunks, ids=[c.id for c in chunks])
        store.add_documents(chunks, ids=[c.id for c in chunks])  # re-index: must NOT duplicate
        print(f"stored after indexing twice: {store._collection.count()} (expected {len(chunks)})")
        for q in ["چند روز مرخصی استعلاجی داریم؟", "How many sick leave days?"]:
            for doc, dist in store.similarity_search_with_score(q, k=2):
                print(f"  q={q!r}  dist={dist:.3f}  {doc.page_content[:50]!r}")


if __name__ == "__main__":
    main()
