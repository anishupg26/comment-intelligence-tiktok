from engine.embeddings import get_embeddings

texts = ["This is amazing", "I am confused about step 3"]

embeds = get_embeddings(texts)

print("Number of embeddings:", len(embeds))
print("Embedding length:", len(embeds[0]))

