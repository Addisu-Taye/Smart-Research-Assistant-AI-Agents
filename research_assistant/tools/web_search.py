# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-07-10
# Purpose: Provide web search functionality for agents
# Key Features:
#   - Mock implementation for testing
#   - Instructions for integrating real APIs (e.g., SerpAPI)

import os
import requests
from dotenv import load_dotenv
from typing import List

load_dotenv() # Load environment variables from .env file

def search_web(query: str) -> List[str]:
    """
    Performs a web search and returns a list of relevant text snippets.
    
    This function currently provides mock results. To enable real web search,
    you need to integrate with a web search API like SerpAPI.
    
    Args:
        query (str): The search query.
        
    Returns:
        List[str]: A list of text snippets from the search results.
    """
    print(f"Web Search Tool: Searching for '{query}'...")

    # --- SerpAPI Integration (Requires SERPAPI_API_KEY in .env) ---
    # Go to https://serpapi.com/ to get your API key.
    # Add SERPAPI_API_KEY="your_api_key_here" to your .env file.
    
    serpapi_api_key = "4357bc688f0826a5cc6fa6018677fbbc7fa6ac01de60a99e7f45a62ae8e6f91d"
    #os.getenv("SERPAPI_API_KEY")

    # --- DEBUGGING STEP: Print the loaded API key (masked for security) ---
    if serpapi_api_key:
        print(f"Web Search Tool: Loaded API Key (first 5 chars): {serpapi_api_key[:5]}*****")
    else:
        print("Web Search Tool: API Key not loaded (serpapi_api_key is None).")
    # --- END DEBUGGING STEP ---

    if not serpapi_api_key or serpapi_api_key == "your_serpapi_key_here": # Added check for placeholder
        print("WARNING: SERPAPI_API_KEY not found or is placeholder in .env. Using mock web search results.")
        # Fallback to mock results if API key is not set or is the placeholder
        mock_results = [
            f"Mock web result for '{query}': This is a placeholder snippet. "
            "To get real search results, please set SERPAPI_API_KEY in your .env file.",
            f"Another mock result for '{query}': Simulated data. "
            "Real data requires a configured API key."
        ]
        return mock_results

    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": serpapi_api_key,
        "engine": "google", # You can change this to "bing", "duckduckgo", etc.
        "num": 5 # Number of results to fetch
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        snippets = []
        if "organic_results" in data:
            for result in data["organic_results"]:
                if "snippet" in result:
                    snippets.append(result["snippet"])
        
        print(f"Web Search Tool: Found {len(snippets)} real results via SerpAPI.")
        return snippets

    except requests.exceptions.RequestException as e:
        print(f"Web Search Tool: Error fetching from SerpAPI: {e}")
        # Fallback to mock results on API error
        mock_results_on_error = [
            f"Mock web result (due to API error) for '{query}': "
            "Could not fetch real results. Please check your internet connection or API key.",
            "Simulated fallback data."
        ]
        return mock_results_on_error
    except Exception as e:
        print(f"Web Search Tool: An unexpected error occurred: {e}")
        mock_results_on_error = [
            f"Mock web result (due to unexpected error) for '{query}': "
            "An unexpected error occurred. Please check logs.",
            "Simulated fallback data."
        ]
        return mock_results_on_error

