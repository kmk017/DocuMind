import os
import requests

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

EMBEDDING_API_URL = "https://ai.api.nvidia.com/v1/retrieval/nvidia/embeddings"
EMBEDDING_MODEL = "nvidia/llama-3.2-nv-embedqa-1b-v2"


def generate_embedding(text, input_type="passage"):
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY is not configured.")

    response = requests.post(
        EMBEDDING_API_URL,
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={
            "input": [text],
            "model": EMBEDDING_MODEL,
            "input_type": input_type,
        },
        timeout=120,
    )

    if not response.ok:
        raise RuntimeError(
            f"NVIDIA embedding error {response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    print("Embedding dimension:", len(data["data"][0]["embedding"]))
    
    return data["data"][0]["embedding"]