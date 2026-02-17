print("PROCESS COMMENTS FILE LOADED")

import os
import time
import json
import pickle
import random
import numpy as np
import pandas as pd
import redis
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer
from numpy.linalg import norm

from config.settings import STORAGE_PROCESSED_DIR, REDIS_URL
from pipelines.preprocess import normalize_columns, detect_comment_column, detect_optional_columns
from utils.hashing import dataset_hash


def get_redis():
    return redis.Redis.from_url(REDIS_URL)


def update_job_status(job_id, status, progress=None):
    if not job_id:
        return
    r = get_redis()
    payload = {"status": status}
    if progress is not None:
        payload["progress"] = progress
    r.set(f"job:{job_id}", json.dumps(payload))


def _load_artifacts():
    embeddings_path = os.path.join(STORAGE_PROCESSED_DIR, "embeddings.pkl")
    labels_path = os.path.join(STORAGE_PROCESSED_DIR, "cluster_labels.csv")
    theme_map_path = os.path.join(STORAGE_PROCESSED_DIR, "theme_mapping.json")
    metrics_path = os.path.join(STORAGE_PROCESSED_DIR, "theme_metrics.csv")

    if not (os.path.exists(embeddings_path) and os.path.exists(labels_path) and os.path.exists(theme_map_path) and os.path.exists(metrics_path)):
        raise FileNotFoundError(
            "Required artifacts not found: embeddings.pkl, cluster_labels.csv, theme_mapping.json, theme_metrics.csv"
        )

    with open(embeddings_path, "rb") as f:
        embeddings = pickle.load(f)

    labels_df = pd.read_csv(labels_path)

    with open(theme_map_path, "r") as f:
        theme_map = json.load(f)

    theme_metrics = pd.read_csv(metrics_path)

    return embeddings, labels_df, theme_map, theme_metrics


