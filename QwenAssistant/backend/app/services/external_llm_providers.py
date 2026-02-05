from __future__ import annotations
from typing import List, Dict, Optional
import requests

class RemoteLLMProvider:
    def summarize(self, query: str, items: List[Dict], max_tokens: int = 512) -> Dict:
        raise NotImplementedError

class OpenAIProvider(RemoteLLMProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def summarize(self, query: str, items: List[Dict], max_tokens: int = 512) -> Dict:
        # Build a compact prompt with citations
        bullets = []
        for i, it in enumerate(items[:5], start=1):
            title = it.get("title") or it.get("id") or ""
            url = it.get("url", "")
            snippet = it.get("snippet") or it.get("content") or ""
            bullets.append(f"[{i}] {title} {url} — {snippet}")
        system = (
            "You are a helpful assistant. Provide a concise answer based on the provided items. "
            "Cite sources by index in square brackets. If unsure, say so. Do not include private information."
        )
        user = f"Question: {query}\nSources:\n" + "\n".join(bullets)
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
        }
        r = requests.post(self.endpoint, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        answer = data["choices"][0]["message"]["content"].strip()
        return {"answer": answer}