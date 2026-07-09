"""
Level 2.5: Domain Classifier (single-domain, lightweight)
Uses TF-IDF similarity against ONE combined SPPU seed set -- no
torch/transformer download needed, keeping this deployable on
free-tier hosting. Simplified from an earlier 4-subject version so
it's easier to explain in an interview and faster to demo end-to-end.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

DOMAIN_THRESHOLD = 0.2  # TF-IDF scores run lower than embedding similarity; tune with testing

# One combined seed set spanning your SPPU subjects.
# Expand this list using real topics from your PYQ PDFs for better accuracy.
SPPU_SEEDS = [
    "HTTP methods GET POST request response REST API session management web technology",
    "search algorithms BFS DFS heuristic expert systems artificial intelligence neural networks",
    "virtualization hypervisor IaaS PaaS SaaS cloud computing deployment models load balancing",
    "Hadoop MapReduce HDFS big data analytics data preprocessing data science",
    "SPPU exam question syllabus computer engineering subject unit",
]


def classify_domain(query: str):
    """
    Returns (domain_name, confidence_score).
    domain_name is "sppu" if similarity is high enough, else "general".
    """
    corpus = SPPU_SEEDS + [query]
    vectorizer = TfidfVectorizer().fit(corpus)
    vectors = vectorizer.transform(corpus)

    query_vec = vectors[-1]
    seed_vecs = vectors[:-1]
    scores = cosine_similarity(query_vec, seed_vecs)[0]
    best_score = float(np.max(scores))

    if best_score < DOMAIN_THRESHOLD:
        return "general", best_score
    return "sppu", best_score
