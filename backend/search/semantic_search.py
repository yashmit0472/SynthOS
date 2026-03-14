import logging
from backend.memory.vector_store import vector_store
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Load model once on startup
logger.info("Loading SentenceTransformer model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def perform_semantic_search(query):
    """Queries ChromaDB for semantically similar files using explicit embeddings."""
    try:
        query_embedding = embedder.encode(query).tolist()
        results = vector_store.query_documents(query_embeddings=[query_embedding], n_results=1)
        
        matches = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            
            for doc, meta in zip(docs, metas):
                matches.append({
                    "filename": meta.get("filename", "Unknown"),
                    "path": meta.get("path", "Unknown"),
                    "snippet": doc[:200] + "..." if len(doc) > 200 else doc
                })
                
        return {"query": query, "results": matches}
    except Exception as e:
        logger.error(f"Error during semantic search: {e}")
        return {"error": "Failed to perform semantic search."}
