"""
Benchmark Mode: compares cloud-only cost vs your hybrid ASNE router
across a fixed set of test queries. Run after the server is up.

Usage: python benchmark.py
"""
import requests
import time

API_URL = "http://localhost:8000/query"

# Mix of simple, domain, and complex queries -- edit/expand this list
# with real questions from your SPPU PYQ material.
TEST_QUERIES = [
    "hello",
    "what is 5 + 7",
    "define oop",
    "what are the types of virtualization in cloud computing",
    "explain HDFS architecture in big data",
    "what is the difference between BFS and DFS with example",
    "explain REST API design principles with example",
    "compare IaaS PaaS and SaaS with real world examples and tradeoffs",
]


def run_benchmark():
    total_cost = 0.0
    total_latency = 0.0
    route_counts = {}

    print(f"{'Query':<55} {'Route':<25} {'Conf':<6} {'Latency':<9} {'Cost'}")
    print("-" * 110)

    for query in TEST_QUERIES:
        start = time.time()
        resp = requests.post(API_URL, json={"query": query}, timeout=120)
        data = resp.json()
        elapsed = round(time.time() - start, 3)

        route = data["route"]
        route_counts[route] = route_counts.get(route, 0) + 1
        total_cost += data["cost_usd"]
        total_latency += elapsed

        print(f"{query[:53]:<55} {route:<25} {data['confidence']:<6} "
              f"{elapsed:<9} ${data['cost_usd']}")

    print("-" * 110)
    print(f"\nTotal queries: {len(TEST_QUERIES)}")
    print(f"Total cost (hybrid router): ${round(total_cost, 6)}")
    print(f"Average latency: {round(total_latency / len(TEST_QUERIES), 3)}s")
    print(f"Route distribution: {route_counts}")

    # Anything that isn't a rule/cache/fast-tier hit counts as an
    # escalation (Claude or the free Groq-premium fallback).
    free_routes = ("rule_engine", "semantic_cache", "fast_tier_model")
    escalated = sum(
        count for route, count in route_counts.items()
        if not route.startswith(free_routes)
    )
    escalation_pct = escalated / len(TEST_QUERIES) * 100
    print(f"\n% of queries that needed escalation (paid or premium tier): {escalation_pct:.1f}%")
    print(f"=> Roughly {100 - escalation_pct:.1f}% of queries handled free "
          f"(rules/cache/fast-tier), vs a cloud-only baseline")


if __name__ == "__main__":
    run_benchmark()
