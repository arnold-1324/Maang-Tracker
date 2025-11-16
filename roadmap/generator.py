# roadmap/generator.py
from memory.db import get_weaknesses

# basic mapping from weaknesses to recommended topics
TOPIC_MAP = {
    "Dynamic Programming / Medium Problems": ["DP fundamentals", "DP - patterns (knapsack, LIS, partition)", "Practice 20 medium DP problems"],
    "Hard Problems": ["Advanced graph problems", "Practice 10 hard problems with editorial reading"],
    "OSS/ProjectExposure": ["Build a medium-size project", "Open-source contribution: fix small issues"],
}

def recommend(limit=5):
    weaknesses = get_weaknesses(limit)
    recs = []
    for w in weaknesses:
        topic = w["topic"]
        score = w["score"]
        recs.append({
            "topic": topic,
            "score": score,
            "recommendations": TOPIC_MAP.get(topic, ["Review fundamentals", "Practice problems"])
        })
    return recs
