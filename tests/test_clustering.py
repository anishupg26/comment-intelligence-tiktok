from engine.clustering import cluster_comments
from engine.insights import generate_cluster_insight

# Strategic weight mapping
strategic_weights = {
    "Request": 5,
    "Confusion": 4,
    "Skepticism": 3,
    "Praise": 2,
    "Noise": 1
}

# Run clustering
df, cluster_counts, total = cluster_comments("data/comments.csv", n_clusters=3)

results = []

for cluster_id, count in cluster_counts.items():
    cluster_df = df[df["cluster"] == cluster_id]
    comments_list = cluster_df["comment"].tolist()

    # Generate structured insight (already returns dict)
    insight = generate_cluster_insight(comments_list)

    comment_share = round((count / total) * 100, 2)

    classification = insight["classification"]
    weight = strategic_weights.get(classification, 1)
    impact_score = round(comment_share * weight, 2)

    risk_flag = insight["risk_flag"]

    # Risk override logic
    if classification == "Confusion" and comment_share > 15:
        risk_flag = "Retention Risk"

    if classification == "Skepticism" and comment_share > 10:
        risk_flag = "Trust Risk"

    results.append({
        "cluster_id": cluster_id,
        "comment_share_%": comment_share,
        "impact_score": impact_score,
        "theme": insight["theme"],
        "classification": classification,
        "insight": insight["insight"],
        "suggested_action": insight["suggested_action"],
        "risk_flag": risk_flag
    })

# Sort by impact score descending
results = sorted(results, key=lambda x: x["impact_score"], reverse=True)

print("\n=== PRIORITIZED INSIGHTS ===\n")

for r in results:
    print(r)
    print()

