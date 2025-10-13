from llama_index.core import GPTVectorStoreIndex, Document

def create_vector_store(texts: list):
    """Create a vector store from a list of documents."""
    docs = [Document(t) for t in texts]
    index = GPTVectorStoreIndex.from_documents(docs)
    return index

def query_vector_store(index, query: str):
    """Run a semantic query against the index."""
    return index.as_query_engine().query(query)
