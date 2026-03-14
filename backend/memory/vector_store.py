import chromadb
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="nexis_files")
        
    def add_documents(self, ids, documents, embeddings=None, metadatas=None):
        logger.info(f"Adding {len(documents)} documents to ChromaDB.")
        kwargs = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas
        }
        if embeddings is not None:
            kwargs["embeddings"] = embeddings
            
        self.collection.add(**kwargs)

    def query_documents(self, query_texts=None, query_embeddings=None, n_results=3):
        kwargs = {"n_results": n_results}
        if query_embeddings is not None:
            kwargs["query_embeddings"] = query_embeddings
        elif query_texts is not None:
            kwargs["query_texts"] = query_texts
            logger.info(f"Querying ChromaDB for text(s): {query_texts}")
            
        results = self.collection.query(**kwargs)
        return results

vector_store = VectorStore()
