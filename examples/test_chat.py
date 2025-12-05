"""
Simple test script for the chat API.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_chat_flow():
    """Test the complete chat flow."""
    print("Testing Chat API Flow\n")
    
    session_id = None
    
    # Step 1: Initial message
    print("1️⃣ User: Hello!")
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "Hello!"
    })
    data = response.json()
    session_id = data["session_id"]
    print(f"   Bot: {data['message']}\n")
    
    # Step 2: Destination
    print("2️⃣ User: Rome")
    response = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "Rome"
    })
    data = response.json()
    print(f"   Bot: {data['message']}\n")
    
    # Step 3: Duration
    print("3️⃣ User: 3 days")
    response = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "3 days"
    })
    data = response.json()
    print(f"   Bot: {data['message']}\n")
    
    # Step 4: Interests
    print("4️⃣ User: Art and Food")
    response = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "Art and Food"
    })
    data = response.json()
    print(f"   Bot: {data['message']}\n")
    
    # Step 5: Budget
    print("5️⃣ User: Medium")
    response = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "Medium"
    })
    data = response.json()
    print(f"   Bot: {data['message']}\n")
    
    # Check if itinerary was generated
    if data.get("itinerary"):
        print("✅ Itinerary generated successfully!")
        itinerary = data["itinerary"]
        print(f"\n📋 Trip: {itinerary['trip_title']}")
        print(f"📝 Summary: {itinerary['summary']}\n")
        
        for day in itinerary["days"]:
            print(f"\n{'='*60}")
            print(f"📅 Day {day['day_number']}: {day['theme']}")
            print(f"{'='*60}")
            
            for i, act in enumerate(day['activities'], 1):
                print(f"\n{i}. {act['time_slot']} - {act['name']} ({act['duration']})")
                print(f"   💭 {act['description']}")
                print(f"   💰 Cost: {act['cost_estimate']}")
            
            print()
    else:
        print(f"⚠️  State: {data['state']}")
        print(f"   Needs more info: {data['needs_more_info']}")

if __name__ == "__main__":
    try:
        test_chat_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure the server is running:")
        print("   python run_api.py")
    except Exception as e:
        print(f"❌ Error: {e}")