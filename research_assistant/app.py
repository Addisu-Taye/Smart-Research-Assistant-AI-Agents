# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-07-11
# Purpose: Provide a FastAPI backend for the research assistant workflow
# Key Features:
#   - Exposes a /research endpoint
#   - Runs the LangGraph workflow asynchronously
#   - Returns research results as JSON
#   - Handles CORS for frontend communication

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

# Import AgentState and setup_workflow from the new workflow_core.py
from workflow_core import AgentState, setup_workflow

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Research Assistant API",
    description="API for the AI-powered research assistant workflow."
)

# Configure CORS to allow requests from your React frontend
# Adjust origins as needed for your development and production environments
origins = [
    "http://localhost:3000",  # Default React development server port
    "http://127.0.0.1:3000",
    # Add your production frontend URL here when deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body model
class ResearchQuery(BaseModel):
    query: str

# Initialize the LangGraph application once on startup
# This avoids recompiling the graph for every request
research_app = setup_workflow()

@app.post("/research")
async def get_research_results(research_query: ResearchQuery):
    """
    Endpoint to trigger the research workflow and get results.
    """
    print(f"\nAPI Request received for query: {research_query.query}")
    
    initial_state = {
        "query": research_query.query,
        "messages": [HumanMessage(content=f"Initial query: {research_query.query}")],
        "scraped_content": [],
        "sentiment_results": None,
        "translated_content": None,
        "summarized_text": None,
        "fact_check_results": None,
        "citations": [],
        "next_step": None,
        "search_query_for_scraper": research_query.query,
    }

    try:
        # Invoke the asynchronous LangGraph workflow
        result = await research_app.ainvoke(initial_state)
        
        # Format the result for the frontend
        formatted_result = {
            "query": result.get("query"),
            "scraped_content": result.get("scraped_content"),
            "summarized_text": result.get("summarized_text"),
            "fact_check_results": result.get("fact_check_results"),
            "citations": result.get("citations"),
            "sentiment_results": result.get("sentiment_results"),
            "translated_content": result.get("translated_content"),
        }
        
        print("API Request processed successfully.")
        return formatted_result

    except Exception as e:
        print(f"An error occurred during API request processing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# To run this FastAPI app:
# 1. Save this file as app.py
# 2. Install FastAPI and Uvicorn: pip install fastapi uvicorn
# 3. Run from your terminal: uvicorn app:app --reload --port 8000
