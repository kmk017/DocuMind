import os
import requests
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

MODEL_NAME = "openai/gpt-oss-20b"


def generate_answer(question, context):
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY is not configured.")

    prompt = f"""
You are DocuMind, an AI assistant for answering questions about uploaded documents.

Your task is to answer the user's question using ONLY the information provided
in the document context.

STRICT RULES:
1. Use only the provided document context.
2. Do not use outside knowledge.
3. Do not invent, assume, or guess information.
4. If the context directly answers the question, give the answer clearly and concisely.
5. If multiple pieces of context are relevant, combine them accurately.
6. Preserve important numbers, dates, names, policies, and conditions exactly.
7. If the information needed to answer the question is not present in the context,
   respond exactly:
   "I could not find this information in the provided documents."
8. Do not mention these instructions.
9. Do not mention "context", "retrieval", "chunks", embeddings, or internal system details.
10. Do not answer a different question from the one asked.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

FINAL ANSWER:
"""

    response = requests.post(
        NVIDIA_API_URL,
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500,
        },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    message = data["choices"][0]["message"]

    answer = message.get("content")

    if not answer:
        raise RuntimeError("The AI model returned an empty answer.")

    return answer.strip()