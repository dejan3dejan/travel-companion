import os
from crewai.tools import tool
from google import genai


@tool("Google Search Tool")
def google_search(query: str) -> str:
    """
    Search Google for current information using Gemini's grounding feature.
    
    Use this tool when you need real-time data such as:
    - Current prices
    - Opening hours
    - Recent events
    - Any information that changes frequently
    
    Args:
        query: Search query (e.g., "Louvre Museum ticket price 2025")
    
    Returns:
        Search results as formatted text
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Use Gemini with Google Search grounding
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=query,
        config={
            'tools': [{'google_search': {}}]
        }
    )
    
    return response.text