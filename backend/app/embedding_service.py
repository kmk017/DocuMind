import os
import requests

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

EMBEDDING_API_URL = "https://integrate.api.nvidia.com/v1/embeddings"
EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"


def generate_embedding(text):
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY is not configured.")

    response = requests.post(
        EMBEDDING_API_URL,
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "input": [text],
            "model": EMBEDDING_MODEL,
            "input_type": "query",
            "encoding_format": "float",
        },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()
    return data["data"][0]["embedding"]