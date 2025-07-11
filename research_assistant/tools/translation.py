# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-07-10
# Purpose: Translate scraped content if required
# Key Features:
#   - Takes scraped content from AgentState
#   - Returns translated content to AgentState
#   - Integrates with googletrans for actual translation (requires installation)
#   - Correctly interacts with AgentState

from typing import TypedDict, List, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from googletrans import Translator # Now actively used

# Placeholder for log_error if it's not defined elsewhere
def log_error(message: str):
    print(f"ERROR: {message}")

# Re-define AgentState for type hinting within this agent, matching main.py
class AgentState(TypedDict):
    query: str
    messages: Annotated[List[BaseMessage], operator.add]
    scraped_content: Annotated[List[str], operator.add]
    sentiment_results: Optional[str]
    translated_content: Optional[str] # This will store the translated output
    summarized_text: Optional[str]
    fact_check_results: Optional[str]
    citations: Annotated[List[str], operator.add]
    next_step: Optional[str]
    search_query_for_scraper: Optional[str]
    # Add a flag if you want the coordinator to explicitly tell the translator
    # translation_required: Optional[bool]
    # target_language: Optional[str] # Defaulting to 'en' if not set by coordinator


def translator_agent(state: AgentState) -> dict:
    """
    Translates the scraped content if translation is deemed necessary,
    and updates the AgentState.

    Args:
        state (AgentState): The current state of the graph.

    Returns:
        dict: A dictionary containing updates to the state, specifically
              setting 'translated_content'.
    """
    print("\n--- Translator Agent: Translating content ---")
    
    scraped_content = state.get("scraped_content", [])
    messages_to_add = []
    
    # You might have a 'translation_required' flag or 'target_language' in AgentState
    # set by the coordinator based on the initial query or detected language.
    # For now, we'll assume translation is always attempted if content exists,
    # and default to English as the target language.
    target_lang = "en" # Default target language

    if not scraped_content:
        print("Translator: No scraped content found to translate.")
        messages_to_add.append(AIMessage(content="Translator: No content for translation."))
        return {
            "translated_content": "Translation unavailable - No content",
            "messages": messages_to_add
        }

    # Combine all scraped content into a single string for translation
    full_content_to_translate = " ".join(scraped_content)
    
    translated_text = ""
    try:
        # Using googletrans for actual translation
        # Note: googletrans is an unofficial API and might be unstable.
        # For production, consider official Google Cloud Translation API or similar.
        translator = Translator()
        # Ensure the content is not too long for the translator
        # Googletrans might have limits or perform better on smaller chunks
        chunk_size = 5000 # Translate in chunks if content is very long
        translated_chunks = []
        for i in range(0, len(full_content_to_translate), chunk_size):
            chunk = full_content_to_translate[i:i+chunk_size]
            translated_obj = translator.translate(chunk, dest=target_lang)
            translated_chunks.append(translated_obj.text)
        translated_text = " ".join(translated_chunks)
        
        print(f"Translator: Content translated to '{target_lang}' ({len(translated_text)} chars).")
        messages_to_add.append(AIMessage(content=f"Translator: Content translated to {target_lang}."))

    except Exception as e:
        log_error(f"Translation failed: {e}")
        messages_to_add.append(AIMessage(content=f"Translator: Translation failed: {e}"))
        translated_text = "Translation unavailable due to error"

    # Return updates to the state
    return {
        "translated_content": translated_text,
        "messages": messages_to_add
    }
