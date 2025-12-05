"""
Task definitions for the Travel Companion agents.
"""
from crewai import Task
from .models import ResearchOutput, Itinerary


def create_research_task(agent, destination):
    """
    Creates the research task with strict verification protocols.
    
    Args:
        agent: The research agent to assign this task to
        destination: The destination to research
    """
    return Task(
        description=f"""Conduct a rigorous data extraction for: {{destination}}.
        
        CRITICAL RULE - DESTINATION VALIDATION:
        First, verify that "{{destination}}" is a REAL, RECOGNIZED travel destination.
        If you cannot find ANY credible travel information about "{{destination}}" after searching:
        - Return an error in the facts list with title "Invalid Destination"
        - Include description: "No verifiable travel data found for this location"
        - DO NOT PROCEED with fake data
        
        EXECUTION PROTOCOL (only if destination is valid):
        1. Source Identification: Use Google Search to locate official websites updated within the last 3 months.
        2. Data Verification: Locate the EXACT current ticket price for the main museum/attraction and opening hours for today.
        3. Cross-Referencing: If data seems outdated, perform a secondary search specifically for "price 2025".
        4. Citation: You MUST extract the URL of the page where you found the price/hours.
        
        CRITICAL CONSTRAINTS:
        - If exact data is unavailable, state "Data Unavailable". DO NOT GUESS.
        - Provide the exact Source URL for every fact.
        - Do not include marketing fluff. Only hard facts.
        - If destination is not recognized (gibberish, made-up place), FAIL EXPLICITLY.""",
        expected_output='A structured list with verified live data, dates, and source URLs. If destination is invalid, return error fact.',
        agent=agent,
        output_pydantic=ResearchOutput
    )


def create_planning_task(agent, research_task, destination, duration, interests, budget):
    """
    Creates the planning task that generates itineraries.
    
    Args:
        agent: The planner agent to assign this task to
        research_task: The research task to use as context (RAG)
        destination: The destination city
        duration: Number of days for the trip
        interests: User's travel interests
        budget: User's budget level
    """
    return Task(
        description=f"""Create a beautiful, realistic {{duration}}-day itinerary for: {{destination}}.

        USER PREFERENCES (MUST FOLLOW):
        - Destination: {{destination}}
        - Duration: {{duration}} days
        - Interests: {{interests}}
        - Budget: {{budget}}

        CRITICAL VALIDATION:
        First, check the Research Agent output. If it contains an error fact with "Invalid Destination" or "No verifiable travel data", 
        you MUST STOP and return an error itinerary with trip_title="Error: Invalid Destination" and empty days array.
        DO NOT CREATE A GENERIC ITINERARY FOR INVALID DESTINATIONS.

        Use the verified research data as priority for prices, opening hours and official names.

        You are allowed (and expected) to include all classic, must-see landmarks and experiences that every visitor wants, even if the researcher didn't explicitly return them.

        UNIVERSAL PERFECTION RULES (apply everywhere):
        1. RESPECT THE DURATION: Create exactly {{duration}} days, not 3 days.
        2. RESPECT THE INTERESTS: Prioritize activities matching "{{interests}}".
        3. RESPECT THE BUDGET: Adjust restaurant/activity cost to "{{budget}}" level.
        4. Schedule the #1 landmark at opening or golden hour to avoid crowds.
        5. For every popular attraction with queues, add "book skip-the-line / timed tickets in advance".
        6. Include one signature "wow" experience (boat cruise, viewpoint at night, cable car, etc.).
        7. Add 1-2 excellent but slightly less-touristy spots that fit the theme.
        8. Choose the most atmospheric neighborhoods for dinners.
        9. Keep daily walking under 10 km and group geographically.
        10. Art & Culture trips MUST include at least one Impressionist/Post-Impressionist museum 
        (Musee d'Orsay, Orangerie, Marmottan, etc.) unless the destination genuinely has none.
        11. Never schedule more than 4 paid attractions per day and keep total transport time under 45 min/day.

        Output must be perfect JSON matching the Itinerary schema.""",
        expected_output=f"A complete, beautiful {duration}-day JSON itinerary tailored to user preferences",
        agent=agent,
        context=[research_task],
        output_pydantic=Itinerary
    )

