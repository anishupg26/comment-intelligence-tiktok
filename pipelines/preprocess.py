import re


def normalize_columns(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def detect_comment_column(df):
    priority = [
        "comment",
        "comment_text",
        "text",
        "body",
        "content",
        "message",
        "caption",
        "transcript"
    ]
    for col in priority:
        if col in df.columns:
            return col

    object_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    best_col = None
    best_len = 0
    for col in object_cols:
        avg_len = df[col].astype(str).str.len().mean()
        if avg_len > 10 and avg_len > best_len:
            best_len = avg_len
            best_col = col
    return best_col


def detect_optional_columns(df):
    aliases = {
        "likes": ["likes", "like_count", "upvotes"],
        "sentiment": ["sentiment", "sentiment_score"],
        "theme": ["theme", "label", "cluster", "category"],
        "timestamp": ["timestamp", "time", "created_at", "datetime", "date"],
        "video_id": ["video_id", "vid", "post_id"],
        "user_id": ["user_id", "uid", "author_id"]
    }
    mapping = {}
    for target, options in aliases.items():
        for col in options:
            if col in df.columns:
                mapping[target] = col
                break
    return mapping
