import pandas as pd
from intelligence.clustering import cluster_comments
from intelligence.insights import generate_cluster_insight


# Strategic priority weights
STRATEGIC_WEIGHTS = {
    "Request": 5,
    "Confusion": 4,
    "Skepticism": 3,
    "Praise": 2,
    "Noise": 1
}


def run_intelligence_engine(comments_df, text_col="comment", n_clusters=8):

    import os
    os.makedirs("data/processed", exist_ok=True)

    temp_path = "data/processed/temp_comments.csv"
    comments_df.to_csv(temp_path, index=False)

    # STEP 1 — clustering
    labeled_df, cluster_counts, total_comments = cluster_comments(
        temp_path,
        n_clusters=n_clusters
    )

    # STEP 2 — insight per cluster
    cluster_summaries = []

    for cluster_id, group in labeled_df.groupby("cluster"):

        insight = generate_cluster_insight(
            group[text_col].tolist()
        )

        # comment share %
        share_pct = (len(group) / total_comments) * 100

        # classification weight
        classification = insight.get("classification", "Noise")
        weight = STRATEGIC_WEIGHTS.get(classification, 1)

        # impact score
        impact_score = share_pct * weight

        insight["cluster_id"] = cluster_id
        insight["comment_share_pct"] = round(share_pct, 2)
        insight["impact_score"] = round(impact_score, 2)

        cluster_summaries.append(insight)

    ranked_df = pd.DataFrame(cluster_summaries)

    # STEP 3 — rank by impact
    ranked_df = ranked_df.sort_values(
        "impact_score",
        ascending=False
    ).reset_index(drop=True)

    return ranked_df, labeled_df

