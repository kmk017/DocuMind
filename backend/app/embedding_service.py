from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text):
    """Generate an embedding vector for the given text."""
    return model.encode(text).tolist()