import os
import shutil

import processing.vector_store as vs
from processing.vector_store import create_vector_store, query_vector_store


class FakeEmbeddings:
    def embed_documents(self, texts):
        # return fixed-dim numeric vectors (no external API calls)
        return [[float(len(t)) * 1.0] * 4 for t in texts]

    def embed_query(self, q):
        return [float(len(q)) * 1.0] * 4


class FakeChromaModule:
    class config:
        class Settings:
            def __init__(self, **kwargs):
                pass

    class _Client:
        def __init__(self, settings):
            self._collections = {}

        def get_or_create_collection(self, name):
            if name not in self._collections:
                self._collections[name] = self.FakeCollection()
            return self._collections[name]

        class FakeCollection:
            def __init__(self):
                self.docs = []
                self.embs = []
                self.metadatas = []
                self.ids = []

            def add(self, documents, embeddings, metadatas=None, ids=None):
                self.docs.extend(documents)
                self.embs.extend(embeddings)
                self.metadatas.extend(metadatas or [{}] * len(documents))
                self.ids.extend(ids or [str(i) for i in range(len(documents))])

            def query(self, query_embeddings, n_results=5, include=None):
                # simple distance by first dimension
                q = query_embeddings[0][0]
                scores = [abs(e[0] - q) for e in self.embs]
                idxs = sorted(range(len(scores)), key=lambda i: scores[i])[:n_results]
                documents = [[self.docs[i] for i in idxs]]
                metadatas = [[self.metadatas[i] for i in idxs]]
                distances = [[scores[i] for i in idxs]]
                return {"documents": documents, "metadatas": metadatas, "distances": distances}

    def Client(self, settings):
        return self._Client(settings)


def test_chroma_store_add_and_query(tmp_path, monkeypatch):
    # Replace chromadb with a fake in-memory module so tests don't need external deps
    fake = FakeChromaModule()
    monkeypatch.setattr(vs, "chromadb", fake)
    # vector_store imports Settings at module scope; patch it too
    monkeypatch.setattr(vs, "Settings", fake.config.Settings, raising=False)

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

    # Patch the Document used in processing.vector_store to accept a positional arg
    monkeypatch.setattr(vs, "Document", lambda t: t)
    monkeypatch.setattr(GPTVectorStoreIndex, "from_documents", lambda docs: DummyIndex())

    idx = create_vector_store(["a", "b"], backend="llama")

    assert hasattr(idx, "as_query_engine")
    res = query_vector_store(idx, "any")
    assert res == "ok"
