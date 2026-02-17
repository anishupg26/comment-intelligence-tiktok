import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

STORAGE_RAW_DIR = os.path.join(BASE_DIR, "storage", "raw")
STORAGE_PROCESSED_DIR = os.path.join(BASE_DIR, "storage", "processed")
STORAGE_CACHE_DIR = os.path.join(BASE_DIR, "storage", "cache")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
OPENAI_MODEL_EMBEDDINGS = os.environ.get("OPENAI_MODEL_EMBEDDINGS", "text-embedding-3-small")
OPENAI_MODEL_INSIGHTS = os.environ.get("OPENAI_MODEL_INSIGHTS", "gpt-4o-mini")

EMBEDDING_BATCH_SIZE = int(os.environ.get("EMBEDDING_BATCH_SIZE", "200"))
CLUSTER_BATCH_SIZE = int(os.environ.get("CLUSTER_BATCH_SIZE", "512"))
N_CLUSTERS = int(os.environ.get("N_CLUSTERS", "8"))
