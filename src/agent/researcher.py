import os
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import json
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ── State ──────────────────────────────────────────────────────────────────
class ResearchState(TypedDict):
    topic: str
    papers: List[dict]
    summaries: List[str]
    reflection: str
    needs_more_papers: bool
    final_review: str
    iteration: int
    status: str

# ── LLM helper ─────────────────────────────────────────────────────────────
def llm(messages: list, temperature: float = 0.3) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()

# ── Node 1: Search papers ───────────────────────────────────────────────────
def search_papers(state: ResearchState) -> ResearchState:
    from tools.arxiv_tool import search_arxiv
    from tools.semantic_tool import search_semantic_scholar 
    print(f"🔍 Searching papers on: {state['topic']}")
    state["status"] = "searching"

    arxiv_papers = search_arxiv(state["topic"], max_results=5)
    semantic_papers = search_semantic_scholar(state["topic"], max_results=5)

    # Deduplicate by title
    seen = set()
    all_papers = []
    for p in arxiv_papers + semantic_papers:
        title = p.get("title", "").lower().strip()
        if title and title not in seen:
            seen.add(title)
            all_papers.append(p)

    state["papers"] = all_papers[:8]  # max 8 papers
    print(f"✅ Found {len(state['papers'])} unique papers")
    return state

# ── Node 2: Summarize each paper ───────────────────────────────────────────
def summarize_papers(state: ResearchState) -> ResearchState:
    print(f"📄 Summarizing {len(state['papers'])} papers...")
    state["status"] = "summarizing"
    summaries = []

    for i, paper in enumerate(state["papers"]):
        title = paper.get("title", "Unknown")
        abstract = paper.get("abstract", "No abstract available")
        authors = ", ".join(paper.get("authors", [])[:3])
        year = paper.get("year", "Unknown")

        prompt = f"""Summarize this research paper in 3-4 sentences focusing on:
1. The main problem it addresses
2. The methodology or approach used
3. Key findings or contributions

Paper Title: {title}
Authors: {authors} ({year})
Abstract: {abstract[:1500]}

Write a concise, informative summary:"""

        summary = llm([{"role": "user", "content": prompt}])
        summaries.append(f"**{title}** ({year})\n{summary}")
        print(f"  ✓ Summarized paper {i+1}/{len(state['papers'])}")

    state["summaries"] = summaries
    return state

# ── Node 3: Reflect on coverage ────────────────────────────────────────────
def reflect(state: ResearchState) -> ResearchState:
    print("🤔 Reflecting on research coverage...")
    state["status"] = "reflecting"

    summaries_text = "\n\n".join(state["summaries"])

    prompt = f"""You are a critical research analyst. Review these paper summaries on the topic "{state['topic']}".

{summaries_text}

Analyze:
1. What aspects of the topic are well covered?
2. What important aspects are missing or underrepresented?
3. Are there contradictions between papers?
4. Is this enough for a comprehensive literature review? (yes/no)

Respond in JSON format:
{{
  "well_covered": "...",
  "gaps": "...",
  "contradictions": "...",
  "sufficient": true/false,
  "reflection_summary": "..."
}}"""

    response = llm([{"role": "user", "content": prompt}])

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        data = json.loads(clean)
        # Only request more if we have very few papers
        state["needs_more_papers"] = (not data.get("sufficient", True)) and len(state.get("papers", [])) < 3
        state["reflection"] = data.get("reflection_summary", response)
    except Exception:
        state["needs_more_papers"] = False
        state["reflection"] = response

    print(f"  Needs more papers: {state['needs_more_papers']}")
    return state

# ── Node 4: Synthesize final review ────────────────────────────────────────
def synthesize(state: ResearchState) -> ResearchState:
    print("✍️  Synthesizing literature review...")
    state["status"] = "synthesizing"

    summaries_text = "\n\n".join(state["summaries"])
    papers_list = "\n".join([
        f"- {p.get('title', 'Unknown')} ({p.get('year', 'N/A')}) — {', '.join(p.get('authors', [])[:2])}"
        for p in state["papers"]
    ])

    prompt = f"""You are an expert academic writer. Write a comprehensive literature review on "{state['topic']}" based on the following papers.

PAPERS ANALYZED:
{papers_list}

PAPER SUMMARIES:
{summaries_text}

RESEARCH GAPS IDENTIFIED:
{state['reflection']}

Write a structured literature review with these sections:
1. **Introduction** — overview of the topic and why it matters
2. **Key Themes** — major themes and findings across papers
3. **Methodological Approaches** — how researchers have studied this topic
4. **Research Gaps & Future Directions** — what's missing and what comes next
5. **Conclusion** — synthesis of the field's current state

Make it academic but readable. Use specific paper references where relevant.
Aim for 600-900 words."""

    review = llm([{"role": "user", "content": prompt}], temperature=0.4)
    state["final_review"] = review
    state["status"] = "complete"
    print("✅ Literature review complete!")
    return state

# ── Routing ────────────────────────────────────────────────────────────────
def should_search_more(state: ResearchState) -> str:
    if len(state.get("papers", [])) == 0:
        return "synthesize"  # no papers found, just synthesize with what we have
    if state.get("needs_more_papers") and state.get("iteration", 0) < 1:
        state["iteration"] = state.get("iteration", 0) + 1
        return "search_more"
    return "synthesize"

# ── Build graph ────────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("search_papers", search_papers)
    graph.add_node("summarize_papers", summarize_papers)
    graph.add_node("reflect", reflect)
    graph.add_node("synthesize", synthesize)

    graph.set_entry_point("search_papers")
    graph.add_edge("search_papers", "summarize_papers")
    graph.add_edge("summarize_papers", "reflect")
    graph.add_conditional_edges(
        "reflect",
        should_search_more,
        {
            "search_more": "search_papers",
            "synthesize": "synthesize"
        }
    )
    graph.add_edge("synthesize", END)

    return graph.compile()

# ── Run ────────────────────────────────────────────────────────────────────
def run_research(topic: str) -> dict:
    graph = build_graph()
    initial_state = ResearchState(
        topic=topic,
        papers=[],
        summaries=[],
        reflection="",
        needs_more_papers=False,
        final_review="",
        iteration=0,
        status="starting"
    )
    result = graph.invoke(initial_state)
    return result

if __name__ == "__main__":
    result = run_research("transformer models in medical imaging")
    print("\n" + "="*60)
    print("FINAL LITERATURE REVIEW")
    print("="*60)
    print(result["final_review"])