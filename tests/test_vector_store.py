import os
import shutil

from processing.vector_store import create_vector_store, query_vector_store


class FakeEmbeddings:
    def embed_documents(self, texts):
        # return fixed-dim numeric vectors (no external API calls)
        return [[float(len(t))] * 4 for t in texts]

    def embed_query(self, q):
        return [float(len(q))] * 4


def test_chroma_store_add_and_query(tmp_path):
    persist_dir = str(tmp_path / "chroma_db")
    docs = ["Alice likes python", "Bob works with embeddings."]
    store = create_vector_store(
        docs,
        persist_directory=persist_dir,
        collection_name="test",
        embeddings=FakeEmbeddings(),
    )

    res = query_vector_store(store, "embeddings", k=1)
    assert isinstance(res, dict)
    assert "documents" in res
    assert len(res["documents"][0]) >= 1


def test_create_vector_store_llama(monkeypatch):
    # Quick test for the legacy llama backend using a dummy index
    class DummyIndex:
        def as_query_engine(self):
            class QE:
                def query(self, q):
                    return "ok"

            return QE()

    from llama_index.core import GPTVectorStoreIndex

    monkeypatch.setattr(GPTVectorStoreIndex, "from_documents", lambda docs: DummyIndex())
    idx = create_vector_store(["a", "b"], backend="llama")

    assert hasattr(idx, "as_query_engine")
    res = query_vector_store(idx, "any")
    assert res == "ok"
