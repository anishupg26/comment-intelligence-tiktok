import re
import time
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer

from intelligence.clustering.clusterer import cluster_comments
from intelligence.insights.insight_generator import generate_cluster_insight


# Strategic priority weights
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

POS_WORDS = {
    "love", "great", "amazing", "helpful", "clear", "awesome", "good", "nice",
    "thanks", "thank", "appreciate", "useful"
}
NEG_WORDS = {
    "confusing", "bad", "hate", "unclear", "hard", "boring", "terrible",
    "wrong", "issue", "problem"
}


def _compute_sentiment(text):
    tokens = re.findall(r"[a-zA-Z']+", str(text).lower())
    if not tokens:
        return 0.0
    pos = sum(1 for t in tokens if t in POS_WORDS)
    neg = sum(1 for t in tokens if t in NEG_WORDS)
    if pos + neg == 0:
        return 0.0
    return (pos - neg) / (pos + neg)


def _compute_engagement(text):
    return float(len(str(text).split()))


def _priority_from_impact(score):
    if score >= 200:
        return "High"
    if score >= 100:
        return "Medium"
    return "Low"


def run_intelligence_engine(comments_df, text_col="comment", n_clusters=8, batch_size=100, progress_callback=None):

    import os
    os.makedirs("data/processed", exist_ok=True)

    temp_path = "data/processed/temp_comments.csv"
    comments_df.to_csv(temp_path, index=False)

    # STEP 1 — clustering
    labeled_df, cluster_counts, total_comments, embeddings, embedding_time, clustering_time = cluster_comments(
        temp_path,
        n_clusters=n_clusters,
        batch_size=batch_size,
        progress_callback=progress_callback
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

    return ranked_df, labeled_df, embeddings, embedding_time, clustering_time


def run_analysis(comments_df, text_col="comment", n_clusters=8, batch_size=100, progress_callback=None):
    start_time = time.time()
    ranked_df, labeled_df, embeddings, embedding_time, clustering_time = run_intelligence_engine(
        comments_df,
        text_col=text_col,
        n_clusters=n_clusters,
        batch_size=batch_size,
        progress_callback=progress_callback
    )

    clusters_df = labeled_df.copy()
    if text_col in clusters_df.columns and "comment" not in clusters_df.columns:
        clusters_df = clusters_df.rename(columns={text_col: "comment"})

    comment_series = clusters_df["comment"].astype(str)

    embeddings_array = np.array(embeddings)
    if len(embeddings_array) >= 2:
        coords = PCA(n_components=2).fit_transform(embeddings_array)
    else:
        coords = np.zeros((len(embeddings_array), 2))

    if "likes" in comments_df.columns:
        likes = comments_df["likes"].fillna(0).astype(float).to_numpy()
    else:
        likes = comment_series.apply(_compute_engagement).to_numpy()

    if "sentiment" in comments_df.columns:
        sentiment = comments_df["sentiment"].fillna(0).astype(float).to_numpy()
    else:
        sentiment = comment_series.apply(_compute_sentiment).to_numpy()

    embeddings_2d = pd.DataFrame({
        "x": coords[:, 0],
        "y": coords[:, 1],
        "cluster": clusters_df["cluster"],
        "comment": comment_series,
        "likes": likes,
        "sentiment": sentiment
    })

    cluster_metrics = (
        embeddings_2d.groupby("cluster")
        .agg(
            cluster_size=("comment", "count"),
            avg_likes=("likes", "mean"),
            avg_sentiment=("sentiment", "mean"),
            engagement_std=("likes", "std")
        )
        .reset_index()
    )

    impact_scores = ranked_df.copy()
    if "theme" not in impact_scores.columns:
        impact_scores["theme"] = impact_scores.get("cluster_id", "Unknown")
    impact_scores["risk_score"] = impact_scores.get("classification", "Noise").map(
        RISK_SCORES
    ).fillna(10)
    impact_scores["priority"] = impact_scores["impact_score"].apply(_priority_from_impact)

    comment_counts = (
        clusters_df.groupby("cluster")["comment"].count().reset_index()
    )
    comment_counts.columns = ["cluster_id", "comment_count"]

    if "cluster_id" in impact_scores.columns:
        impact_scores = impact_scores.merge(
            comment_counts,
            on="cluster_id",
            how="left"
        )
    else:
        impact_scores["comment_count"] = comment_counts["comment_count"].sum()

    impact_scores = impact_scores[[
        "cluster_id",
        "theme",
        "impact_score",
        "risk_score",
        "priority",
        "comment_count"
    ]]

    top_insights = []
    for _, row in ranked_df.iterrows():
        top_insights.append({
            "theme": row.get("theme", "Unknown"),
            "problem": row.get("insight", ""),
            "recommended_action": row.get("suggested_action", ""),
            "impact_estimate": row.get("impact_score", 0),
            "risk_flag": row.get("risk_flag", "None")
        })

    keywords = {}
    vectorizer = CountVectorizer(stop_words="english", max_features=8)
    for cluster_id, group in clusters_df.groupby("cluster"):
        comments = group["comment"].astype(str).tolist()
        if not comments:
            keywords[str(cluster_id)] = []
            continue
        matrix = vectorizer.fit_transform(comments)
        freqs = np.asarray(matrix.sum(axis=0)).ravel()
        terms = vectorizer.get_feature_names_out()
        term_df = pd.DataFrame({
            "keyword": terms,
            "importance": freqs
        }).sort_values("importance", ascending=False)
        keywords[str(cluster_id)] = term_df.head(5).to_dict(orient="records")

    total_time = time.time() - start_time

    return {
        "clusters": clusters_df,
        "cluster_metrics": cluster_metrics,
        "top_insights": top_insights,
        "impact_scores": impact_scores,
        "embeddings_2d": embeddings_2d,
        "keywords": keywords,
        "performance": {
            "total_rows": len(clusters_df),
            "total_time": total_time,
            "rows_per_second": len(clusters_df) / total_time if total_time > 0 else 0,
            "embedding_time": embedding_time,
            "clustering_time": clustering_time
        }
    }


def run_intelligence(comments_df, text_col="comment", n_clusters=8, batch_size=100, progress_callback=None):
    return run_analysis(
        comments_df,
        text_col=text_col,
        n_clusters=n_clusters,
        batch_size=batch_size,
        progress_callback=progress_callback
    )
