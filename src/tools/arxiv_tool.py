import arxiv
import time

def search_arxiv(topic: str, max_results: int = 5) -> list[dict]:
    try:
        time.sleep(3)  # wait before request
        client = arxiv.Client(delay_seconds=3, num_retries=3)
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []
        for result in client.results(search):
            papers.append({
                "title": result.title,
                "abstract": result.summary,
                "authors": [a.name for a in result.authors],
                "year": result.published.year,
                "url": result.entry_id,
                "source": "arxiv"
            })
            time.sleep(0.5)

        print(f"  [Arxiv] Found {len(papers)} papers")
        return papers

    except Exception as e:
        print(f"  [Arxiv] Error: {e}")
        return []