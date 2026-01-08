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
- Default backend is **Chroma** (persistent, metadata support, easy to use on Windows).
- You can switch to the legacy LlamaIndex in `create_vector_store(..., backend='llama')` if needed.
- Future: optionally add a config switch to toggle FAISS/Chroma and a Gemini embedding adapter (for the free Gemini model) before migrating to Hugging Face deployment.
- Examples: see `examples/chroma_demo.py`.

If you want, I can now add tests, a config switch for FAISS, or implement Gemini embedding integration next.