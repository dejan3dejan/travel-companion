"""
Smart Chat API endpoint powered by Gemini LLM.
Replaces rigid state machine with an intelligent conversational agent.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import uuid
from datetime import datetime
import sys
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from core.logger import get_logger
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from core.database import get_db, ChatSession

logger = get_logger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crew import run_travel_planning
from core.models import Itinerary

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found")
genai.configure(api_key=api_key)

router = APIRouter()

# --- Data Models ---

class ChatMessage(BaseModel):
    """User message to the chat system."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    """Response from the chat system."""
    session_id: str
    message: str
    needs_more_info: bool
    state: str # 'collecting' | 'ready' | 'completed' | 'error'
    itinerary: Optional[dict] = None

# --- Structured Output for Conversation Manager ---

class TravelPreferences(BaseModel):
    """Current state of gathered travel preferences."""
    destination: Optional[str] = Field(None, description="City or region user wants to visit")
    duration: Optional[str] = Field(None, description="Number of days")
    interests: Optional[str] = Field(None, description="User interests (e.g., Art, Food)")
    budget: Optional[str] = Field(None, description="Budget level (Low, Medium, High)")

class ConversationStatus(BaseModel):
    """Structured output from the Chat Manager LLM."""
    response_to_user: str = Field(description="Natural language response to the user")
    updated_preferences: TravelPreferences = Field(description="Updated preferences based on conversation")
    missing_info: list[str] = Field(description="List of fields still missing (destination, duration, interests, budget)")
    is_ready: bool = Field(False, description="True only if ALL 4 fields are filled and valid")
    is_valid_destination: bool = Field(True, description="False if user asks for a fake place like Narnia or Gotham")
    is_off_topic: bool = Field(False, description="True if user is asking non-travel questions")

# --- Logic ---

def get_conversation_manager():
    """Returns the configured Gemini model for conversation management."""
    system_prompt = """
    You are an expert, charming AI Travel Consultant.
    
    YOUR GOAL:
    Collect 4 key pieces of information from the user to plan a perfect trip:
    1. **Destination** (City/Country) - MUST be a real place on Earth.
    2. **Duration** (How many days) - e.g., "3 days", "one week".
    3. **Interests** (What they like) - e.g., "Art", "Food", "Hiking".
    4. **Budget** (Low/Medium/High) - Infer from context if possible (e.g. "cheap" = Low).

    CURRENT CONTEXT:
    User has provided: {current_data}

    INSTRUCTIONS:
    1. **Analyze** the user's latest message. Extract any new information.
    2. **Validate** the destination immediately. If the user says "Narnia", "Gotham", or nonsense, politely reject it in `response_to_user` and set `is_valid_destination` to False.
    3. **Merge** new info with existing data.
    4. **Conversation:** 
       - If information is missing, ask for it naturally. Do NOT be a robot. Be conversational.
       - If user gives destination ("Paris"), react enthusiastically ("Paris is wonderful! How many days...?").
       - You can ask for multiple things, but don't overwhelm.
    5. **Completion:** Set `is_ready` to True ONLY when you have all 4 validated fields.

    OUTPUT FORMAT:
    Return a JSON object with this EXACT structure:
    {
        "response_to_user": "string",
        "updated_preferences": {
            "destination": "string or null",
            "duration": "string or null",
            "interests": "string or null",
            "budget": "string or null"
        },
        "missing_info": ["string", "string"],
        "is_ready": boolean,
        "is_valid_destination": boolean,
        "is_off_topic": boolean
    }
    """
    
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash-001",
        generation_config={
            "response_mime_type": "application/json"
        },
        system_instruction=system_prompt
    )

async def process_with_llm(user_message: str, current_data: dict) -> ConversationStatus:
    """Sends context to LLM and gets structured decision."""
    model = get_conversation_manager()
    
    # Construct the prompt with current state
    prompt = f"""
    Current Known Data: {json.dumps(current_data)}
    User's Latest Message: "{user_message}"
    
    Update the data and generate a response.
    """
    
    response = model.generate_content(prompt)
    
    # Parse JSON response
    try:
        return ConversationStatus.model_validate_json(response.text)
    except Exception as e:
        logger.error(f"LLM Parsing Error: {e}\nRaw text: {response.text}")
        # Fallback safe response
        return ConversationStatus(
            response_to_user="I'm having a little trouble understanding. Could we start over with where you want to go?",
            updated_preferences=TravelPreferences(),
            missing_info=["destination"],
            is_valid_destination=True,
            is_ready=False
        )

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage, db: Session = Depends(get_db)):
    """
    Smart Chat Endpoint.
    """
    # 1. Session Management
    session_id = chat_message.session_id or str(uuid.uuid4())
    
    db_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    
    if not db_session:
        # Create new session in database
        db_session = ChatSession(
            session_id=session_id,
            user_id=chat_message.user_id,
            data={
                "destination": None,
                "duration": None,
                "interests": None,
                "budget": None
            }
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
    
    user_text = chat_message.message.strip()
    
    # 2. AI Processing (The "Brain")
    # We pass the currently known data so the AI knows what's missing
    ai_decision = await process_with_llm(user_text, db_session.data)
    
    # Debug logging to see AI decision
    logger.info(f"AI Decision: is_ready={ai_decision.is_ready}, missing={ai_decision.missing_info}, current_data={db_session.data}, updated={ai_decision.updated_preferences.model_dump()}")
    
    # 3. Update Session State
    # Only update fields that are not None in the AI output
    preferences_dict = ai_decision.updated_preferences.model_dump()
    for key, value in preferences_dict.items():
        if value:
            db_session.data[key] = value
    
    # Tell SQLAlchemy that the JSON column was modified
    flag_modified(db_session, "data")
    db.commit()  # Save changes to database
    
    # Debug: verify data was saved
    logger.debug(f"After commit, db_session.data = {db_session.data}")
            
    # 4. Handle Logic based on AI decision
    
    # CASE A: Invalid Destination (e.g. Narnia)
    if not ai_decision.is_valid_destination:
        # Reset destination if it was invalid
        db_session.data["destination"] = None
        flag_modified(db_session, "data")
        db.commit()  # Save changes to database
        return ChatResponse(
            session_id=session_id,
            message=ai_decision.response_to_user, # AI will contain the polite rejection
            needs_more_info=True,
            state="collecting"
        )

    # CASE B: Ready to Plan!
    if ai_decision.is_ready:
        destination = db_session.data.get("destination")
        duration = db_session.data.get("duration")
        interests = db_session.data.get("interests")
        budget = db_session.data.get("budget")
        
        # Notify user we are starting
        # Note: In a real WebSocket app, we'd send this message immediately, then the result later.
        # For HTTP, we have to block. We'll append a notification to the AI's last words.
        
        try:
            logger.info(f"Starting CrewAI planning for {destination} with duration {duration}, interests {interests}, and budget {budget}")
            result = run_travel_planning(
                destination=destination,
                duration=duration,
                interests=interests,
                budget=budget
            )
            
            if isinstance(result.pydantic, Itinerary):
                itinerary_dict = result.pydantic.model_dump()
                db_session.itinerary = itinerary_dict
                flag_modified(db_session, "itinerary")
                db.commit()  # Save itinerary to database
                
                return ChatResponse(
                    session_id=session_id,
                    message=f"{ai_decision.response_to_user} (Generating your itinerary now... Done!)",
                    needs_more_info=False,
                    state="completed",
                    itinerary=itinerary_dict
                )
        except Exception as e:
            logger.error(f"CrewAI planning failed", error=str(e), destination=destination)
            return ChatResponse(
                session_id=session_id,
                message="I have all the info, but something went wrong generating the plan. Please try again.",
                needs_more_info=False,
                state="error"
            )

    # CASE C: Still collecting info
    return ChatResponse(
        session_id=session_id,
        message=ai_decision.response_to_user,
        needs_more_info=True,
        state="collecting"
    )

@router.get("/session/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Debug endpoint to see what the AI has collected."""
    db_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": db_session.session_id,
        "data": db_session.data,
        "itinerary": db_session.itinerary,
        "created_at": db_session.created_at,
        "updated_at": db_session.updated_at
    }
