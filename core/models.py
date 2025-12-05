"""Pydantic models for structured agent outputs."""

from pydantic import BaseModel, Field
from typing import List, Optional


class Fact(BaseModel):
    """A single interesting fact with source verification."""
    
    title: str = Field(description="Short fact title (max 10 words)")
    description: str = Field(description="Detailed explanation (2-3 sentences)")
    source_url: str = Field(description="URL of the official website where this was verified")
    verification_date: str = Field(description="Date when this information was last checked (e.g. 'Today')")


class ResearchOutput(BaseModel):
    """Structured output from destination research."""
    
    destination: str = Field(description="City or destination name")
    facts: List[Fact] = Field(description="List of verified facts")

class Activity(BaseModel):
    """A single planned activity in the itinerary."""
    name: str = Field(description="Name of the activity or location")
    description: str = Field(description="Brief description of what to do there")
    time_slot: str = Field(description="Suggested time (e.g., 'Morning', '14:00')")
    duration: str = Field(description="Estimated duration (e.g., '2 hours')")
    cost_estimate: str = Field(description="Estimated cost (e.g., '€20', 'Free')")

class DayPlan(BaseModel):
    """A full day schedule."""
    day_number: int = Field(description="Day sequence number (1, 2, 3...)")
    theme: str = Field(description="Theme of the day (e.g., 'Art & History')")
    activities: List[Activity] = Field(description="List of activities for this day")

class Itinerary(BaseModel):
    """The complete travel itinerary."""
    trip_title: str = Field(description="Catchy title for the trip")
    summary: str = Field(description="Brief summary of the whole trip experience")
    days: List[DayPlan] = Field(description="List of daily plans")