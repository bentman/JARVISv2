from __future__ import annotations
from typing import List, Dict, Optional
import requests

class WebSearchProvider:
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        raise NotImplementedError

class BingProvider(WebSearchProvider):
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {"q": query, "count": max_results}
        r = requests.get(self.endpoint, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in (data.get("webPages", {}) or {}).get("value", [])[:max_results]:
            results.append({
                "title": item.get("name", ""),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", ""),
            })
        return results

class GoogleCSEProvider(WebSearchProvider):
    def __init__(self, api_key: str, cx: str):
        self.api_key = api_key
        self.cx = cx
        self.endpoint = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": max(1, min(max_results, 10)),
        }
        r = requests.get(self.endpoint, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get("items", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            })
        return results

class TavilyProvider(WebSearchProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.tavily.com/search"

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        payload = {
            "query": query,
            "max_results": max_results,
        }
        r = requests.post(self.endpoint, json=payload, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        results = []
        # Expect data to contain a list of results with title/url/snippet-compatible fields
        # Normalize conservatively
        for item in data.get("results", []):
            results.append({
                "title": item.get("title") or item.get("name") or "",
                "url": item.get("url") or item.get("link") or "",
                "snippet": item.get("snippet") or item.get("content") or "",
            })
        return results