import re
from typing import Dict, List

from dotenv import load_dotenv

load_dotenv()


def clean_transcript(text: str) -> str:
    # 1. Collapse multiple spaces/newlines into a single space
    text = re.sub(r"\s+", " ", text).strip()

    # 2. Remove everything inside square brackets (and the brackets)
    #    Examples: [music]  [Applause]  [inaudible 00:12]  → gone
    text = re.sub(r"\[[^\]]*\]", "", text)

    # 3. Remove repeated single words (stutters): "I I I really" → "I really"
    #    (\w+)   = capture one word
    #    ( \1)+  = one or more repetitions of " space + the same word"
    #    r'\1'   = replace the whole match with just the first captured word
    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text, flags=re.IGNORECASE)

    # 4 remove all >>
    text = re.sub(r">>", "", text)

    # 5. Remove common fillers (add/remove patterns as you like)
    fillers = [
        r"\bi mean\b",
        r"\byou know\b",
        r"\bum+\b",
        r"\buh+\b",
        r"\ber+\b",
        r"\bah+\b",
        r"\bkind of\b",
        r"\bkinda\b",
        r"\bsort of\b",
        r"\bsorta\b",
        r"\bbasically\b",
        r"\bactually\b",
        r"\bokay\b",
        r"\bok\b",
        r"\byeah\b",
        r"\bsounds good\b",
    ]
    for pattern in fillers:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 6. Remove common greetings and goodbyes (flexible patterns)
    greetings_goodbyes = [
        # Openings
        r"\b(hey|hi|hello|good morning|good afternoon|good evening) (everyone|everybody|guys|folks|all)?\b",
        r"\bwelcome back\b",
        r"\bthanks for (joining|tuning in|watching)\b",
        r"\bladies and gentlem[ae]n\b",
        # Closings
        r"\b(see you|catch you) (all |guys |folks )?(later|next time|soon|tomorrow)\b",
        r"\b(that\'?s|that is) (it|all) for (today|now|this (one|episode|video))\b",
        r"\b(alright|okay|ok),? (that\'?s|that is) (it|all)\b",
        r"\bthanks for (watching|listening|tuning in)\b",
        r"\buntil next time\b",
        r"\bsee you guys all next time\b",
        r"\btake care\b",
        r"\bbye[\s,]*bye\b",
        r"\bgoodbye\b",
    ]
    for pattern in greetings_goodbyes:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 7. === FIX LONELY / LEFTOVER PUNCTUATION ===
    #    Remove comma/period/etc. that are now sitting alone at the start
    #    or after another space
    text = re.sub(r"(^|\s)[,:;]+", r"\1", text)  # leading ", insane" → " insane"
    text = re.sub(r"[,:;]+(\s|$)", r"\1", text)  # trailing "earnings ," → "earnings "

    # 8. Clean up spaces around remaining punctuation
    #    "word , word" → "word, word"
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)

    # 9. Collapse multiple punctuation marks: "!!" or ",," → single
    text = re.sub(r"([,.!?;:]){2,}", r"\1", text)

    # 10. Final space cleanup
    text = re.sub(r"\s{2,}", " ", text).strip()

    # with open("cleared_chunks.txt", "a") as file:
    # file.write(text + "\n")
    return text


def chunk_by_sentences(
    raw_transcript: str, max_chunk_size: int = 1000, overlap_sentences: int = 2
) -> List[Dict]:
    """
    Chunk cleaned transcript by sentences with configurable overlap.
    """
    cleaned_transcript = clean_transcript(raw_transcript)

    sentences = re.split(r"(?<=[.!?])\s+", cleaned_transcript.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    chunk_id = 0

    i = 0
    while i < len(sentences):
        current_chunk = []
        current_length = 0

        # Build current chunk
        j = i
        while j < len(sentences):
            sentence = sentences[j]
            new_length = current_length + len(sentence) + 1  # +1 for space

            if (
                new_length > max_chunk_size and current_chunk
            ):  # Don't create empty chunk
                break

            current_chunk.append(sentence)
            current_length = new_length
            j += 1

        # Create chunk
        chunk_text = " ".join(current_chunk)

        chunks.append(
            {
                "id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_text.split()),
                    "sentence_count": len(current_chunk),
                    "start_sentence_idx": i,
                    "end_sentence_idx": j - 1,
                },
            }
        )

        chunk_id += 1

        # Move forward with overlap
        if overlap_sentences > 0:
            i += max(1, len(current_chunk) - overlap_sentences)
        else:
            i = j  # No overlap

    return chunks[:-2]
