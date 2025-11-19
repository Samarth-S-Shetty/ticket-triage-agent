# kb/search.py
import json
import os
import time
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Try to import OpenAI client if key exists
client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        client = None

ROOT = Path(__file__).resolve().parent
KB_PATH = ROOT / "kb.json"
EMBED_CACHE_PATH = ROOT / "embeddings.json"

# Load KB
def load_kb() -> List[Dict[str, Any]]:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

KB = load_kb()


# -------------------- Utilities --------------------

def dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))

def norm(a: List[float]) -> float:
    s = sum(x * x for x in a)
    return s ** 0.5 if s > 0 else 0.0

def cosine_similarity(a: List[float], b: List[float]) -> float:
    na = norm(a)
    nb = norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot(a, b) / (na * nb)


# -------------------- Embedding cache / helpers --------------------

def load_embedding_cache() -> Dict[str, List[float]]:
    if EMBED_CACHE_PATH.exists():
        try:
            with open(EMBED_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_embedding_cache(cache: Dict[str, List[float]]) -> None:
    try:
        with open(EMBED_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception:
        pass  # ignore disk write issues


def make_kb_text(entry: Dict[str, Any]) -> str:
    symptoms = entry.get("symptoms", [])
    if isinstance(symptoms, list):
        symptoms_text = " ".join(symptoms)
    else:
        symptoms_text = str(symptoms)
    return f"{entry.get('title', '')}. {symptoms_text}"


# -------------------- Embedding generation --------------------

def get_embedding_for_text(text: str) -> List[float]:
    """
    Returns embedding vector for text using OpenAI embeddings API.
    Raises exception if client is None or API call fails.
    """
    if client is None:
        raise RuntimeError("OpenAI client not configured")

    # Defensive: handle short text quickly
    # Call embedding API (batch single input)
    resp = client.embeddings.create(model="text-embedding-3-small", input=[text])
    # Try to extract embedding robustly
    try:
        emb = resp.data[0].embedding
        return emb
    except Exception:
        # fallback: try alt field shapes
        try:
            return resp["data"][0]["embedding"]
        except Exception as e:
            raise RuntimeError(f"Could not extract embedding: {e}")


# -------------------- Fallback simple keyword score --------------------

def keyword_score(description: str, symptoms: List[str]) -> float:
    desc_words = set(description.lower().split())
    symptom_words = set()
    for s in symptoms:
        symptom_words.update(str(s).lower().split())
    if not symptom_words:
        return 0.0
    overlap = len(desc_words.intersection(symptom_words))
    return overlap / (len(symptom_words) or 1)


# -------------------- Main search (embeddings) --------------------

def build_or_load_kb_embeddings() -> Dict[str, List[float]]:
    """
    Returns a mapping key -> embedding vector for each KB entry.
    Key chosen: entry['id']
    Caches to disk in kb/embeddings.json to avoid repeated API calls.
    """
    cache = load_embedding_cache()

    need_save = False
    for entry in KB:
        eid = entry.get("id")
        if not eid:
            continue
        if eid in cache and isinstance(cache[eid], list) and len(cache[eid]) > 0:
            continue  # already cached
        # Compute embedding for this KB entry text
        text = make_kb_text(entry)
        try:
            emb = get_embedding_for_text(text)
            cache[eid] = emb
            need_save = True
            # Be polite to API
            time.sleep(0.1)
        except Exception:
            # If embedding fails, leave out of cache (will fallback to keyword)
            cache[eid] = []  # placeholder empty vector
            need_save = True

    if need_save:
        save_embedding_cache(cache)
    return cache


def search_kb(description: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Main entry: returns top_k KB matches sorted by cosine similarity.
    If OpenAI key present, uses embeddings; otherwise falls back to keyword_score.
    """
    results = []
    desc = description.strip()

    if client:
        # Build or load KB embeddings (cached)
        kb_emb_cache = build_or_load_kb_embeddings()
        # Compute embedding for incoming description
        try:
            desc_emb = get_embedding_for_text(desc)
        except Exception:
            # Embedding call failed -> fallback to keyword scoring for all entries
            desc_emb = None

        for entry in KB:
            eid = entry.get("id")
            score = 0.0
            if desc_emb and kb_emb_cache.get(eid):
                kb_vec = kb_emb_cache.get(eid)
                # skip empty placeholder vectors
                if isinstance(kb_vec, list) and len(kb_vec) > 0:
                    score = cosine_similarity(desc_emb, kb_vec)
                else:
                    score = 0.0
            else:
                # fallback
                score = keyword_score(desc, entry.get("symptoms", []))

            results.append({
                "id": eid,
                "title": entry.get("title"),
                "score": float(round(score, 4)),
                "recommended_action": entry.get("recommended_action")
            })

    else:
        # No OpenAI client -> use keyword scoring
        for entry in KB:
            score = keyword_score(desc, entry.get("symptoms", []))
            results.append({
                "id": entry.get("id"),
                "title": entry.get("title"),
                "score": float(round(score, 4)),
                "recommended_action": entry.get("recommended_action")
            })

    # Sort and return top_k
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:top_k]
