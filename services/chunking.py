import re
from typing import Generator

def smart_chunk_text(
    text: str, 
    max_chars: int = 1500, 
    overlap_paragraphs: int = 1
) -> Generator[str, None, None]:
    """
    Paragraph-aware chunking that respects word boundaries even for huge paragraphs.
    Top 1% Improvement: Uses generators and recursive safe-splitting.
    """
    if not text:
        return

    # Normalize excessive newlines to ensure clean paragraph separation
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    current_paras = []
    current_length = 0

    for para in paragraphs:
        para_len = len(para)

        # CASE 1: The single paragraph is HUGE (bigger than max_chars)
        # We must split this specific paragraph safely.
        if para_len > max_chars:
            # First, flush whatever we have in the buffer
            if current_paras:
                yield "\n\n".join(current_paras)
                current_paras = []
                current_length = 0
            
            # Now split the huge paragraph using a helper that respects words
            # (Logic adapted from our previous safe chunker)
            start = 0
            while start < para_len:
                end = start + max_chars
                if end < para_len:
                    # Find last space to avoid cutting words
                    last_space = para.rfind(" ", start, end)
                    if last_space != -1 and last_space > start + (max_chars * 0.5):
                        end = last_space + 1
                
                sub_chunk = para[start:end].strip()
                if sub_chunk:
                    yield sub_chunk
                
                # For huge paragraphs, we don't do complex overlap logic, 
                # we just ensure we move forward safely.
                start = end
            continue

        # CASE 2: Standard Paragraph Accumulation
        # Check if adding this paragraph exceeds the limit
        # We add 2 chars for the "\n\n" separator
        added_len = para_len + (2 if current_paras else 0)

        if current_length + added_len > max_chars:
            # Yield current buffer
            yield "\n\n".join(current_paras)

            # Handle Overlap: Keep the last N paragraphs for context
            if overlap_paragraphs > 0:
                current_paras = current_paras[-overlap_paragraphs:]
                # Recalculate length (expensive but necessary for accuracy)
                current_length = sum(len(p) for p in current_paras) + (2 * (len(current_paras) - 1)) if current_paras else 0
            else:
                current_paras = []
                current_length = 0

        current_paras.append(para)
        current_length += len(para) + (2 if len(current_paras) > 1 else 0)

    # Flush any remaining text
    if current_paras:
        yield "\n\n".join(current_paras)
