import json
from pathlib import Path
from tempfile import mkdtemp
import typer
import numpy as np

from langchain_milvus import Milvus
from langchain_core.documents import Document
from langchain_docling import DoclingLoader
from langchain_community.embeddings import OllamaEmbeddings

app = typer.Typer()

embeding_model = "nomic-embed-text"
llm_model = "gpt-oss:20b"


@app.command()
def load():
    """Load and embed documents into Milvus vector store."""
    FILE_PATH = ["pdf/fast21-pan.pdf"]
    loader = DoclingLoader(file_path=FILE_PATH)
    docs = loader.load()
    # Initialize Ollama embeddings with safe wrapper
    embeddings = OllamaEmbeddings(model=embeding_model)
    # Initialize Milvus vector store with embeddings
    vector_store = Milvus(
        embedding_function=embeddings,
        collection_name="document_collection",
        connection_args={"host": "localhost", "port": "19530"}
    )
    # Add documents to the vector store
    vector_store.add_documents(docs)
    print(f"Successfully loaded {len(docs)} documents into Milvus")


@app.command()
def query(query_text: str, k: int = 5):
    """Query the Milvus vector store for similar documents."""
    # Initialize Ollama embeddings with safe wrapper (same as used for loading)
    embeddings = OllamaEmbeddings(model=embeding_model)
    
    # Initialize Milvus vector store connection
    vector_store = Milvus(
        embedding_function=embeddings,
        collection_name="document_collection",
        connection_args={"host": "localhost", "port": "19530"}
    )
    
    # Perform similarity search
    results = vector_store.similarity_search(query_text, k=k)
    
    print(f"Found {len(results)} similar documents for query: '{query_text}'")
    print("-" * 80)
    
    for i, doc in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"Content: {doc.page_content[:200]}...")
        if doc.metadata:
            print(f"Metadata: {doc.metadata}")
        print("-" * 40)


if __name__ == "__main__":
    app()
