from intelligence.scoring.impact_scoring import compute_impact, risk_score, priority_from_impact


def score_cluster(share_pct, classification):
    impact = compute_impact(share_pct, classification)
    return impact, risk_score(classification), priority_from_impact(impact)