def process_comments(df, job_id=None, dataset_id=None):
    np.random.seed(42)
    random.seed(42)

    os.makedirs(STORAGE_PROCESSED_DIR, exist_ok=True)

    start = time.time()
    df = normalize_columns(df)
    comment_col = detect_comment_column(df)
    if not comment_col:
        raise ValueError("No comment column detected")

    if comment_col != "comment":
        df = df.rename(columns={comment_col: "comment"})

    optional_map = detect_optional_columns(df)
    for target, source in optional_map.items():
        if target not in df.columns and source in df.columns:
            df = df.rename(columns={source: target})

    if "comment_id" in df.columns:
        df = df.drop_duplicates(subset=["comment_id"])

    if dataset_id is None:
        dataset_id = dataset_hash(df)

    update_job_status(job_id, "processing", progress=0.05)

    embeddings, labels_df, theme_map, theme_metrics = _load_artifacts()
    print("\nSTEP 1 — after embedding generation")
    print(len(df))

    if "comment_id" in df.columns and "comment_id" in labels_df.columns:
        df = df.merge(labels_df[["comment_id", "cluster"]], on="comment_id", how="left")
    elif len(labels_df) == len(df):
        df["cluster"] = labels_df["cluster"].values
    else:
        raise ValueError("Cluster labels do not align with dataset")

    theme_map = {str(k): str(v).strip().lower() for k, v in theme_map.items()}
    df["theme"] = df["cluster"].astype(str).map(theme_map)
    df["theme"] = df["theme"].astype(str).str.strip()
    print("\nSTEP 2 — after clustering assignment")
    print(df["theme"].value_counts())
    print("\nSTEP 3 — after any filtering / cleaning")
    print(df["theme"].value_counts())

    theme_metrics["theme"] = theme_metrics["theme"].astype(str).str.strip().str.lower()

    update_job_status(job_id, "processing", progress=0.3)

    comment_series = df["comment"].astype(str)

    embeddings_array = np.array(embeddings)
    if len(embeddings_array) >= 2:
        coords = PCA(n_components=2).fit_transform(embeddings_array)
    else:
        coords = np.zeros((len(embeddings_array), 2))

    if "likes" in df.columns:
        likes = df["likes"].fillna(0).astype(float).to_numpy()
    else:
        likes = comment_series.apply(lambda t: float(len(str(t).split()))).to_numpy()

    if "sentiment" in df.columns:
        sentiment = df["sentiment"].fillna(0).astype(float).to_numpy()
    else:
        sentiment = comment_series.apply(lambda t: 0.0).to_numpy()

    embeddings_2d = pd.DataFrame({
        "x": coords[:, 0],
        "y": coords[:, 1],
        "cluster": df["cluster"],
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

    theme_summary = (
        df.groupby("theme")
        .agg(
            volume=("comment", "count"),
            avg_likes=("likes", "mean"),
            avg_sentiment=("sentiment", "mean"),
        )
        .reset_index()
    )
    print("\nSTEP 4 — after aggregation")
    print(theme_summary["theme"].value_counts())

    comment_counts = (
        df.groupby("cluster")[["comment"]].count().reset_index()
    )
    comment_counts.columns = ["cluster_id", "comment_count"]

    impact_scores = theme_metrics.merge(comment_counts, on="cluster_id", how="left")
    impact_scores["theme"] = impact_scores["theme"].astype(str).str.strip().str.lower()
    print("COLUMNS NOW (impact_scores after merge):", impact_scores.columns.tolist())

    print("INSIGHTS DF COLUMNS:", impact_scores.columns)

    impact_by_theme = (
        impact_scores.groupby("theme", as_index=False)["impact_score"]
        .max()
        .rename(columns={"impact_score": "impact_score"})
    )
    theme_summary = theme_summary.merge(impact_by_theme, on="theme", how="left")
    theme_summary["theme"] = theme_summary["theme"].astype(str).str.strip()
    theme_summary = (
        theme_summary
        .sort_values("impact_score", ascending=False)
        .drop_duplicates(subset="theme", keep="first")
        .reset_index(drop=True)
    )

    top_insights = []
    if "recommended_action" in impact_scores.columns:
        for _, row in theme_summary.iterrows():
            theme_val = row.get("theme", "unknown")
            insight_row = impact_scores[impact_scores["theme"] == theme_val.lower()].head(1)
            if insight_row.empty:
                continue
            insight_row = insight_row.iloc[0]
            top_insights.append({
                "theme": theme_val,
                "problem": insight_row.get("insight", ""),
                "recommended_action": insight_row.get("recommended_action", ""),
                "impact_estimate": insight_row.get("impact_score", 0),
                "risk_flag": insight_row.get("risk_flag", "None")
            })
    actions_df = pd.DataFrame(top_insights)
    print("\nSTEP 5 — before computing actions")
    if not actions_df.empty:
        print(actions_df["theme"].value_counts())
    else:
        print("No actions generated")

    keywords = {}
    vectorizer = CountVectorizer(stop_words="english", max_features=8)
    for cluster_id, group in df.groupby("cluster"):
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

    total_time = time.time() - start

    for col in ["engagement_lift", "view_growth", "retention_gain"]:
        if col not in impact_scores.columns:
            impact_scores[col] = np.nan
    impact_scores = impact_scores[[
        "theme",
        "impact_score",
        "engagement_lift",
        "view_growth",
        "retention_gain"
    ]]

    print("\n=== FINAL INSIGHT TABLE ===")
    print(impact_scores.head(20))
    print("\nColumns:", impact_scores.columns.tolist())
    print("\nNull counts:")
    print(impact_scores.isnull().sum())
    if "theme" in impact_scores.columns:
        print("\nUnique themes:")
        print(impact_scores["theme"].unique())

    results = {
        "dataset_id": dataset_id,
        "clusters": df,
        "cluster_metrics": cluster_metrics,
        "top_insights": top_insights,
        "impact_scores": impact_scores,
        "theme_summary": theme_summary,
        "embeddings_2d": embeddings_2d,
        "keywords": keywords,
        "performance": {
            "total_rows": len(df),
            "total_time": total_time,
            "rows_per_second": len(df) / total_time if total_time > 0 else 0,
            "embedding_time": 0.0,
            "clustering_time": 0.0
        }
    }

    output_path = os.path.join(STORAGE_PROCESSED_DIR, f"{dataset_id}.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(results, f)

    r = get_redis()
    r.set(f"results:{dataset_id}", pickle.dumps(results))
    r.set(f"clusters:{dataset_id}", pickle.dumps(df))
    r.set(f"insights:{dataset_id}", pickle.dumps(impact_scores))

    update_job_status(job_id, "completed", progress=1.0)

    return results
