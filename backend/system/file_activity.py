import os
import glob
import time
import logging

logger = logging.getLogger(__name__)

def get_recently_modified_files(directory, max_files=5, days=1):
    """Returns files modified within the last N days in a directory."""
    recent_files = []
    now = time.time()
    cutoff_time = now - (days * 86400)
    
    # Very basic recursive search, ignoring hidden dirs/files
    try:
        # Use a more targeted approach rather than walking entire C drive
        for root, dirs, files in os.walk(directory):
            # Skip common heavy/irrelevant folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'AppData']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                filepath = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(filepath)
                    if mtime > cutoff_time:
                        recent_files.append({
                            "path": filepath,
                            "name": file,
                            "mtime": mtime
                        })
                except (OSError, FileNotFoundError):
                    pass
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")
        
    # Sort by most recently modified
    recent_files = sorted(recent_files, key=lambda x: x["mtime"], reverse=True)
    return recent_files[:max_files]

def analyze_recent_activity(directory=None):
    """Returns an insight string about recently edited files."""
    if directory is None:
        # Default to Documents folder on Windows
        directory = os.path.expanduser("~/Documents")
        
    if not os.path.exists(directory):
        return None
        
    recent = get_recently_modified_files(directory, max_files=2, days=1)
    
    if recent:
        names = [f["name"] for f in recent]
        insight = f"You recently edited {', '.join(names)}. Continue working on them?"
        return insight
        
    return None
