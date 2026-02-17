import pandas as pd
import time
from sklearn.cluster import MiniBatchKMeans
from intelligence.embeddings import get_embeddings


def cluster_comments(csv_path, n_clusters=5, batch_size=100, progress_callback=None):
    df = pd.read_csv(csv_path)

    comments = df["comment"].tolist()

    embed_start = time.time()
    embeddings = get_embeddings(
        comments,
        batch_size=batch_size,
        progress_callback=progress_callback
    )
    embedding_time = time.time() - embed_start

    cluster_start = time.time()
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        batch_size=512,
        random_state=42
    )
    labels = kmeans.fit_predict(embeddings)
    clustering_time = time.time() - cluster_start

    df["cluster"] = labels

    cluster_counts = df["cluster"].value_counts().to_dict()

    total_comments = len(df)

    return df, cluster_counts, total_comments, embeddings, embedding_time, clustering_time
