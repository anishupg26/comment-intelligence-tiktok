import os
import uuid
import pandas as pd
from config.settings import STORAGE_RAW_DIR


def save_raw_dataset(df):
    os.makedirs(STORAGE_RAW_DIR, exist_ok=True)
    dataset_id = str(uuid.uuid4())
    path = os.path.join(STORAGE_RAW_DIR, f"{dataset_id}.csv")
    df.to_csv(path, index=False)
    return dataset_id, path
