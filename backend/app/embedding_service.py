import os
import requests

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

EMBEDDING_API_URL = "https://integrate.api.nvidia.com/v1/embeddings"
EMBEDDING_MODEL = "nvidia/llama-3.2-nv-embedqa-1b-v2"


def generate_embedding(text, input_type="passage"):
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY is not configured.")

    response = requests.post(
        EMBEDDING_API_URL,
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "input": [text],
            "model": EMBEDDING_MODEL,
            "input_type": input_type,
            "encoding_format": "float",
        },
        timeout=120,
    )

    if not response.ok:
        raise RuntimeError(
            f"NVIDIA embedding error {response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    embedding = data["data"][0]["embedding"]

    print("Embedding dimension:", len(embedding))

    return embedding