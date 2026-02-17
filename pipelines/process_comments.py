print("PROCESS COMMENTS FILE LOADED")

import os
import time
import json
import pickle
import random
import numpy as np
import pandas as pd
import redis

from config.settings import STORAGE_PROCESSED_DIR, REDIS_URL
from pipelines.preprocess import normalize_columns, detect_comment_column, detect_optional_columns
from utils.hashing import dataset_hash
from intelligence.pipeline import run_analysis


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

    update_job_status(job_id, "processing", progress=0.3)
    results = run_analysis(
        df,
        text_col="comment",
        n_clusters=8,
        batch_size=100
    )
    total_time = time.time() - start
    results["performance"]["total_time"] = total_time

    results = {
        **results,
        "dataset_id": dataset_id
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
