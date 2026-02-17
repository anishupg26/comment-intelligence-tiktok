import pandas as pd
import time
from sklearn.cluster import MiniBatchKMeans
from config.settings import N_CLUSTERS, CLUSTER_BATCH_SIZE
from intelligence.embeddings.embedder import generate_embeddings


def cluster_embeddings(embeddings, n_clusters=N_CLUSTERS):
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        batch_size=CLUSTER_BATCH_SIZE,
        random_state=42
    )
    labels = kmeans.fit_predict(embeddings)
    return labels


def cluster_comments(csv_path, n_clusters=N_CLUSTERS, batch_size=100, progress_callback=None):
    df = pd.read_csv(csv_path)
    comments = df["comment"].astype(str).tolist()

    embed_start = time.time()
    embeddings = generate_embeddings(comments, batch_size=batch_size)
    embedding_time = time.time() - embed_start

    cluster_start = time.time()
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        batch_size=CLUSTER_BATCH_SIZE,
        random_state=42
    )
    labels = kmeans.fit_predict(embeddings)
    clustering_time = time.time() - cluster_start

    df["cluster"] = labels
    cluster_counts = df["cluster"].value_counts().to_dict()
    total_comments = len(df)

    if progress_callback:
        progress_callback(1, 1, 0)

    return df, cluster_counts, total_comments, embeddings, embedding_time, clustering_time
