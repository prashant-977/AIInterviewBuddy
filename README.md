# AIInterviewBuddy — Vector Store (Chroma) Integration

This repo now includes a Chroma-backed vector store to persist embeddings and enable efficient retrieval.

## Quick setup ✅
1. Create and activate a Python environment (recommended):
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Set your OpenAI API key for embeddings (or provide a custom embedding callable):
   ```bash
   set OPENAI_API_KEY=your_key_here   # PowerShell/Windows
   ```

## Usage (Chroma)
- Build a persistent collection and add documents:
  ```python
  from processing.vector_store import create_vector_store

  texts = ["Document one", "Document two"]
  store = create_vector_store(texts, persist_directory='db/chroma', collection_name='aibuddy')
  ```

- Query the collection:
  ```python
  from processing.vector_store import query_vector_store
  res = query_vector_store(store, "search query", k=5)
  ```

## Notes & roadmap
- **Default backend** is **Chroma** (persistent, metadata support, easy to use on Windows).
- **Switching backends**: set the environment variable `VECTOR_BACKEND` to `llama` to use the original `GPTVectorStoreIndex`, e.g.:

```bash
set VECTOR_BACKEND=llama   # PowerShell on Windows
```

Alternatively pass `backend='llama'` to `create_vector_store(...)`.

- **Embedding provider**: `ChromaStore` uses LangChain `OpenAIEmbeddings` by default (reads `OPENAI_API_KEY`), but you can pass any object implementing `embed_documents(texts)` and `embed_query(text)` to the `ChromaStore(..., embeddings=your_embedder)` constructor. This makes it straightforward to swap in Gemini or a Hugging Face embedding model later.

- **Future work:**
  - Add an explicit config file or `dataclass` for backend selection and tuning.
  - Add FAISS support (switchable) for very large indexes if needed.
  - Add Gemini embedding adapter and a Hugging Face deployment path.

- **Examples:** see `examples/chroma_demo.py`.

If you want, I can now add tests, an explicit config module for toggling FAISS/Chroma, or implement Gemini embedding integration next.