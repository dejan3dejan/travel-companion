from pydantic import BaseModel, Field
from typing import List


class Fact(BaseModel):
    """A single interesting fact about a destination."""
    
    title: str = Field(description="Short fact title (max 10 words)")
    description: str = Field(description="Detailed explanation (2-3 sentences)")


class ResearchOutput(BaseModel):
    """Structured output from destination research."""
    
    destination: str = Field(description="City or destination name")
    facts: List[Fact] = Field(description="List of 3 interesting facts")