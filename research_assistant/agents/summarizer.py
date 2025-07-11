# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-06-15
# Purpose: Condense research materials
# Key Features:
#   - Map-reduce summarization
#   - Length control
#   - Key point extraction
#   - Correctly interacts with AgentState

from typing import TypedDict, List, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.chains.summarize import load_summarize_chain
# from langchain_openai import OpenAI # REMOVE or comment this line
# from langchain_community.llms import Ollama # REMOVE or comment this line
from langchain_google_genai import ChatGoogleGenerativeAI # ADD this line for Google Gemini
from langchain_core.documents import Document
import os # Added to access environment variables

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
    summarized_text: Optional[str] # This will store the final combined summary
    fact_check_results: Optional[str]
    citations: Annotated[List[str], operator.add]
    next_step: Optional[str]
    search_query_for_scraper: Optional[str]
    # If you want to control summary length from the coordinator, add it here:
    # summary_length: Optional[str]


def summarizer_agent(state: AgentState) -> dict:
    """
    Generates concise summaries from scraped content and updates the AgentState.

    Args:
        state (AgentState): The current state of the graph.

    Returns:
        dict: A dictionary containing updates to the state, specifically
              setting 'summarized_text'.
    """
    print("\n--- Summarizer Agent: Generating summaries ---")
    
    # Prioritize translated content if available, otherwise use scraped content
    content_to_summarize = state.get("translated_content")
    if not content_to_summarize:
        content_to_summarize = " ".join(state.get("scraped_content", []))
    
    if not content_to_summarize:
        print("Summarizer: No content found to summarize (neither translated nor scraped).")
        messages_to_add = [AIMessage(content="Summarizer: No content for summarization.")]
        return {
            "summarized_text": "Summary unavailable - No content to summarize",
            "messages": messages_to_add
        }

    # Prepare documents for the summarization chain
    docs = [Document(page_content=content_to_summarize)]
    
    if not docs:
        print("Summarizer: Content is empty or invalid for summarization.")
        messages_to_add = [AIMessage(content="Summarizer: Invalid content for summarization.")]
        return {
            "summarized_text": "Summary unavailable - Invalid content",
            "messages": messages_to_add
        }

    try:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            log_error("GOOGLE_API_KEY not found in .env. Cannot use Google Gemini for summarization.")
            messages_to_add = [AIMessage(content="Summarizer: Google API key missing. Summary unavailable.")]
            return {
                "summarized_text": "Summary unavailable - Google API Key missing",
                "messages": messages_to_add
            }

        # Explicitly using 'gemini-1.5-flash' for faster summarization
        model_name = "gemini-1.5-flash" 
        print(f"Summarizer: Attempting to use Google Gemini model: {model_name}")
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=0, google_api_key=google_api_key)
        
        # Using "map_reduce" for potentially large amounts of text
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        
        summary_length_param = "5 bullet points" # Defaulting for now

        # Run the summarization chain using .invoke()
        combined_summary_response = chain.invoke({"input_documents": docs})
        combined_summary = combined_summary_response.get("output_text", "") # Access the output text

        # Format the combined summary
        formatted_summary = _format_summary(combined_summary, summary_length_param)
        
        print(f"Summarizer: Summary generated ({len(formatted_summary)} chars).")
        messages_to_add = [AIMessage(content=f"Summarizer: Content summarized.")]

        # Return updates to the state
        return {
            "summarized_text": formatted_summary,
            "messages": messages_to_add
        }
    
    except Exception as e:
        log_error(f"Summarization failed: {e}")
        messages_to_add = [AIMessage(content=f"Summarizer: Summarization failed: {e}")]
        return {
            "summarized_text": "Summary unavailable due to error",
            "messages": messages_to_add
        }

def _format_summary(text: str, length: str) -> str:
    """Format summary based on requested length."""
    print(f"Summarizer: Formatting summary to '{length}'.")
    if "bullet" in length.lower():
        # Ensure points are split correctly and handle empty points
        points = [p.strip() for p in text.split(". ") if p.strip()]
        try:
            num_bullets = int(length.split()[0])
            return "\n- " + "\n- ".join(points[:num_bullets])
        except ValueError:
            log_error(f"Invalid summary length format: {length}. Returning raw text.")
            return text # Fallback to raw text if format is bad
    return text[:500] # Fallback truncation if no specific bullet instruction
