# 🧠 DevDocs AI  
_Your personal ChatGPT for local documents._

> Chat with your own documents locally using AI.

DevDocs AI is a fully offline, privacy-first **RAG (Retrieval-Augmented Generation)** system that lets you index your documents and ask questions in a ChatGPT-style interface.

It allows you to interact with:
- 📄 PDF files  
- 📝 TXT and Markdown files  
- 💻 Code files (.py, .js, .ts, etc.)  
- 📚 Multiple documents inside one folder  

Everything runs **locally** on your machine using:
- **Ollama** for embeddings and LLM inference  
- **ChromaDB** for vector storage  
- **FastAPI** for the backend  
- A lightweight **HTML frontend** that looks and behaves like ChatGPT  

No cloud. No data sharing. 100% private.

---

## 🚀 Features

- ChatGPT-style UI  
- Local document indexing  
- PDF + text + code support  
- Smart chunking of documents  
- Fast semantic vector search  
- Spinner animation while AI is thinking  
- Sidebar for document indexing  
- Source-aware answers  
- Fully offline & privacy-first design  

---

## 🏗 Architecture

```
Frontend (HTML UI)
        ↓
FastAPI Backend
        ↓
ChromaDB (Vector Store)
        ↓
Ollama (Embeddings + LLM)
```

This architecture represents a real-world **RAG pipeline** used in production-grade GenAI systems.

---

## 📦 Requirements

- Python 3.10+  
- Ollama installed locally  

Pull required models:

```bash
ollama pull nomic-embed-text
ollama pull qwen2.5:3b
```

---

## 🛠 Installation

Clone the repository:

```bash
git clone <your-repo-url>
cd backend
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend server:

```bash
uvicorn app:app --reload
```

Open the UI:

Just open `index.html` in your browser.

---

## 🧪 Usage

1. Open the UI  
2. Enter your document folder path:

```
/home/yourname/Documents/docs
```

3. Click **Index Now**  
4. Sidebar collapses automatically  
5. Start asking questions in the chat  

---

## 🧠 Example Questions

- “What is this document about?”  
- “Explain the main topic”  
- “Summarize page 2”  
- “What libraries are used in this code?”  
- “What is the conclusion?”  

---

## 🔒 Privacy

All processing happens locally:

- No internet calls  
- No API keys  
- No cloud servers  
- Your documents never leave your machine  

This is true **local-first AI**.

---

## 📈 Why this project is powerful

This project demonstrates:

- Real **RAG architecture**  
- **LLM integration** using Ollama  
- **Vector database design** using ChromaDB  
- Backend engineering with FastAPI  
- UI/UX thinking similar to ChatGPT  
- Debugging and system-level thinking  

This is not a tutorial project.  
This is **production-style GenAI engineering**.

---

## 🧑‍💻 Author

**Sourabh Bhimagonda Kagilkar**  
GenAI Developer | Data Analyst | Python Engineer  

---

## ⭐ Final Note

This is not a toy project.  
This is a **real GenAI system** built from scratch.

If you are learning RAG, embeddings, or local LLM deployment, this project is a perfect reference implementation.
