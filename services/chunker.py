from typing import Generator

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> Generator[str, None, None]:
    """
    Splits text into chunks while respecting word boundaries.
    Top 1% Improvement: Uses generators for memory efficiency and 
    adjusts split points to avoid cutting words in half.
    """
    if not text:
        return
    
    # Safety check to prevent infinite loops
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        
        # Performance/Accuracy Fix: 
        # If we are not at the end of the text, try not to slice in the middle of a word.
        if end < text_len:
            # Look for the last space within the chunk to split safely
            # We search backwards from the 'end' point
            last_space = text.rfind(" ", start, end)
            
            # If a space is found (and it's not too far back, e.g., >50% of chunk), use it.
            # This ensures we don't shrink chunks too much if there are no spaces (like a long URL).
            if last_space != -1 and last_space > start + (chunk_size * 0.5):
                end = last_space + 1  # Include the space in this chunk

        # Extract the chunk
        chunk = text[start:end]
        
        # Use yield instead of appending to a list (Saves RAM)
        yield chunk

        # Move the pointer
        # We advance by the actual length of the chunk minus the overlap
        start += (len(chunk) - overlap)
