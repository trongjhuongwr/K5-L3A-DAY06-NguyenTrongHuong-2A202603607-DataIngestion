"""Embedding generation via OpenRouter API."""
import os
import urllib.request
import urllib.error
import json
import time


def get_embeddings(texts: list[str], model: str = "openai/text-embedding-3-small", batch_size: int = 25) -> list[list[float]]:
    """Retrieve vector embeddings for a list of texts using OpenRouter API."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENROUTER_API_KEY in environment or .env file.")

    url = "https://openrouter.ai/api/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    all_embeddings: list[list[float]] = []
    total_texts = len(texts)

    for i in range(0, total_texts, batch_size):
        batch = texts[i:i + batch_size]
        payload = json.dumps({"model": model, "input": batch}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers)

        success = False
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    for item in data["data"]:
                        all_embeddings.append(item["embedding"])
                success = True
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                print(f"[Warning] Embedding batch {i//batch_size + 1} attempt {attempt + 1} failed: {exc}. Retrying...")
                time.sleep(1.5 * (attempt + 1))

        if not success:
            raise RuntimeError(f"Failed to generate embeddings for batch {i} after 3 attempts.")

        # Rate-limiting cushion
        time.sleep(0.15)

    return all_embeddings
