# ==============================================
#   CONCIERGE MULTI-AGENT SYSTEM (Kaggle Project)
#   Works on: Python 3.10+
#   Features:
#     - Meal Planner Agent
#     - Travel Planner Agent
#     - Study Companion Agent
#     - Routine Automator Agent
#     - Health Agent
#     - Google AI Integration
#     - SQLite Database
#     - CLI Menu
# ==============================================

import os
import sqlite3
import json
import uuid
from datetime import datetime
from google import generativeai as genai

# ------------------------------------------
# GOOGLE AI STUDIO API SETUP
# ------------------------------------------
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE"   # <- PUT YOUR API KEY HERE
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ------------------------------------------
# DATABASE SETUP
# ------------------------------------------
DB = "agents.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS agents(
        id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        state_json TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_agent(agent):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO agents(id, name, type, state_json)
    VALUES (?, ?, ?, ?)
    """, (agent.id, agent.name, agent.type, json.dumps(agent.state)))
    conn.commit()
    conn.close()

def load_agents():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, name, type, state_json FROM agents")
    data = cur.fetchall()
    agents = []
    for row in data:
        a = BaseAgent(row[1], row[2], row[0])
        a.state = json.loads(row[3])
        agents.append(a)
    conn.close()
    return agents

# ------------------------------------------
# BASE AGENT CLASS
# ------------------------------------------
class BaseAgent:
    def __init__(self, name, agent_type, agent_id=None):
        self.name = name
        self.type = agent_type
        self.id = agent_id or str(uuid.uuid4())
        self.state = {}

    def ask_google_ai(self, prompt: str) -> str:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash-lite")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[Google AI Error]: {e}"

# ------------------------------------------
# AGENTS
# ------------------------------------------
class MealPlannerAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name, "MealPlanner")

    def generate_meal(self, day: str) -> str:
        meal = self.ask_google_ai(f"Create a healthy 1-day meal plan for {day}.")
        self.state[day] = meal
        save_agent(self)
        return meal

class TravelPlannerAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name, "TravelPlanner")

    def plan_trip(self, city: str) -> str:
        plan = self.ask_google_ai(f"Create a 2-day travel itinerary for {city}.")
        self.state["trip"] = plan
        save_agent(self)
        return plan

class StudyCompanionAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name, "StudyCompanion")

    def generate_notes(self, topic: str) -> str:
        notes = self.ask_google_ai(f"Explain {topic} in simple language.")
        self.state[topic] = notes
        save_agent(self)
        return notes

class RoutineAutomatorAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name, "RoutineAutomator")

    def generate_routine(self) -> str:
        routine = self.ask_google_ai("Create a productive daily routine for a student.")
        self.state["routine"] = routine
        save_agent(self)
        return routine

class HealthAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name, "HealthAgent")

    def health_advice(self, problem: str) -> str:
        advice = self.ask_google_ai(f"Give general health advice for: {problem}")
        self.state["advice"] = advice
        save_agent(self)
        return advice

# ------------------------------------------
# CLI MENU
# ------------------------------------------
def main_menu():
    init_db()
    print("\n===== CONCIERGE MULTI-AGENT SYSTEM =====")
    while True:
        print("\n1. Create Meal Plan")
        print("2. Plan Travel")
        print("3. Generate Study Notes")
        print("4. Create Daily Routine")
        print("5. Get Health Advice")
        print("6. Show All Saved Agents")
        print("7. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            agent = MealPlannerAgent("MealBot")
            day = input("Enter day name: ").strip()
            print("\nMeal Plan:\n", agent.generate_meal(day))

        elif choice == "2":
            agent = TravelPlannerAgent("TravelBot")
            city = input("Enter city: ").strip()
            print("\nTravel Plan:\n", agent.plan_trip(city))

        elif choice == "3":
            agent = StudyCompanionAgent("StudyBot")
            topic = input("Enter topic: ").strip()
            print("\nStudy Notes:\n", agent.generate_notes(topic))

        elif choice == "4":
            agent = RoutineAutomatorAgent("RoutineBot")
            print("\nDaily Routine:\n", agent.generate_routine())

        elif choice == "5":
            agent = HealthAgent("HealthBot")
            problem = input("Enter health problem: ").strip()
            print("\nHealth Advice:\n", agent.health_advice(problem))

        elif choice == "6":
            agents = load_agents()
            if not agents:
                print("No agents saved yet.")
            for a in agents:
                print(f"{a.name} ({a.type}) → {json.dumps(a.state, indent=2)}")

        elif choice == "7":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Enter a number 1-7.")

# ------------------------------------------
# RUN
# ------------------------------------------
if __name__ == "__main__":
    main_menu()

