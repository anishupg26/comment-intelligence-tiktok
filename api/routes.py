import os
import io
import json
import pickle
import uuid
import pandas as pd
import redis
from fastapi import APIRouter, UploadFile, File, HTTPException

from config.settings import STORAGE_RAW_DIR, STORAGE_PROCESSED_DIR, REDIS_URL
from pipelines.ingest import save_raw_dataset
from pipelines.preprocess import normalize_columns, detect_comment_column

router = APIRouter()


def get_redis():
    return redis.Redis.from_url(REDIS_URL)


def _serialize_result(payload):
    if isinstance(payload, pd.DataFrame):
        return payload.to_dict(orient="records")
    if isinstance(payload, dict):
        out = {}
        for k, v in payload.items():
            out[k] = _serialize_result(v)
        return out
    if isinstance(payload, list):
        return [_serialize_result(v) for v in payload]
    return payload


@router.post("/upload")
def upload(file: UploadFile = File(...)):
    contents = file.file.read()
    df = pd.read_csv(io.BytesIO(contents))
    df = normalize_columns(df)
    comment_col = detect_comment_column(df)
    if not comment_col:
        raise HTTPException(status_code=400, detail="No comment column detected")

    dataset_id, path = save_raw_dataset(df)
    return {"dataset_id": dataset_id}


@router.post("/process")
def process(dataset_id: str):
    job_id = str(uuid.uuid4())
    r = get_redis()
    r.set(f"job:{job_id}", json.dumps({"status": "queued", "progress": 0.0}))
    r.rpush("job_queue", json.dumps({"job_id": job_id, "dataset_id": dataset_id}))
    return {"job_id": job_id}


@router.get("/status/{job_id}")
def status(job_id: str):
    r = get_redis()
    payload = r.get(f"job:{job_id}")
    if not payload:
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(payload)


@router.get("/results/{dataset_id}")
def results(dataset_id: str):
    r = get_redis()
    cached = r.get(f"results:{dataset_id}")
    if cached:
        data = pickle.loads(cached)
    else:
        path = os.path.join(STORAGE_PROCESSED_DIR, f"{dataset_id}.pkl")
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Results not found")
        with open(path, "rb") as f:
            data = pickle.load(f)
    return {"data": _serialize_result(data)}


@router.get("/clusters")
def clusters(dataset_id: str):
    r = get_redis()
    cached = r.get(f"clusters:{dataset_id}")
    if cached:
        data = pickle.loads(cached)
        return {"data": _serialize_result(data)}
    raise HTTPException(status_code=404, detail="Clusters not found")


@router.get("/insights")
def insights(dataset_id: str):
    r = get_redis()
    cached = r.get(f"insights:{dataset_id}")
    if cached:
        data = pickle.loads(cached)
        return {"data": _serialize_result(data)}
    raise HTTPException(status_code=404, detail="Insights not found")


@router.get("/actions")
def actions(dataset_id: str):
    r = get_redis()
    cached = r.get(f"results:{dataset_id}")
    if cached:
        data = pickle.loads(cached)
        return {"data": _serialize_result(data.get("top_insights", []))}
    raise HTTPException(status_code=404, detail="Actions not found")
