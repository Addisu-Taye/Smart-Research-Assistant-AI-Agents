# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-06-15
# Purpose: Break down research queries into tasks and manage workflow flow
# Key Features:
#   - Query decomposition
#   - Task prioritization
#   - Workflow control (deciding when to continue or end)

from typing import TypedDict, List, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Define the AgentState structure again for type hinting within this agent.
# It must match the AgentState defined in main.py
class AgentState(TypedDict):
    query: str
    messages: Annotated[List[BaseMessage], operator.add]
    scraped_content: Annotated[List[str], operator.add]
    sentiment_results: Optional[str]
    translated_content: Optional[str]
    summarized_text: Optional[str]
    fact_check_results: Optional[str]
    citations: Annotated[List[str], operator.add]
    next_step: Optional[str] # This is crucial for controlling the graph flow

def research_coordinator(state: AgentState) -> dict:
    """
    Coordinates the research process, preparing tasks and deciding the next workflow step.

    This agent receives the current state of the graph, processes it, and
    returns updates to the state, including the 'next_step' to control
    the conditional routing in the main workflow.

    Args:
        state (AgentState): The current state of the graph, containing the query
                            and results from previous agents.

    Returns:
        dict: A dictionary containing updates to the state.
              Crucially, it sets the 'next_step' field to either
              "continue_research" or "end_research".
    """
    print("\n--- Coordinator Agent: Processing and deciding next step ---")

    current_query = state.get("query", "")
    current_messages = state.get("messages", [])
    current_scraped_content = state.get("scraped_content", [])
    current_summary = state.get("summarized_text")
    current_fact_check = state.get("fact_check_results")
    current_citations = state.get("citations", [])

    # Initialize updates dictionary
    updates = {}

    # --- Task Decomposition/Prioritization (Example Logic) ---
    # In a real scenario, this agent would use an LLM to decide what to do.
    # For now, we'll use simple rule-based logic.

    # If this is the very first entry, or we just came from citations,
    # we need to start/continue the main research cycle (scraping).
    if not current_scraped_content or (current_citations and not current_summary):
        print(f"Coordinator: Initializing/Continuing research for query: {current_query}")
        updates["next_step"] = "continue_research"
        # You might also set initial task parameters here, which other agents would then read
        # For example, if you want to pass a specific search query to the scraper:
        # updates["search_query_for_scraper"] = f"{current_query} latest findings"
        
        # Add a message to the history for tracing
        updates["messages"] = [AIMessage(content=f"Coordinator: Initiating web scraping for '{current_query}'.")]

    # If we have scraped content and a summary, and fact-checking/citations are done,
    # we can consider ending the research.
    elif current_scraped_content and current_summary and current_fact_check and current_citations:
        print("Coordinator: All research phases seem complete. Preparing final output.")
        updates["next_step"] = "end_research"
        updates["messages"] = [AIMessage(content="Coordinator: Research complete. Finalizing results.")]
    else:
        # Fallback for unexpected states, or if more iteration is needed but not explicitly handled above
        # For a simple linear flow, this should ideally not be hit if conditions are well-defined.
        print("Coordinator: Unsure of next step or more iteration needed. Defaulting to continue.")
        updates["next_step"] = "continue_research"
        updates["messages"] = [AIMessage(content="Coordinator: Continuing workflow (default).")]

    # The coordinator might also update other fields in the state for subsequent agents
    # For example, setting the 'summary_length' or 'citation_style' based on query analysis.
    # updates["summary_length"] = "5 bullet points"
    # updates["citation_style"] = "APA"
    # updates["translation_required"] = False # Or based on query language detection

    return updates

