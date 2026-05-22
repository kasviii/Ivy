import httpx
import time

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def search_semantic_scholar(topic: str, max_results: int = 5) -> list[dict]:
    try:
        time.sleep(5)  # wait before request
        params = {
            "query": topic,
            "limit": max_results,
            "fields": "title,abstract,authors,year,externalIds,url"
        }

        headers = {"User-Agent": "IvyResearchAgent/1.0"}

        with httpx.Client(timeout=30) as client:
            response = client.get(
                SEMANTIC_SCHOLAR_URL, 
                params=params,
                headers=headers
            )
            if response.status_code == 429:
                print("  [Semantic Scholar] Rate limited, waiting 15s...")
                time.sleep(15)
                response = client.get(
                    SEMANTIC_SCHOLAR_URL,
                    params=params,
                    headers=headers
                )
            response.raise_for_status()
            data = response.json()

        papers = []
        for item in data.get("data", []):
            if not item.get("abstract"):
                continue
            papers.append({
                "title": item.get("title", ""),
                "abstract": item.get("abstract", ""),
                "authors": [a["name"] for a in item.get("authors", [])],
                "year": item.get("year"),
                "url": item.get("url", ""),
                "source": "semantic_scholar"
            })

        print(f"  [Semantic Scholar] Found {len(papers)} papers")
        return papers

    except Exception as e:
        print(f"  [Semantic Scholar] Error: {e}")
        return []