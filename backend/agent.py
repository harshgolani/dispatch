import os
from dotenv import load_dotenv #type: ignore
from anthropic import Anthropic #type: ignore
from tavily import TavilyClient #type: ignore

load_dotenv()

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_web(query: str) -> str:
    """Search the web and return clean text results."""
    results = tavily_client.search(query, max_results=3)
    output = ""
    for r in results["results"]:
        output += f"**{r['title']}**\n{r['content']}\n\n"
    return output.strip()


def classify_result(content: str, expected_topic: str) -> bool:
    """
    Use Haiku to classify if search result is relevant.
    Returns True if relevant, False if not useful.
    This is the cost-aware routing — simple classification stays on Haiku.
    """
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=10,
        system="You are a relevance classifier. Reply with only 'yes' or 'no'.",
        messages=[
            {
                "role": "user",
                "content": f"Does this content contain useful information about '{expected_topic}'?\n\nContent: {content[:500]}"
            }
        ]
    )
    answer = response.content[0].text.strip().lower()
    return "yes" in answer


def run_agent(company: str) -> dict:
    """
    Company Research Agent.
    - Haiku handles classification (cheap, fast)
    - Sonnet handles synthesis (powerful, used once)
    Returns structured report with execution trace.
    """
    trace = []

    searches = [
        ("overview", f"{company} company overview what they do products services 2026"),
        ("news", f"{company} latest news 2026"),
        ("engineering", f"{company} engineering tech stack culture hiring 2026"),
    ]

    results = {}
    for key, query in searches:
        trace.append({"step": f"search_{key}", "model": "tavily", "query": query})
        content = search_web(query)

        # Haiku classifies if result is relevant
        trace.append({"step": f"classify_{key}", "model": "haiku"})
        relevant = classify_result(content, f"{company} {key}")

        if relevant:
            results[key] = content
            trace.append({"step": f"classify_{key}_result", "verdict": "relevant"})
        else:
            # Retry with broader query
            broader_query = f"{company} {key}"
            trace.append({"step": f"retry_{key}", "model": "tavily", "query": broader_query})
            results[key] = search_web(broader_query)
            trace.append({"step": f"classify_{key}_result", "verdict": "retried"})

    # Sonnet handles final synthesis only
    trace.append({"step": "synthesize", "model": "sonnet"})

    context = f"""
Company: {company}

OVERVIEW:
{results.get('overview', 'No results found')}

RECENT NEWS:
{results.get('news', 'No results found')}

ENGINEERING & CULTURE:
{results.get('engineering', 'No results found')}
"""

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        system="""You are a company research assistant. Given search results about a company,
write a structured, concise research brief for a job seeker or investor.
Format your response with these exact sections:
## What They Do
## Recent News
## Engineering & Culture
## Why It's Interesting

Be concise and factual. Only use information from the provided search results.""",
        messages=[
            {
                "role": "user",
                "content": f"Write a research brief for: {company}\n\nSearch results:\n{context}"
            }
        ]
    )

    return {
        "company": company,
        "report": response.content[0].text,
        "trace": trace
    }
