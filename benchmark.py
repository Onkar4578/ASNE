"""
Benchmark Mode: compares your hybrid ASNE router against a rough cloud-only cost
estimate and reports route distribution, latency, and escalation frequency.
Run after the server is up.

Usage: python benchmark.py
"""
import os
import requests
import time

API_URL = os.environ.get("ASNE_API_URL", "https://asne-1.onrender.com/query")

# Mix of simple, domain, and complex queries -- edit/expand this list
# with real questions from your SPPU PYQ material.
TEST_QUERIES = [
    # --- Level 1: Rule engine matches (instant, free) ---
    "hello",
    "define oop",
    "full form of dbms",
    "full form of http",
    "what is 12 + 8",

    # --- Level 2: Cache test (exact repeat of an earlier query) ---
    "define oop",

    # --- Web Technology (SPPU) ---
    "explain the difference between GET and POST HTTP methods",
    "what is the role of session management in web applications",
    "explain REST API design principles with an example",

    # --- Artificial Intelligence (SPPU) ---
    "explain BFS and DFS with a real world example",
    "what is a heuristic function in AI search algorithms",
    "explain the difference between supervised and unsupervised learning",

    # --- Cloud Computing (SPPU) ---
    "explain the difference between IaaS PaaS and SaaS with examples",
    "what are the types of virtualization in cloud computing",
    "explain load balancing in cloud infrastructure",

    # --- Data Science / Big Data (SPPU) ---
    "explain the HDFS architecture in big data",
    "what is the role of MapReduce in Hadoop",
    "explain data preprocessing steps in a machine learning pipeline",

    # --- General (non-SPPU) queries ---
    "write a short professional bio for a LinkedIn profile",
    "explain how photosynthesis works",
    "what are some tips for staying focused while studying",

    # --- Deliberately hard/ambiguous (likely to need escalation) ---
    "Design a distributed consensus algorithm that tolerates Byzantine faults in a 7-node cluster, and prove its correctness under network partitions",
    "Critically compare three cache eviction strategies for a system handling 10 million requests per second and recommend one with justification",
    "What is the exact closing stock price of Tesla on July 3rd 2026, down to the cent?",
    "Explain the trade-offs between CAP theorem choices for a globally distributed banking system, with a recommendation",

    # --- Ambiguous / conversational (tests general fallback + confidence) ---
    "can you help me plan my exam study schedule for next week",
    "what's the difference between a good and a great software engineer",
]


def run_benchmark():
    total_cost = 0.0
    total_latency = 0.0
    route_counts = {}

    print(f"{'Query':<55} {'Route':<35} {'Conf':<6} {'Latency':<9} {'Cost'}")
    print("-" * 120)

    for query in TEST_QUERIES:
        start = time.time()
        resp = requests.post(API_URL, json={"query": query}, timeout=120)
        data = resp.json()
        elapsed = round(time.time() - start, 3)

        route = data["route"]
        route_counts[route] = route_counts.get(route, 0) + 1
        total_cost += data["cost_usd"]
        total_latency += elapsed

        print(f"{query[:53]:<55} {route:<35} {data['confidence']:<6} "
              f"{elapsed:<9} ${data['cost_usd']}")

    print("-" * 120)
    print(f"\nUsing API endpoint: {API_URL}")
    print(f"Total queries: {len(TEST_QUERIES)}")
    print(f"Total cost (hybrid router): ${round(total_cost, 6)}")
    print(f"Average latency: {round(total_latency / len(TEST_QUERIES), 3)}s")
    print("Route distribution:")
    for route, count in sorted(route_counts.items(), key=lambda item: -item[1]):
        print(f"  {route:<45} {count}")

    free_routes = ("rule_engine", "semantic_cache", "fast_tier_model")
    escalated_count = sum(
        count for route, count in route_counts.items()
        if not route.startswith(free_routes)
    )
    escalation_pct = escalated_count / len(TEST_QUERIES) * 100
    print(f"\n% of queries that needed escalation (paid or premium tier): {escalation_pct:.1f}%")
    print(f"% handled free by rules/cache/fast-tier: {100 - escalation_pct:.1f}%")

    if escalated_count > 0:
        avg_escalated_cost = total_cost / escalated_count
        estimated_cloud_only_cost = avg_escalated_cost * len(TEST_QUERIES)
        savings_pct = 100 * (estimated_cloud_only_cost - total_cost) / estimated_cloud_only_cost
        print(f"Estimated hybrid savings vs cloud-only at the average escalated query cost: {savings_pct:.1f}%")
        print(f"Average cost per escalated query: ${round(avg_escalated_cost, 6)}")
    else:
        print("No escalations observed, so the hybrid path is fully free in this run.")


if __name__ == "__main__":
    run_benchmark()
