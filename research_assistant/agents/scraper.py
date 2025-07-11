# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-06-15
# Purpose: Fetch research materials from web/PDFs and update the AgentState
# Key Features:
#   - Uses a web search tool
#   - Supports arXiv API
#   - Integrates with PDF text extraction tool
#   - Correctly reads from and updates AgentState

import os
import arxiv
from typing import TypedDict, List, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Import the web search function from your local tools directory
from tools.web_search import search_web 

# Import the actual PDF extraction tool from tools/pdf_parser.py
from tools.pdf_parser import extract_text_from_pdf 

# Re-define AgentState for type hinting within this agent, matching main.py
class AgentState(TypedDict):
    query: str
    messages: Annotated[List[BaseMessage], operator.add]
    scraped_content: Annotated[List[str], operator.add]
    sentiment_results: Optional[str]
    translated_content: Optional[str]
    summarized_text: Optional[str]
    fact_check_results: Optional[str]
    citations: Annotated[List[str], operator.add]
    next_step: Optional[str]
    # Add any other fields the coordinator might set for the scraper
    search_query_for_scraper: Optional[str]


def web_scraper_agent(state: AgentState) -> dict:
    """
    Fetches and preprocesses research materials based on the query in AgentState.

    Args:
        state (AgentState): The current state of the graph.

    Returns:
        dict: A dictionary containing updates to the state, specifically
              adding fetched content to 'scraped_content' and updating messages.
    """
    print("\n--- Web Scraper Agent: Fetching research materials ---")
    
    current_query = state.get("query", "")
    sources = []
    messages_to_add = []

    # The coordinator might set a specific 'search_query_for_scraper' in the state
    # if it performs query decomposition. Otherwise, use the main 'query'.
    search_term = state.get("search_query_for_scraper", current_query)

    print(f"Scraper: Performing web search for: '{search_term}'")
    try:
        # Using the local search_web function.
        # This function should return a list of strings (snippets or full content).
        web_search_results = search_web(search_term)
        
        if web_search_results:
            for snippet in web_search_results:
                sources.append(snippet)
                messages_to_add.append(AIMessage(content=f"Scraper: Found web snippet: {snippet[:100]}..."))
        else:
            messages_to_add.append(AIMessage(content=f"Scraper: No web results found for '{search_term}'."))

    except Exception as e:
        print(f"Scraper: Error during web search: {e}")
        messages_to_add.append(AIMessage(content=f"Scraper: Error during web search: {e}"))

    # --- arXiv papers ---
    # Check if the search term indicates a desire for arXiv papers
    if "arxiv.org" in search_term.lower() or "arxiv paper" in search_term.lower():
        print(f"Scraper: Searching arXiv for: '{search_term}'")
        try:
            arxiv_results = arxiv.Search(
                query=search_term,
                max_results=3, # Limit to 3 results to avoid excessive processing
                sort_by=arxiv.SortCriterion.Relevance
            ).results()
            
            for paper in arxiv_results:
                if paper.summary:
                    sources.append(paper.summary)
                    messages_to_add.append(AIMessage(content=f"Scraper: Found arXiv paper '{paper.title}': {paper.summary[:100]}..."))
                # You might want to store paper URLs or full text if available
            if not arxiv_results:
                messages_to_add.append(AIMessage(content=f"Scraper: No arXiv results found for '{search_term}'."))

        except Exception as e:
            print(f"Scraper: Error during arXiv search: {e}")
            messages_to_add.append(AIMessage(content=f"Scraper: Error during arXiv search: {e}"))
    
    # --- PDF processing ---
    # This part assumes a PDF file exists locally (e.g., "temp.pdf")
    # In a real application, you'd integrate with a file upload or a more robust PDF source.
    if "filetype:pdf" in search_term.lower():
        print("Scraper: Attempting to extract text from PDF.")
        try:
            # This now calls the actual extract_text_from_pdf from tools/pdf_parser.py
            pdf_content = extract_text_from_pdf("temp.pdf") 
            if pdf_content:
                sources.append(pdf_content)
                messages_to_add.append(AIMessage(content="Scraper: Extracted content from PDF."))
            else:
                messages_to_add.append(AIMessage(content="Scraper: No content extracted from PDF (or PDF not found)."))
        except Exception as e:
            print(f"Scraper: Error during PDF extraction: {e}")
            messages_to_add.append(AIMessage(content=f"Scraper: Error during PDF extraction: {e}"))

    print(f"Scraper: Finished fetching. Total content pieces: {len(sources)}")

    # Return updates to the state.
    # 'scraped_content' uses operator.add, so new content will be appended.
    # 'messages' also uses operator.add, so new messages will be appended.
    return {
        "scraped_content": sources,
        "messages": messages_to_add
    }
