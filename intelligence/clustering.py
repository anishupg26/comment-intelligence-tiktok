import pandas as pd
from sklearn.cluster import KMeans
from intelligence.embeddings import get_embeddings

def cluster_comments(csv_path, n_clusters=5):
    df = pd.read_csv(csv_path)

    comments = df["comment"].tolist()

    embeddings = get_embeddings(comments)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    df["cluster"] = labels

    cluster_counts = df["cluster"].value_counts().to_dict()

    total_comments = len(df)

    return df, cluster_counts, total_comments


