"""Vector store helpers.

Provides a Chroma-backed vector store (persistent) and keeps the
legacy LlamaIndex-based functions for backward compatibility.

Usage:
  - By default this module uses Chroma (set env var VECTOR_BACKEND=llama
    to use the original GPTVectorStoreIndex).
  - The Chroma functions accept an embedding provider (langchain/OpenAI
    embeddings by default) so you can swap in Gemini later.
"""
import os
from typing import List, Optional

# Legacy import kept for backward compatibility
from llama_index.core import GPTVectorStoreIndex, Document

try:
    import chromadb
    from chromadb.config import Settings
except Exception:
    chromadb = None

try:
    from langchain.embeddings import OpenAIEmbeddings
except Exception:
    OpenAIEmbeddings = None


class ChromaStore:
    """Simple Chroma-backed vector store helper.

    - Stores documents and embeddings in a persistent Chroma collection.
    - Uses LangChain OpenAI embeddings by default (requires OPENAI_API_KEY).
    - The embedder can be provided to allow switching to Gemini later.
    """

    def __init__(
        self,
        persist_directory: str = "db/chroma",
        collection_name: str = "aibuddy",
        embeddings=None,
    ):
        if chromadb is None:
            raise ImportError("chromadb is not installed. Please install chromadb in requirements.txt")

        self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_directory))
        self.collection = self.client.get_or_create_collection(name=collection_name)

        if embeddings is not None:
            self.embeddings = embeddings
        else:
            if OpenAIEmbeddings is None:
                raise ImportError("langchain OpenAIEmbeddings not available. Install langchain and an OpenAI SDK or pass a custom embedder")
            # Uses OPENAI_API_KEY from environment
            self.embeddings = OpenAIEmbeddings()

    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None, ids: Optional[List[str]] = None):
        """Add documents to the collection (computes embeddings automatically)."""
        if not texts:
            return
        embs = self.embeddings.embed_documents(texts)
        self.collection.add(documents=texts, embeddings=embs, metadatas=metadatas, ids=ids)

    def query(self, query_text: str, k: int = 5):
        """Query the collection and return the raw chroma response."""
        q_emb = self.embeddings.embed_query(query_text)
        res = self.collection.query(query_embeddings=[q_emb], n_results=k, include=["documents", "metadatas", "distances"])
        return res


def create_vector_store(texts: List[str], backend: Optional[str] = None, **kwargs):
    """Create a vector store using the selected backend.

    - backend: 'chroma' (default) or 'llama'
    - kwargs are forwarded to the selected backend constructor
    """
    backend = backend or os.getenv("VECTOR_BACKEND", "chroma")

    if backend.lower() == "chroma":
        store = ChromaStore(**kwargs)
        store.add_documents(texts)
        return store

    # Fallback to the original GPTVectorStoreIndex behavior
    docs = [Document(t) for t in texts]
    index = GPTVectorStoreIndex.from_documents(docs)
    return index


def query_vector_store(index_or_store, query: str, k: int = 5):
    """Run a semantic query against the given index or ChromaStore."""
    if isinstance(index_or_store, ChromaStore):
        return index_or_store.query(query, k=k)

    # Assume LlamaIndex index
    return index_or_store.as_query_engine().query(query)
