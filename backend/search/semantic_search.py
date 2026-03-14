import logging
from backend.memory.vector_store import vector_store

logger = logging.getLogger(__name__)

def perform_semantic_search(query):
    """Queries ChromaDB for semantically similar files."""
    try:
        results = vector_store.query_documents(query_texts=[query], n_results=3)
        
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
