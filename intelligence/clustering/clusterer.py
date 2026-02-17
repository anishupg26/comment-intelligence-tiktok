import numpy as np
from sklearn.cluster import MiniBatchKMeans
from config.settings import N_CLUSTERS, CLUSTER_BATCH_SIZE


def cluster_embeddings(embeddings, n_clusters=N_CLUSTERS):
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        batch_size=CLUSTER_BATCH_SIZE,
        random_state=42
    )
    labels = kmeans.fit_predict(embeddings)
    return labels
