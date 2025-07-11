# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-07-11
# Purpose: Define shared AgentState and workflow setup for research assistant
# Key Features:
#   - AgentState TypedDict for consistent state management
#   - setup_workflow function to build the LangGraph
#   - Reusable by both CLI (main.py) and API (app.py)

from typing import TypedDict, List, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Import all agents
from agents import (
    research_coordinator,
    web_scraper_agent,
    summarizer_agent,
    fact_checker_agent,
    citation_formatter_agent,
    sentiment_analyzer_agent,
    translator_agent
)

# Define the state for the LangGraph workflow
class AgentState(TypedDict):
    """
    Represents the state of our graph.
    Each key is an attribute of the state that can be read and updated by nodes.
    """
    query: str
    messages: Annotated[List[BaseMessage], operator.add]
    scraped_content: Annotated[List[str], operator.add]
    sentiment_results: Optional[str]
    translated_content: Optional[str]
    summarized_text: Optional[str]
    fact_check_results: Optional[str]
    citations: Annotated[List[str], operator.add]
    next_step: Optional[str]
    search_query_for_scraper: Optional[str]


def should_continue_research(state: AgentState) -> str:
    """
    Determines whether the research workflow should continue or end.
    """
    if state.get("next_step") == "end_research":
        return "end_research"
    return "continue_research"


def setup_workflow():
    """
    Initializes and configures the multi-agent research assistant workflow using LangGraph.
    """
    workflow = StateGraph(AgentState)
    
    agents = {
        "coordinator": research_coordinator,
        "scraper": web_scraper_agent,
        "sentiment_analyzer": sentiment_analyzer_agent,
        "translator": translator_agent,
        "summarizer": summarizer_agent,
        "fact_checker": fact_checker_agent,
        "citation_formatter": citation_formatter_agent
    }
    
    for name, agent in agents.items():
        workflow.add_node(name, agent)
    
    edges = [
        ("scraper", "sentiment_analyzer"),
        ("sentiment_analyzer", "translator"),
        ("translator", "summarizer"),
        ("summarizer", "fact_checker"),
        ("fact_checker", "citation_formatter"),
    ]
    
    for src, dst in edges:
        workflow.add_edge(src, dst)
    
    workflow.set_entry_point("coordinator")
    
    workflow.add_conditional_edges(
        "coordinator",
        should_continue_research,
        {
            "continue_research": "scraper",
            "end_research": END
        }
    )
    
    return workflow.compile()
