# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-07-10
# Purpose: Analyze the sentiment of scraped content
# Key Features:
#   - Takes scraped content from AgentState
#   - Returns sentiment analysis results to AgentState
#   - Placeholder for actual sentiment analysis logic
#   - Correctly interacts with AgentState

from typing import TypedDict, List, Annotated, Optional
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
    citations: Annotated[List[str], operator.add]
    next_step: Optional[str]
    search_query_for_scraper: Optional[str]

def sentiment_analyzer_agent(state: AgentState) -> dict:
    """
    Analyzes the sentiment of the scraped content and updates the AgentState.

    Args:
        state (AgentState): The current state of the graph.

    Returns:
        dict: A dictionary containing updates to the state, specifically
              setting 'sentiment_results'.
    """
    print("\n--- Sentiment Analyzer Agent: Analyzing sentiment ---")
    
    # Prioritize translated content for sentiment analysis if available
    content_for_sentiment = state.get("translated_content")
    if not content_for_sentiment:
        content_for_sentiment = " ".join(state.get("scraped_content", []))
    
    messages_to_add = []

    if not content_for_sentiment:
        print("Sentiment Analyzer: No content found for analysis (neither translated nor scraped).")
        messages_to_add.append(AIMessage(content="Sentiment Analyzer: No content for analysis."))
        return {
            "sentiment_results": "N/A - No content to analyze",
            "messages": messages_to_add
        }

    # --- Placeholder for actual sentiment analysis logic ---
    # In a real scenario, you would use an NLP library (e.g., NLTK, spaCy,
    # Hugging Face transformers with a pre-trained model) or an API
    # to determine the sentiment (positive, negative, neutral, mixed).
    
    # Mock sentiment analysis based on keywords for demonstration
    mock_sentiment = "Neutral"
    content_lower = content_for_sentiment.lower()
    if "positive" in content_lower or "benefits" in content_lower or "breakthrough" in content_lower:
        mock_sentiment = "Positive"
    elif "negative" in content_lower or "causes" in content_lower or "impact" in content_lower or "error" in content_lower:
        mock_sentiment = "Negative"
    elif "contribution" in content_lower or "research" in content_lower or "understanding" in content_lower:
        mock_sentiment = "Neutral/Informative"
    
    sentiment_output = f"Overall sentiment of the content: {mock_sentiment}"
    print(f"Sentiment Analyzer: Analysis complete. Result: {sentiment_output}")

    messages_to_add.append(AIMessage(content=f"Sentiment Analyzer: Sentiment analyzed as {mock_sentiment}."))

    # Return updates to the state
    return {
        "sentiment_results": sentiment_output,
        "messages": messages_to_add
    }
