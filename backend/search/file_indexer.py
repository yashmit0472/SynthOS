import os
import logging
from backend.memory.vector_store import vector_store

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {'.txt', '.md', '.json'}

def index_directory(directory=None):
    """Scans a directory and indexes supported files into ChromaDB."""
    if directory is None:
        directory = os.path.expanduser("~/Documents")
        
    if not os.path.exists(directory):
        logger.warning(f"Directory {directory} does not exist.")
        return 0
        
    documents = []
    metadatas = []
    ids = []
    
    logger.info(f"Scanning directory {directory} for indexing...")
    try:
        for root, dirs, files in os.walk(directory):
            # Skip hidden and system folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'AppData']]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        if content.strip():
                            documents.append(content)
                            metadatas.append({"filename": file, "path": filepath})
                            ids.append(filepath)
                    except Exception as e:
                        pass
    except Exception as e:
        logger.error(f"Error during indexing {directory}: {e}")
        
    if documents:
        # ChromaDB can usually handle batches, but we keep it simple here
        vector_store.add_documents(ids, documents, metadatas)
        logger.info(f"Successfully indexed {len(documents)} files.")
        return len(documents)
    else:
        logger.info("No new files to index.")
        return 0
