    def _can_escalate_llm(self) -> bool:
        if not settings.REMOTE_LLM_ENABLED:
            return False
        prov = (settings.REMOTE_LLM_PROVIDER or "").lower()
        if prov == "openai" and settings.OPENAI_API_KEY and settings.OPENAI_MODEL:
            return True
        # Future providers can be added here
        return False

    def _summarize_with_llm(self, query: str, items: List[Dict]) -> Dict:
        # Privacy: redact snippets before sending
        safe_items: List[Dict] = []
        for it in items:
            safe_items.append({
                "title": it.get("title") or it.get("id") or "",
                "url": it.get("url", ""),
                "snippet": privacy_service.redact_sensitive_data(it.get("snippet") or it.get("content") or ""),
            })
        provider: Optional[RemoteLLMProvider] = None
        prov = (settings.REMOTE_LLM_PROVIDER or "").lower()
        if prov == "openai":
            provider = OpenAIProvider(settings.OPENAI_API_KEY, settings.OPENAI_MODEL)
        else:
            raise RuntimeError("Remote LLM provider not supported")

        # Budget pre-check
        from app.services.budget_service import budget_service
        if not budget_service.within_limits():
            raise RuntimeError("Budget limit exceeded for remote LLM")

        # Call provider
        redacted_query = privacy_service.redact_sensitive_data(query)
        resp = provider.summarize(redacted_query, safe_items, max_tokens=512)
        answer = resp.get("answer", "")

        # Estimate tokens and log budget usage
        est_tokens = max(1, (len(redacted_query) + len(answer)) // 4)
        # Log cost using category-aware rate selection
        budget_service.log_event(category="llm:web", tokens_used=est_tokens, execution_time_sec=0.0)

        # Return LLM item
        return {
            "source": "llm",
            "provider": prov,
            "answer": answer,
            "citations": [it.get("url") for it in safe_items if it.get("url")],
        }

from __future__ import annotations
from typing import List, Dict, Optional

from app.core.config import settings
from app.services.memory_service import memory_service
from app.services.privacy_service import privacy_service
from app.services.search_providers import TavilyProvider, WebSearchProvider, BingProvider, GoogleCSEProvider
from app.services.external_llm_providers import OpenAIProvider, RemoteLLMProvider

class UnifiedSearchService:
    def __init__(self):
        self.enabled = settings.SEARCH_ENABLED
        self.providers: Dict[str, WebSearchProvider] = {}
        if not self.enabled:
            return
        # Build providers based on configured keys
        if settings.SEARCH_BING_API_KEY:
            self.providers["bing"] = BingProvider(settings.SEARCH_BING_API_KEY, settings.SEARCH_BING_ENDPOINT)
        if settings.SEARCH_GOOGLE_API_KEY and settings.SEARCH_GOOGLE_CX:
            self.providers["google"] = GoogleCSEProvider(settings.SEARCH_GOOGLE_API_KEY, settings.SEARCH_GOOGLE_CX)
        if settings.SEARCH_API_KEY:
            self.providers["tavily"] = TavilyProvider(settings.SEARCH_API_KEY)
        # Default order
        self.providers_order = [p.strip() for p in getattr(settings, "SEARCH_PROVIDERS", "bing,google,tavily").split(",") if p.strip()]

    def unified_search(self, query: str, include_local: bool = True, include_web: bool = False, max_results: Optional[int] = None, web_sources: Optional[List[str]] = None, escalate_llm: bool = False) -> Dict:
        from app.services.cache_service import cache_service
        max_k = max_results or settings.SEARCH_MAX_RESULTS
        items: List[Dict] = []
        # Build cache key
        cfg = privacy_service.get_settings()
        key_payload = {
            "q": query,
            "local": include_local,
            "web": include_web,
            "src": web_sources or self.providers_order,
            "k": max_k,
            "plevel": cfg.get("privacy_level"),
            "llm": bool(escalate_llm),
        }
        import json, hashlib
        key = "unified:" + hashlib.sha256(json.dumps(key_payload, sort_keys=True).encode("utf-8")).hexdigest()[:24]
        if cache_service.healthy():
            cached = cache_service.get_json(key)
            if cached:
                return cached

        # Always start with local (semantic over memory)
        if include_local:
            mem_results = memory_service.semantic_search(query)
            for m in mem_results[:max_k]:
                items.append({
                    "source": "memory",
                    "id": m.id,
                    "conversation_id": m.conversation_id,
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "mode": m.mode,
                })

        # Then optionally the web
        web_used = False
        used_providers: List[str] = []
        if include_web and self.enabled and self.providers:
            # Only allow web if not local_only
            if cfg.get("privacy_level") != "local_only":
                # Determine provider order
                order = [p for p in (web_sources or self.providers_order) if p in self.providers]
                redacted = privacy_service.redact_sensitive_data(query)
                for name in order:
                    prov = self.providers[name]
                    try:
                        web_results = prov.search(redacted, max_results=max_k)
                        if web_results:
                            web_used = True
                            used_providers.append(name)
                            for w in web_results:
                                items.append({
                                    "source": "web",
                                    "provider": name,
                                    "title": w.get("title", ""),
                                    "url": w.get("url", ""),
                                    "snippet": w.get("snippet", ""),
                                })
                    except Exception:
                        # Skip provider on error; continue others
                        continue
        result = {
            "query": query,
            "count": len(items),
            "web_used": web_used,
            "used": {"local": include_local, "web": used_providers, "llm": False},
            "items": items[:max_k]
        }

        # Optional LLM escalation
        if escalate_llm and self._can_escalate_llm() and include_web and used_providers:
            try:
                llm_item = self._summarize_with_llm(query, items[:max_k])
                result["used"]["llm"] = True
                result["items"].append(llm_item)
                result["count"] = len(result["items"])
            except Exception:
                # Skip LLM on error
                pass

        if cache_service.healthy():
            cache_service.set_json(key, result, ttl_seconds=120)
        return result

unified_search_service = UnifiedSearchService()