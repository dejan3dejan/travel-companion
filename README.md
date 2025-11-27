# AI Travel Companion

Multi-agent AI system that plans personalized travel itineraries using **Gemini 2.0 Flash** with **live Google Search** capabilities.

## What it does

The system uses multiple specialized AI agents that collaborate to create complete trip plans:

- **Research Agent** - Discovers destinations, attractions, and restaurants using live Google Search
- **Budget Agent** - Filters options by price and calculates total trip cost
- **Planner Agent** - Creates day-by-day schedules with optimized routes
- **Critic Agent** - Reviews plans for logic errors and suggests improvements

All outputs are **Pydantic validated** for structured, reliable data.

## Tech Stack

- **CrewAI** - Multi-agent orchestration framework
- **Gemini 2.0 Flash** - Google's LLM (cheapest model, ~$0 for testing)
- **Google Search Grounding** - Live web search via Gemini API
- **Pydantic** - Data validation and structured outputs

## Setup

### 1. Clone and navigate to project
```bash
cd travel-companion
```

### 2. Create virtual environment
```bash
python -m venv venv
```

**Activate:**
- Windows: `.\venv\Scripts\Activate`
- Mac/Linux: `source venv/bin/activate`

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API key

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

Get your key from: https://aistudio.google.com/apikey

### 5. Run the demo
```bash
python hello_crew.py
```

## Example Output

The agent automatically calls Google Search and returns structured data:

```json
{
  "destination": "Paris",
  "facts": [
    {
      "title": "Louvre Museum Ticket Price",
      "description": "Standard adult admission is €22 online..."
    },
    {
      "title": "Louvre Museum Opening Hours Today",
      "description": "Thursday, November 27, 2025, open 9:00 AM to 6:00 PM..."
    }
  ]
}
```

## Project Structure

```
travel-companion/
├── core/
│   ├── models.py      # Pydantic schemas
│   └── tools.py       # Google Search tool
├── hello_crew.py      # Main demo script
├── requirements.txt
└── .env              # API keys (not in git)
```

## License

MIT

