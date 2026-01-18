import chromadb
import os
import uuid
from typing import List, Dict, Any
from models.embeddings import embed_batch
#from .embeddings import embed_batch  # Using our new optimized batch function

DB_PATH = os.path.abspath("db")

# SINGLETON PATTERN: Initialize client once to avoid overhead on every call
_client_instance = None

def get_client():
    """Returns a singleton instance of the PersistentClient."""
    global _client_instance
    if _client_instance is None:
        os.makedirs(DB_PATH, exist_ok=True)
        # Top 1% Tip: Use PersistentClient for stability in production
        _client_instance = chromadb.PersistentClient(path=DB_PATH)
    return _client_instance

def get_collection():
    client = get_client()
    # "get_or_create" is safe and efficient
    return client.get_or_create_collection(name="docs")

# Open models/vector_store.py and REPLACE the add_documents function

def add_documents(docs: List[Dict[str, Any]]):
    """
    Adds documents in BATCHES with safety checks.
    Fixes the 'Number of embeddings must match number of ids' error.
    """
    collection = get_collection()
    
    valid_docs = [doc for doc in docs if doc.get("content", "").strip()]
    if not valid_docs:
        return

    # 1. Prepare Lists
    texts = [doc["content"] for doc in valid_docs]
    metadatas = [{"path": doc["path"]} for doc in valid_docs]
    ids = [str(uuid.uuid4()) for _ in valid_docs]

    # 2. Generate Embeddings (but keep track of failures!)
    # We cannot use the old embed_batch because it swallows errors silently.
    # We must embed one by one to know WHICH one failed, or update embed_batch.
    # For safety on your HDD, we will do a robust loop here.
    
    final_ids = []
    final_texts = []
    final_embeddings = []
    final_metadatas = []

    from .embeddings import embed  # Import single embed function

    for i, text in enumerate(texts):
        try:
            # Generate embedding for THIS specific chunk
            vec = embed(text)
            
            if vec:
                # ONLY if embedding succeeds, add to the final lists
                final_ids.append(ids[i])
                final_texts.append(text)
                final_embeddings.append(vec)
                final_metadatas.append(metadatas[i])
            else:
                print(f"Skipping chunk {i}: Embedding generation returned None.")
                
        except Exception as e:
            print(f"Failed to embed chunk {i}: {e}")

    # 3. Batch Insert (Only the valid ones)
    if final_ids:
        try:
            collection.add(
                ids=final_ids,
                documents=final_texts,
                embeddings=final_embeddings,
                metadatas=final_metadatas
            )
            print(f"Successfully saved {len(final_ids)} chunks to DB.")
        except Exception as e:
            print(f"ChromaDB Insert Error: {e}")
            
def query_vectors(query_text: str, n_results: int = 5):
    """
    Added this helper for rag.py to use later.
    Performs the similarity search.
    """
    from .embeddings import embed
    
    query_vec = embed(query_text)
    if not query_vec:
        return []

    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_vec],
        n_results=n_results
    )
    return results

def reset_db():
    client = get_client()
    try:
        client.delete_collection("docs")
    except Exception:
        pass
    # Re-create immediately so it's ready
    client.get_or_create_collection("docs")

def list_documents():
    """
    Optimized to fetch only metadata if possible, 
    though Chroma's basic API fetches all. 
    """
    collection = get_collection()
    # get(include=[...]) optimizes by NOT fetching the heavy embeddings vector data
    data = collection.get(include=["metadatas"])

    counts = {}
    if data and "metadatas" in data:
        for meta in data["metadatas"]:
            path = meta.get("path", "unknown")
            counts[path] = counts.get(path, 0) + 1

    return [{"path": k, "chunks": v} for k, v in counts.items()]
