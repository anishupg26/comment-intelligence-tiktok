import os
import sys
import json
import pickle
import pandas as pd
import redis

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from config.settings import STORAGE_RAW_DIR, REDIS_URL
from pipelines.process_comments import process_comments


def get_redis():
    return redis.Redis.from_url(REDIS_URL)


def run_worker():
    r = get_redis()
    while True:
        _, payload = r.blpop("job_queue")
        job = json.loads(payload)
        job_id = job["job_id"]
        dataset_id = job["dataset_id"]

        try:
            r.set(f"job:{job_id}", json.dumps({"status": "processing", "progress": 0.05}))
            path = os.path.join(STORAGE_RAW_DIR, f"{dataset_id}.csv")
            df = pd.read_csv(path)
            process_comments(df, job_id=job_id, dataset_id=dataset_id)
        except Exception as exc:
            r.set(f"job:{job_id}", json.dumps({"status": "failed", "progress": 1.0, "error": str(exc)}))


if __name__ == "__main__":
    run_worker()
