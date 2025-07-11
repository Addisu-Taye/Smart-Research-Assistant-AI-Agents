# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-06-15
# Purpose: Format references in standard styles
# Key Features:
#   - APA/MLA/Chicago support (mocked)
#   - Auto-detection of source types (mocked)
#   - Error fallback
#   - Correctly interacts with AgentState

from typing import Literal, TypedDict, List, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Placeholder for log_error if it's not defined elsewhere
def log_error(message: str):
    print(f"ERROR: {message}")

# Re-define AgentState for type hinting within this agent, matching main.py
class AgentState(TypedDict):
    query: str
    messages: Annotated[List[BaseMessage], operator.add]
    scraped_content: Annotated[List[str], operator.add]
    sentiment_results: Optional[str]
    translated_content: Optional[str]
    summarized_text: Optional[str]
    fact_check_results: Optional[str]
    citations: Annotated[List[str], operator.add] # This will store the formatted citations
    next_step: Optional[str]
    search_query_for_scraper: Optional[str]
    # summary_length: Optional[str] # Uncomment if you add this to AgentState in main.py
    # citation_style: Optional[str] # Uncomment if you want coordinator to set this


def citation_formatter_agent(state: AgentState) -> dict:
    """
    Converts raw sources (scraped content) into formatted citations and updates the AgentState.

    Args:
        state (AgentState): The current state of the graph.

    Returns:
        dict: A dictionary containing updates to the state, specifically
              adding formatted citations to 'citations'.
    """
    print("\n--- Citation Formatter Agent: Formatting citations ---")
    
    # The citation formatter should ideally work on the original source URLs/metadata,
    # not just the scraped content snippets. For this example, we'll use scraped_content
    # as a proxy for sources, but a real implementation would need more structured data.
    sources_content = state.get("scraped_content", [])
    messages_to_add = []

    if not sources_content:
        print("Citation Formatter: No scraped content found to format citations from.")
        messages_to_add.append(AIMessage(content="Citation Formatter: No content for citation."))
        return {
            "citations": ["Citations unavailable - No content"],
            "messages": messages_to_add
        }

    # Get the desired citation style from the state, or use a default
    # You might want the coordinator to set this in the state.
    # For now, a hardcoded default.
    # style = state.get("citation_style", "APA")
    style = "APA" # Defaulting for now

    formatted_citations = []
    for i, source_text in enumerate(sources_content, 1):
        try:
            # This is a very basic heuristic; real auto-detection would be more complex.
            if "arxiv.org" in source_text.lower():
                formatted_citations.append(_format_arxiv(source_text, style, i))
            elif "doi.org" in source_text.lower():
                formatted_citations.append(_format_doi(source_text, style, i))
            else:
                # Fallback for general web snippets or unknown types
                # In a real scenario, you'd try to extract title, author, date, URL.
                formatted_citations.append(f"[{i}] Web Source. (n.d.). {source_text[:100]}... [APA-like mock]")
            
            messages_to_add.append(AIMessage(content=f"Citation Formatter: Formatted source {i} (Style: {style})."))

        except Exception as e:
            log_error(f"Citation formatting for source {i} failed: {e}")
            formatted_citations.append(f"[{i}] Citation unavailable due to error.")
            messages_to_add.append(AIMessage(content=f"Citation Formatter: Error formatting source {i}: {e}"))
    
    print(f"Citation Formatter: Finished formatting {len(formatted_citations)} citations.")

    # Return updates to the state.
    # 'citations' uses operator.add, so new citations will be appended.
    # 'messages' also uses operator.add, so new messages will be appended.
    return {
        "citations": formatted_citations,
        "messages": messages_to_add
    }

def _format_arxiv(source: str, style: Literal["APA","MLA", "Chicago"], idx: int) -> str:
    """Mock arXiv formatter - replace with real implementation."""
    # In a real implementation, you'd parse the arxiv ID and fetch metadata
    # from the arXiv API to get author, title, year, etc.
    print(f"Citation Formatter: Mock formatting arXiv source {idx} for style {style}.")
    if style.lower() == "apa":
        return f"[{idx}] Author, A. A. (2024). Title of ArXiv Paper. *arXiv preprint arXiv:{source.split('arxiv.org/')[-1].split('/')[0]}*."
    elif style.lower() == "mla":
        return f"[{idx}] Author, A. A. \"Title of ArXiv Paper.\" *arXiv*, 2024, arXiv:{source.split('arxiv.org/')[-1].split('/')[0]}."
    else: # Default or Chicago
        return f"[{idx}] ArXiv Paper (2024). {source[:50]}... [Mock {style}]"

def _format_doi(source: str, style: str, idx: int) -> str:
    """Mock DOI formatter - replace with real implementation."""
    # In a real implementation, you'd use a DOI resolver API (e.g., Crossref)
    # to fetch metadata for the article.
    print(f"Citation Formatter: Mock formatting DOI source {idx} for style {style}.")
    doi_part = source.split('doi.org/')[-1].split(' ')[0] # Get just the DOI part
    if style.lower() == "apa":
        return f"[{idx}] Author, B. B. (2023). Title of Journal Article. *Journal Name*, *Volume*(Issue), pages. doi:{doi_part}"
    elif style.lower() == "mla":
        return f"[{idx}] Author, B. B. \"Title of Journal Article.\" *Journal Name*, vol. X, no. Y, 2023, pp. Z-Z, doi:{doi_part}."
    else: # Default or Chicago
        return f"[{idx}] Journal Article (2023). doi:{doi_part} [Mock {style}]"

