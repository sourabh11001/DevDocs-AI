import ollama
from typing import Dict, Any, List

# Import our optimized helper to keep code DRY (Don't Repeat Yourself)
#from .vector_store import query_vectors
from models.vector_store import query_vectors, get_collection
from models.embeddings import embed
# Initialize AsyncClient for non-blocking operations
# This allows handling multiple user requests simultaneously
client = ollama.AsyncClient()

#GENERATION_MODEL = "qwen2.5:3b"
GENERATION_MODEL = "qwen2.5:0.5b"
async def ask(query: str) -> Dict[str, Any]:
    """
    Retrieves context and generates an answer asynchronously.
    Top 1% Improvement: Non-blocking I/O allows high concurrency.
    """
    if not query.strip():
        return {"answer": "Please ask a question.", "sources": []}

    # 1. Retrieve Context (using our optimized vector store helper)
    # Note: Vector search is usually CPU bound/fast, so sync is often okay,
    # but strictly we could wrap it in a thread if the DB is huge. 
    # For now, the direct call is fine.
    results = query_vectors(query, n_results=3)

    # Handle empty results safely
    if not results or not results["documents"] or not results["documents"][0]:
        return {"answer": "I don't know based on the available documents.", "sources": []}

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    # 2. Construct Prompt (Senior Dev Improvement)
    # We use explicit XML-style tags <context> to prevent the model 
    # from confusing instructions with data.
    formatted_context = "\n\n".join(
        [f"<doc id='{i}'>{doc}</doc>" for i, doc in enumerate(docs)]
    )

    system_prompt = (
        "You are a precise assistant. Use ONLY the provided Context to answer the Question. "
        "If the answer is not found in the Context, explicitly say 'I don't know'. "
        "Do not hallucinate or use outside knowledge."
    )

    user_prompt = f"""
Context:
{formatted_context}

Question: 
{query}
"""

    try:
        # 3. Asynchronous Generation
        # The 'await' keyword yields control back to the event loop
        # while waiting for Ollama to respond.
        response = await client.generate(
            model=GENERATION_MODEL,
            system=system_prompt,  # Use system parameter for better instruction following
            prompt=user_prompt,
            options={
                "temperature": 0.1,  # Low temp for factual RAG answers
                "num_ctx": 4096      # Ensure context window is large enough
            }
        )

        return {
            "answer": response["response"].strip(),
            "sources": metas
        }

    except Exception as e:
        print(f"LLM Generation Error: {e}")
        return {
            "answer": "An error occurred while generating the answer.",
            "sources": []
        }
