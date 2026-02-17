import time
import numpy as np
import redis

from intelligence.embeddings.embedder import generate_embeddings
from config.settings import REDIS_URL, EMBEDDING_BATCH_SIZE
from utils.hashing import text_hash


def get_redis():
    return redis.Redis.from_url(REDIS_URL)


def embed_texts(texts, progress_callback=None, log_callback=None):
    r = get_redis()
    embeddings = [None] * len(texts)
    missing_texts = []
    missing_indices = []

    for i, text in enumerate(texts):
        key = f"embed:{text_hash(text)}"
        cached = r.get(key)
        if cached is not None:
            embeddings[i] = np.frombuffer(cached, dtype=np.float32)
        else:
            missing_texts.append(text)
            missing_indices.append(i)

    total = max(1, (len(missing_texts) + EMBEDDING_BATCH_SIZE - 1) // EMBEDDING_BATCH_SIZE)
    batch_times = []

    for batch_idx, start in enumerate(range(0, len(missing_texts), EMBEDDING_BATCH_SIZE)):
        batch = missing_texts[start:start + EMBEDDING_BATCH_SIZE]
        t0 = time.time()
        batch_embeddings = generate_embeddings(batch, batch_size=EMBEDDING_BATCH_SIZE)
        batch_time = time.time() - t0
        batch_times.append(batch_time)

        for j, emb in enumerate(batch_embeddings):
            idx = missing_indices[start + j]
            embeddings[idx] = emb
            key = f"embed:{text_hash(batch[j])}"
            r.set(key, emb.astype(np.float32).tobytes())

        if progress_callback:
            avg_batch_time = sum(batch_times) / len(batch_times)
            remaining = total - (batch_idx + 1)
            eta_seconds = remaining * avg_batch_time
            progress_callback(batch_idx + 1, total, eta_seconds)

        if log_callback:
            avg_batch_time = sum(batch_times) / len(batch_times)
            remaining = total - (batch_idx + 1)
            eta_seconds = remaining * avg_batch_time
            log_callback(eta_seconds)

    return np.vstack([emb if isinstance(emb, np.ndarray) else np.array(emb) for emb in embeddings])
