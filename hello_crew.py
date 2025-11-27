import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from core.models import ResearchOutput
from core.tools import google_search

# Load environment variables
load_dotenv()

# Validate API key
if not os.getenv("GEMINI_API_KEY"):
    print("ERROR: GEMINI_API_KEY not found in .env file!")
    exit(1)

# Disable OpenAI check (we're using Gemini)
os.environ["OPENAI_API_KEY"] = "NA"

# Define Research Agent
researcher = Agent(
    role='Travel Researcher',
    goal='Discover current, accurate information about {topic}',
    backstory='You are a meticulous travel researcher who always verifies facts with live data sources.',
    verbose=True,
    allow_delegation=False,
    llm="gemini/gemini-2.0-flash-001",
    tools=[google_search]
)

# Define Task
research_task = Task(
    description='Research current information about {topic}. Find the exact ticket price for the Louvre Museum and its opening hours today.',
    expected_output='A structured list with at least one fact containing live data (price or hours).',
    agent=researcher,
    output_pydantic=ResearchOutput
)

# Create Crew
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True,
    process=Process.sequential
)

# Execute
if __name__ == "__main__":
    print("🤖 Starting agent execution...\n")
    result = crew.kickoff(inputs={'topic': 'Paris'})

    # Display results
    print("\n" + "="*50)
    print("AGENT RESULTS")
    print("="*50)
    print(f"Type: {type(result.pydantic)}")
    print(f"Destination: {result.pydantic.destination}")
    print(f"Facts found: {len(result.pydantic.facts)}\n")
    
    for i, fact in enumerate(result.pydantic.facts, 1):
        print(f"{i}. {fact.title}")
        print(f"   {fact.description}\n")