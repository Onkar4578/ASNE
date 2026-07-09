"""
Level 1: Rule Engine
Instant, free, zero-model responses for common predictable patterns.
Add more patterns as you discover repeated query types during testing.
"""
import re

# Each rule: (regex_pattern, response_generator_function)
RULES = [
    (
        r"^\s*(hi|hello|hey)\s*[!.]?\s*$",
        lambda m: "Hello! Ask me anything about your SPPU subjects or general queries."
    ),
    (
        r"what\s+is\s+(\d+)\s*\+\s*(\d+)",
        lambda m: f"{int(m.group(1)) + int(m.group(2))}"
    ),
    (
        r"what\s+is\s+(\d+)\s*-\s*(\d+)",
        lambda m: f"{int(m.group(1)) - int(m.group(2))}"
    ),
    (
        r"what\s+is\s+(\d+)\s*\*\s*(\d+)",
        lambda m: f"{int(m.group(1)) * int(m.group(2))}"
    ),
    (
        r"define\s+oop|what\s+is\s+oop",
        lambda m: "OOP (Object-Oriented Programming) is a paradigm based on objects "
                  "containing data (attributes) and behavior (methods). Core principles: "
                  "Encapsulation, Inheritance, Polymorphism, Abstraction."
    ),
    (
        r"full\s+form\s+of\s+dbms",
        lambda m: "DBMS = Database Management System"
    ),
    (
        r"full\s+form\s+of\s+http",
        lambda m: "HTTP = HyperText Transfer Protocol"
    ),
]


def match_rule(query: str):
    """
    Try to match query against known rules.
    Returns response string if matched, else None.
    """
    normalized = query.strip().lower()
    for pattern, responder in RULES:
        match = re.search(pattern, normalized)
        if match:
            return responder(match)
    return None
