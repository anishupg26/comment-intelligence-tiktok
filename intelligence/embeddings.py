import os
import time
import pickle
import hashlib

from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

client = OpenAI()

CACHE_PATH = ".cache/embeddings.pkl"


def text_hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    with open(CACHE_PATH, "rb") as f:
        return pickle.load(f)


def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(cache, f)


def generate_embeddings_batched(texts, batch_size=100, model="text-embedding-3-small", progress_callback=None):
    cache = _load_cache()
    embeddings = [None] * len(texts)
    missing_texts = []
    missing_indices = []
    missing_hashes = []

    for i, text in enumerate(texts):
        h = text_hash(text)
        if h in cache:
            embeddings[i] = cache[h]
        else:
            missing_texts.append(text)
            missing_indices.append(i)
            missing_hashes.append(h)

    total_batches = max(1, (len(missing_texts) + batch_size - 1) // batch_size)
    batch_times = []

    for batch_idx, start in enumerate(tqdm(range(0, len(missing_texts), batch_size))):
        batch = missing_texts[start:start + batch_size]
        batch_hashes = missing_hashes[start:start + batch_size]
        batch_indices = missing_indices[start:start + batch_size]

        t0 = time.time()
        response = client.embeddings.create(
            model=model,
            input=batch
        )
        batch_time = time.time() - t0
        batch_times.append(batch_time)

        for j, emb in enumerate(response.data):
            idx = batch_indices[j]
            embeddings[idx] = emb.embedding
            cache[batch_hashes[j]] = emb.embedding

        if progress_callback:
            avg_batch_time = sum(batch_times) / len(batch_times)
            remaining_batches = total_batches - (batch_idx + 1)
            eta_seconds = remaining_batches * avg_batch_time
            progress_callback(batch_idx + 1, total_batches, eta_seconds)

    _save_cache(cache)
    return embeddings


def get_embeddings(texts, model="text-embedding-3-small", batch_size=100, progress_callback=None):
    return generate_embeddings_batched(
        texts,
        batch_size=batch_size,
        model=model,
        progress_callback=progress_callback
    )
