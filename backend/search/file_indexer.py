import os
import logging
import docx
from pypdf import PdfReader
from backend.memory.vector_store import vector_store
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {'.txt', '.md', '.json', '.pdf', '.docx'}

logger.info("Initializing Indexer SentenceTransformer model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext in ['.txt', '.md', '.json']:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
                
        elif ext == ".pdf":
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages[:10]:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
            
        elif ext == ".docx":
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs[:200]])
            
    except Exception as e:
        logger.warning(f"Could not extract text from {file_path}: {e}")
        
    return ""

def get_target_directories():
    """Returns a list of common Windows user directories."""
    user_profile = os.environ.get('USERPROFILE')
    onedrive = os.environ.get('OneDrive')
    
    dirs = []
    if user_profile:
        dirs.extend([
            os.path.join(user_profile, "Documents"),
            os.path.join(user_profile, "Desktop"),
            os.path.join(user_profile, "Downloads")
        ])
    if onedrive:
        dirs.append(onedrive)
        
    return [d for d in dirs if os.path.exists(d)]

def index_all_folders():
    """Automatically finds specific user directories and indexes them."""
    target_dirs = get_target_directories()
    total_indexed = 0
    
    for directory in target_dirs:
        total_indexed += index_directory(directory)
        
    return total_indexed

def index_directory(directory):
    """Scans a directory and indexes supported files into ChromaDB using explicit embeddings."""
    if not os.path.exists(directory):
        return 0
        
    documents = []
    metadatas = []
    ids = []
    
    logger.info(f"Scanning directory {directory} for indexing...")
    try:
        # Prevent walking too deeply into huge hierarchies
        for root, dirs, files in os.walk(directory):
            # Prune hidden/system/dev folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'AppData', 'Local Settings']]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    filepath = os.path.join(root, file)
                    
                    text = extract_text(filepath)
                    if not text or len(text.strip()) < 20:
                        continue
                        
                    # Truncate text to avoid model blowing chunks on 10,000 token PDFs
                    text = text[:8000]
                        
                    documents.append(text)
                    metadatas.append({"filename": file, "path": filepath})
                    ids.append(filepath)
                    
            # Batch add every 50 docs to prevent OOM
            if len(documents) >= 50:
                embeddings = embedder.encode(documents).tolist()
                vector_store.add_documents(ids, documents, embeddings=embeddings, metadatas=metadatas)
                logger.info(f"Indexed batch of {len(documents)} files from {directory}...")
                documents = []
                metadatas = []
                ids = []
                
    except Exception as e:
        logger.error(f"Error walking {directory}: {e}")
        
    # Add any remaining
    if documents:
        embeddings = embedder.encode(documents).tolist()
        vector_store.add_documents(ids, documents, embeddings=embeddings, metadatas=metadatas)
        logger.info(f"Indexed final batch of {len(documents)} files from {directory}.")
        return len(documents)
        
    return 0
