"""
The Orchestrator: ties together Rule Engine -> Cache -> Domain Classifier
-> Fast Tier Model (Groq, free) -> Confidence Check -> Cloud Escalation (Claude, paid).
Returns an explainable response showing exactly which layer handled it.

This version is deployment-safe: no local processes, no heavy ML downloads,
works identically on your laptop and on Render/Railway/etc.
"""
import time
from app.core import rule_engine, semantic_cache, domain_classifier, fast_tier_model, cloud_model

CONFIDENCE_ESCALATION_THRESHOLD = 60  # below this, escalate to cloud
COMPLEXITY_LENGTH_THRESHOLD = 120  # characters above this are treated as more complex
COMPLEXITY_KEYWORDS = [
    "prove",
    "design",
    "critically evaluate",
    "compare",
    "justify",
    "trade-off",
    "tradeoffs",
    "analysis",
    "security",
    "protocol",
]


def handle_query(query: str) -> dict:
    start_time = time.time()

    # ---- Level 1: Rule Engine ----
    rule_response = rule_engine.match_rule(query)
    if rule_response:
        return _build_response(
            answer=rule_response,
            route="rule_engine",
            confidence=100,
            cost=0.0,
            start_time=start_time,
            reason="Matched a predefined rule pattern.",
        )

    # ---- Level 2: Semantic Cache ----
    cached_response = semantic_cache.check_cache(query)
    if cached_response:
        return _build_response(
            answer=cached_response,
            route="semantic_cache",
            confidence=100,
            cost=0.0,
            start_time=start_time,
            reason="Found a similar past query in cache.",
        )

    # ---- Level 2.5: Domain Classification ----
    domain, domain_score = domain_classifier.classify_domain(query)
    complexity_flag = _should_escalate_by_complexity(query)

    # ---- Level 3: Fast Tier Model (Groq, free) ----
    try:
        answer, confidence = fast_tier_model.query_fast_model(query, domain)
    except (RuntimeError, Exception) as e:
        # Fast tier key missing or call failed -- fall back straight to Level 4
        # so the app still works end-to-end for a user/demo.
        try:
            cloud_answer, cost, provider = cloud_model.query_cloud_model(query)
        except RuntimeError as e2:
            return _build_response(
                answer="ASNE isn't fully configured yet: no fast-tier or "
                       "escalation API key is set. Set GROQ_API_KEY "
                       "(free) at minimum for the app to answer queries.",
                route="error",
                confidence=0,
                cost=0.0,
                start_time=start_time,
                reason=str(e2),
            )
        semantic_cache.add_to_cache(query, cloud_answer)
        return _build_response(
            answer=cloud_answer,
            route=f"{provider} (fast tier unavailable)",
            confidence=95,
            cost=cost,
            start_time=start_time,
            reason=f"Fast tier unavailable ({e}); used {provider} as fallback.",
        )

    should_escalate = confidence < CONFIDENCE_ESCALATION_THRESHOLD or complexity_flag
    if not should_escalate:
        semantic_cache.add_to_cache(query, answer)
        return _build_response(
            answer=answer,
            route=f"fast_tier_model ({domain})",
            confidence=confidence,
            cost=0.0,
            start_time=start_time,
            reason=f"Detected '{domain}' domain (score {domain_score:.2f}); "
                   f"fast tier model answered with sufficient confidence.",
        )

    # ---- Level 4: Cloud/Premium Escalation ----
    try:
        cloud_answer, cost, provider = cloud_model.query_cloud_model(query)
    except RuntimeError as e:
        semantic_cache.add_to_cache(query, answer)
        return _build_response(
            answer=answer,
            route=f"fast_tier_model ({domain}, low confidence, no escalation configured)",
            confidence=confidence,
            cost=0.0,
            start_time=start_time,
            reason=str(e),
        )

    semantic_cache.add_to_cache(query, cloud_answer)
    escalation_reason = (
        f"Query complexity suggested escalation; fast tier confidence was {confidence}. "
        f"Escalated to {provider}."
        if complexity_flag else
        f"Fast tier confidence ({confidence}) was below threshold "
        f"({CONFIDENCE_ESCALATION_THRESHOLD}); escalated to {provider}."
    )

    return _build_response(
        answer=cloud_answer,
        route=provider,
        confidence=95,
        cost=cost,
        start_time=start_time,
        reason=escalation_reason,
    )


def _should_escalate_by_complexity(query: str) -> bool:
    normalized = query.lower()
    if len(normalized) >= COMPLEXITY_LENGTH_THRESHOLD:
        return True
    return any(keyword in normalized for keyword in COMPLEXITY_KEYWORDS)


def _build_response(answer, route, confidence, cost, start_time, reason):
    latency = round(time.time() - start_time, 3)
    return {
        "answer": answer,
        "route": route,
        "confidence": confidence,
        "latency_seconds": latency,
        "cost_usd": cost,
        "reason": reason,
    }
