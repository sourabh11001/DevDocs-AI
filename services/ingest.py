import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Handling optional dependencies gracefully
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

# -------- Imports from your other optimized files --------
# We use relative imports assuming this runs inside the 'backend' package
# -------- Imports from your other optimized files --------

# CHANGE THIS:
# from .chunking import smart_chunk_text
# from ..models.vector_store import add_documents  <-- THIS CAUSED THE ERROR

# TO THIS (Absolute Imports):
from services.chunking import smart_chunk_text
from models.vector_store import add_documents
# -------- Constants --------
MAX_FILE_CHARS = 500_000  # Increased limit, we handle it via chunking
MAX_WORKERS = min(32, os.cpu_count() + 4)  # Optimal thread count for I/O

EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".idea", ".vscode"
}

SUPPORTED_EXTENSIONS = {
    ".txt": "text", 
    ".pdf": "pdf", 
    ".docx": "docx",
    ".md": "text", 
    ".py": "code", 
    ".js": "code", 
    ".ts": "code",
    ".java": "code",
    ".c": "code",
    ".cpp": "code"
}

# -------- File loaders (Optimized) --------

def load_txt(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(MAX_FILE_CHARS)
    except Exception:
        return ""

def load_pdf(path):
    if not PdfReader:
        print(f"pypdf not installed. Skipping {path}")
        return ""
    try:
        reader = PdfReader(path)
        # Optimized list comprehension is faster than appending in loop
        pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        return "\n\n".join(pages)[:MAX_FILE_CHARS]
    except Exception as e:
        print(f"Error reading PDF {path}: {e}")
        return ""

def load_docx(path):
    if not Document:
        print(f"python-docx not installed. Skipping {path}")
        return ""
    try:
        doc = Document(path)
        return "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])[:MAX_FILE_CHARS]
    except Exception as e:
        print(f"Error reading DOCX {path}: {e}")
        return ""

def load_code(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            # Read all lines at once
            content = f.read(MAX_FILE_CHARS)
            return content
    except Exception:
        return ""

def get_loader(ext):
    if ext == ".pdf": return load_pdf
    if ext == ".docx": return load_docx
    return load_code if ext in [".py", ".js", ".ts", ".c", ".cpp", ".java"] else load_txt

# -------- Main Pipeline --------

def process_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Loads a single file AND chunks it immediately.
    Returns a list of chunk dictionaries ready for the DB.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return []

    loader = get_loader(ext)
    content = loader(file_path)

    if not content or not content.strip():
        return []

    # Chunk the content immediately using our optimized generator
    # We convert the generator to a list here because we need to return data to the thread
    chunks = []
    chunk_generator = smart_chunk_text(content, max_chars=500)
    
    for i, chunk_text in enumerate(chunk_generator):
        chunks.append({
            "path": file_path,
            "chunk_index": i,
            "content": chunk_text,
            "metadata": {"source": file_path, "type": SUPPORTED_EXTENSIONS[ext]}
        })
    
    return chunks

def run_ingestion(folder_path: str):
    """
    Top 1% Feature: Parallel Ingestion Pipeline.
    1. Finds all files.
    2. Reads & Chunks them in parallel (ThreadPool).
    3. Batches them to the Vector Database.
    """
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    # 1. Collect all file paths first (Fast)
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                all_files.append(os.path.join(root, file))

    print(f"Found {len(all_files)} files. Starting ingestion...")

    # 2. Parallel Processing
    # We process files in chunks to avoid holding everything in RAM
    batch_size = 50  # Number of files to process before writing to DB
    current_batch_docs = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all file processing jobs
        future_to_file = {executor.submit(process_file, fp): fp for fp in all_files}

        for future in as_completed(future_to_file):
            try:
                # Get chunks from a single file
                file_chunks = future.result()
                current_batch_docs.extend(file_chunks)

                # 3. Micro-Batch Insert
                # If we have enough chunks, write to DB immediately
                if len(current_batch_docs) >= 100:
                    add_documents(current_batch_docs)
                    print(f"Ingested {len(current_batch_docs)} chunks...")
                    current_batch_docs = []  # Clear memory

            except Exception as e:
                fp = future_to_file[future]
                print(f"Failed to process {fp}: {e}")

    # 4. Final Flush
    if current_batch_docs:
        add_documents(current_batch_docs)
        print(f"Ingested final {len(current_batch_docs)} chunks.")

    print("Ingestion complete.")

# Keeps backward compatibility if you have old code calling this
def load_documents(folder_path: str):
    print("Warning: Use 'run_ingestion' for better performance.")
    # Calls the optimization internally but returns raw format
    # (Not recommended for production, but provided for compatibility)
    pass
