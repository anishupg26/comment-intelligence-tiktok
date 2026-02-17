STRATEGIC_WEIGHTS = {
    "Request": 5,
    "Confusion": 4,
    "Skepticism": 3,
    "Praise": 2,
    "Noise": 1
}

RISK_SCORES = {
    "Confusion": 80,
    "Skepticism": 70,
    "Request": 50,
    "Praise": 20,
    "Noise": 10
}


def compute_impact(share_pct, classification):
    weight = STRATEGIC_WEIGHTS.get(classification, 1)
    return share_pct * weight


def risk_score(classification):
    return RISK_SCORES.get(classification, 10)


def priority_from_impact(score):
    if score >= 200:
        return "High"
    if score >= 100:
        return "Medium"
    return "Low"
