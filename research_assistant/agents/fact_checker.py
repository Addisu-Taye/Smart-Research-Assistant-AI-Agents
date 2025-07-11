# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-06-15
# Purpose: Validate claims in research summaries
# Key Features:
#   - Wolfram Alpha integration
#   - Claim-by-claim verification
#   - Result annotation
#   - Correctly interacts with AgentState

import os
import wolframalpha
from typing import TypedDict, List, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv() # Ensure environment variables are loaded for Wolfram Alpha APPID

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
    fact_check_results: Optional[str] # This will store the fact-checking output
    citations: Annotated[List[str], operator.add]
    next_step: Optional[str]
    search_query_for_scraper: Optional[str]
    # summary_length: Optional[str] # Uncomment if you add this to AgentState in main.py


def fact_checker_agent(state: AgentState) -> dict:
    """
    Verifies factual accuracy of the summarized text and updates the AgentState.

    Args:
        state (AgentState): The current state of the graph.

    Returns:
        dict: A dictionary containing updates to the state, specifically
              setting 'fact_check_results'.
    """
    print("\n--- Fact Checker Agent: Verifying claims ---")
    
    summarized_text = state.get("summarized_text")
    messages_to_add = []

    if not summarized_text:
        print("Fact Checker: No summarized text found to verify.")
        messages_to_add.append(AIMessage(content="Fact Checker: No summary for verification."))
        return {
            "fact_check_results": "Fact-checking unavailable - No summary",
            "messages": messages_to_add
        }

    wolfram_alpha_appid = os.getenv("WOLFRAM_ALPHA_APPID")

    if not wolfram_alpha_appid:
        print("WARNING: WOLFRAM_ALPHA_APPID not found in .env. Skipping real fact-checking.")
        messages_to_add.append(AIMessage(content="Fact Checker: WOLFRAM_ALPHA_APPID missing. Using mock verification."))
        # Fallback to mock results if API key is not set
        mock_fact_check = f"Mock Fact Check: '{summarized_text[:100]}...' [✅ - Mock Verified]"
        return {
            "fact_check_results": mock_fact_check,
            "messages": messages_to_add
        }

    try:
        client = wolframalpha.Client(wolfram_alpha_appid)
        verified_claims_with_status = []
        
        # Simple split by ". " might not be robust for all summaries.
        # Consider using a more advanced sentence tokenizer if needed.
        claims = [claim.strip() for claim in summarized_text.split(". ") if claim.strip()]
        
        if not claims:
            print("Fact Checker: No discernible claims found in summary.")
            messages_to_add.append(AIMessage(content="Fact Checker: No claims to verify."))
            return {
                "fact_check_results": "Fact-checking unavailable - No claims found",
                "messages": messages_to_add
            }

        for i, claim in enumerate(claims):
            print(f"Fact Checker: Verifying claim {i+1}/{len(claims)}: '{claim[:50]}...'")
            try:
                # Wolfram Alpha query for validation
                # The 'validate:' prefix might not always yield direct true/false.
                # You may need to parse Wolfram Alpha's pods for a more robust check.
                res = client.query(f"Is it true that {claim}?") 
                
                status_symbol = "❓" # Default to unknown
                if res and hasattr(res, 'pods'):
                    # Attempt to find a pod that indicates a clear answer
                    for pod in res.pods:
                        if pod.title in ["Result", "Answer", "Input interpretation", "Properties"]:
                            # A very basic check: if Wolfram Alpha provides any result, consider it verifiable
                            # A more robust check would involve parsing specific pod content.
                            status_symbol = "✅" 
                            break # Found a relevant pod, assume verifiable
                        elif pod.title in ["False", "Incorrect"]: # Example for explicit false
                             status_symbol = "❌"
                
                verified_claims_with_status.append(f"{claim} [{status_symbol}]")
                messages_to_add.append(AIMessage(content=f"Fact Checker: Claim '{claim[:50]}...' verified: {status_symbol}"))

            except Exception as claim_e:
                log_error(f"Fact-checking for claim '{claim[:50]}...' failed: {claim_e}")
                verified_claims_with_status.append(f"{claim} [❌ - Error]")
                messages_to_add.append(AIMessage(content=f"Fact Checker: Claim verification error for '{claim[:50]}...': {claim_e}"))
        
        final_fact_check_results = ". ".join(verified_claims_with_status)
        print(f"Fact Checker: Verification complete. Results: {final_fact_check_results[:200]}...")

        # Return updates to the state
        return {
            "fact_check_results": final_fact_check_results,
            "messages": messages_to_add
        }
    
    except Exception as e:
        log_error(f"Fact-checking process failed: {e}")
        messages_to_add.append(AIMessage(content=f"Fact Checker: Fact-checking process failed: {e}"))
        return {
            "fact_check_results": "Fact-checking unavailable due to error",
            "messages": messages_to_add
        }
