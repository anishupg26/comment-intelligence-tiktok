import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

def get_embeddings(texts, model="text-embedding-3-small"):
    embeddings = []
    
    for text in texts:
        response = client.embeddings.create(
            model=model,
            input=text
        )
        embeddings.append(response.data[0].embedding)
    
    return embeddings

