import numpy as np
from openai import OpenAI
from config.settings import OPENAI_MODEL_EMBEDDINGS, EMBEDDING_BATCH_SIZE

client = OpenAI()


def generate_embeddings(texts, batch_size=EMBEDDING_BATCH_SIZE):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model=OPENAI_MODEL_EMBEDDINGS,
            input=batch
        )
        all_embeddings.extend([e.embedding for e in response.data])
    return np.array(all_embeddings)
