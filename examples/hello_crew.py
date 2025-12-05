"""
Simple CLI demo for the Travel Companion AI system.
"""
from core.crew import run_travel_planning
from core.models import Itinerary


def display_itinerary(result):
    """Pretty-print the itinerary result."""
    print("\n" + "="*50)
    print("FINAL ITINERARY")
    print("="*50)
    
    if isinstance(result.pydantic, Itinerary):
        trip = result.pydantic
        print(f"Trip: {trip.trip_title}")
        print(f"Summary: {trip.summary}\n")
        
        for day in trip.days:
            print(f"Day {day.day_number}: {day.theme}")
            for act in day.activities:
                print(f"   - {act.time_slot}: {act.name} ({act.duration})")
                print(f"     Desc: {act.description}")
                print(f"     Cost: {act.cost_estimate}")
            print("-" * 20)
    else:
        print(f"ERROR - Output type mismatch: {type(result.pydantic)}")


if __name__ == "__main__":
    print("AI Travel Companion - Demo\n")
    
    # Get user input
    destination = input("Where do you want to travel? (default: Paris): ").strip()
    if not destination:
        destination = "Paris"
    
    duration = input("How many days? (default: 3): ").strip()
    if not duration:
        duration = "3"
    
    interests = input("Interests? (default: Art and History): ").strip()
    if not interests:
        interests = "Art and History"
    
    budget = input("Budget level (Low/Medium/High, default: Medium): ").strip()
    if not budget:
        budget = "Medium"
    
    print(f"\nPlanning a {duration}-day trip to {destination}...\n")
    
    # Run the crew with all preferences
    result = run_travel_planning(
        destination=destination,
        duration=duration,
        interests=interests,
        budget=budget
    )
    
    # Display results
    display_itinerary(result)
