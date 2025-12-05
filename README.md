# AI Travel Companion

Conversational AI travel planning system powered by CrewAI, Google Gemini, and PostgreSQL.

## Setup

# Install dependencies
pip install -r requirements.txt

# Setup .env file
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/travel_companion

# Initialize database
python init_db.py

# Run server
python run_api.py## Tech Stack

- FastAPI
- CrewAI
- Google Gemini 2.0 Flash
- PostgreSQL + SQLAlchemy
- Loguru

---

*Documentation in progress...*