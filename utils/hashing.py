import hashlib


def text_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def dataset_hash(df) -> str:
    return hashlib.md5(df.to_csv(index=False).encode()).hexdigest()
