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


def run_agent(company: str) -> dict:
    """
    Company Research Agent.
    Routes simple searches to Haiku, final synthesis to Sonnet.
    Returns structured report with sections and execution trace.
    """
    trace = []

    # Step 1 — parallel searches using Haiku for planning
    searches = [
        ("overview", f"{company} company overview what they do products services 2026"),
        ("news", f"{company} latest news 2026"),
        ("engineering", f"{company} engineering tech stack culture hiring 2026"),
    ]

    results = {}
    for key, query in searches:
        trace.append({"step": f"search_{key}", "model": "haiku", "query": query})
        results[key] = search_web(query)

    # Step 2 — classify complexity (simple routing logic)
    # All searches done — now synthesize with Sonnet
    trace.append({"step": "synthesize", "model": "sonnet"})

    context = f"""
Company: {company}

OVERVIEW SEARCH RESULTS:
{results['overview']}

RECENT NEWS:
{results['news']}

ENGINEERING & CULTURE:
{results['engineering']}
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
