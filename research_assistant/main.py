# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-06-15
# Purpose: Orchestrate the multi-agent research assistant workflow (CLI)
# Key Features:
#   - LangGraph-based agent coordination (now asynchronous)
#   - 7-agent pipeline (search, summarize, fact-check, etc.)
#   - Error handling and logging

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import asyncio # Import asyncio for running asynchronous code

# Import AgentState and setup_workflow from the new workflow_core.py
from workflow_core import AgentState, setup_workflow

load_dotenv()

# Suppress the transformers warning if you don't need PyTorch/TensorFlow/Flax
# os.environ["TRANSFORMERS_VERBOSITY"] = "error"


async def main_run():
    """
    Main asynchronous function to run the CLI research workflow.
    """
    app = setup_workflow()
    
    query = input("Enter research query: ")
    
    initial_state = {
        "query": query,
        "messages": [HumanMessage(content=f"Initial query: {query}")],
        "scraped_content": [],
        "sentiment_results": None,
        "translated_content": None,
        "summarized_text": None,
        "fact_check_results": None,
        "citations": [],
        "next_step": None,
        "search_query_for_scraper": query,
    }

    print("\nStarting research workflow...")
    try:
        result = await app.ainvoke(initial_state)
    except Exception as e:
        print(f"An error occurred during workflow execution: {e}")
        result = None
    
    if result:
        print("\nResearch Results:")
        print(f"Query: {result.get('query')}")
        print(f"Scraped Content (first 200 chars): {result.get('scraped_content')[0][:200] if result.get('scraped_content') and len(result.get('scraped_content')) > 0 and len(result.get('scraped_content')[0]) > 0 else 'N/A'}")
        print(f"Summarized Text: {result.get('summarized_text')}")
        print(f"Fact Check Results: {result.get('fact_check_results')}")
        print(f"Citations: {result.get('citations')}")
        print(f"Sentiment Results: {result.get('sentiment_results')}")
        print(f"Translated Content: {result.get('translated_content')}")
    else:
        print("Workflow did not complete successfully.")

if __name__ == "__main__":
    asyncio.run(main_run())
