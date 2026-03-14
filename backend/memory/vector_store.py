import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="nexis_files")
        
    def add_documents(self, ids, documents, metadatas=None):
        logger.info(f"Adding {len(documents)} documents to ChromaDB.")
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query_documents(self, query_texts, n_results=3):
        logger.info(f"Querying ChromaDB for: {query_texts}")
        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results
        )
        return results

vector_store = VectorStore()
