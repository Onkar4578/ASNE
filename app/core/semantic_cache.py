"""
Level 2: Semantic Cache (lightweight version for free-tier deployment)
Uses TF-IDF + cosine similarity instead of sentence-transformers/torch.
This avoids heavy model downloads (~500MB+) that break free-tier RAM limits
on Render/Railway/etc. Trade-off: slightly less accurate than embeddings,
but real, free, and deployable.

NOTE: cache_store.json is written to local disk. On Render's free tier,
disk is ephemeral -- it resets on redeploy/restart. Fine for a demo;
for persistence across restarts, swap this for a free Render Postgres
or a free Redis instance later.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

CACHE_FILE = "cache_store.json"
SIMILARITY_THRESHOLD = 0.55  # tune based on testing; TF-IDF scores run lower than embeddings


def _load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []  # list of {"query": str, "response": str}


def _save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def check_cache(query: str):
    """
    Returns cached response if a similar-enough query exists, else None.
    Fits TF-IDF jointly over cached queries + new query (cheap at small scale).
    """
    cache = _load_cache()
    if not cache:
        return None

    corpus = [entry["query"] for entry in cache] + [query]
    vectorizer = TfidfVectorizer().fit(corpus)
    vectors = vectorizer.transform(corpus)

    query_vec = vectors[-1]
    cached_vecs = vectors[:-1]
    scores = cosine_similarity(query_vec, cached_vecs)[0]

    best_idx = scores.argmax()
    best_score = scores[best_idx]

    if best_score >= SIMILARITY_THRESHOLD:
        return cache[best_idx]["response"]
    return None


def add_to_cache(query: str, response: str):
    cache = _load_cache()
    cache.append({"query": query, "response": response})
    _save_cache(cache)
