"""
Main Crew orchestration for the Travel Companion system.
"""
import os
from crewai import Crew, Process
from dotenv import load_dotenv
from .agents import create_research_agent, create_planner_agent
from .tasks import create_research_task, create_planning_task
from .logger import get_logger

logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Validate API key
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("ERROR: GEMINI_API_KEY not found in .env file!")

# Disable OpenAI check (we're using Gemini)
os.environ["OPENAI_API_KEY"] = "NA"


def create_travel_crew(destination: str, duration: str, interests: str, budget: str):
    """
    Creates and returns the configured Travel Companion crew.
    
    Args:
        destination: City or destination name
        duration: Number of days for the trip
        interests: User's travel interests
        budget: Budget level (Low/Medium/High)
    
    Returns:
        Crew: Configured crew with research and planning agents
    """
    # Create agents
    researcher = create_research_agent()
    planner = create_planner_agent()
    
    # Create tasks with user preferences
    research_task = create_research_task(researcher, destination)
    planning_task = create_planning_task(planner, research_task, destination, duration, interests, budget)
    
    # Create and return crew
    return Crew(
        agents=[researcher, planner],
        tasks=[research_task, planning_task],
        verbose=True,
        process=Process.sequential
    )


def run_travel_planning(destination: str, duration: str = "3", interests: str = "general", budget: str = "medium"):
    logger.info(f"Creating crew for {destination} with duration {duration}, interests {interests}, and budget {budget}")
    """
    Executes the travel planning workflow for a given destination.
    
    Args:
        destination: City or destination name (e.g., "Paris", "Rome")
        duration: Number of days for the trip (default: "3")
        interests: User's travel interests (default: "general")
        budget: Budget level - Low/Medium/High (default: "medium")
    
    Returns:
        CrewOutput: Result containing the Itinerary object
    """
    crew = create_travel_crew(destination, duration, interests, budget)
    logger.debug("Crew created, starting kickoff")

    result = crew.kickoff(inputs={
        'destination': destination,
        'duration': duration,
        'interests': interests,
        'budget': budget
    })

    logger.info("Crew execution completed", destination=destination)
    return result