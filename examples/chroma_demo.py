"""Small demo for Chroma-backed vector store.

Run as: python examples/chroma_demo.py

Make sure you set OPENAI_API_KEY in your environment (or pass a custom embedder).
"""

from processing.vector_store import create_vector_store, query_vector_store

SAMPLE_DOCS = [
    "Alice is a software engineer who loves Python and data.",
    "Bob is a product manager with experience in hiring and onboarding.",
    "Carol is a data scientist who works with machine learning and embeddings.",
]


def main():
    store = create_vector_store(SAMPLE_DOCS, persist_directory="db/chroma", collection_name="aibuddy_demo")
    res = query_vector_store(store, "Who works with embeddings?", k=2)
    print("Query results:")
    print(res)


if __name__ == "__main__":
    main()
