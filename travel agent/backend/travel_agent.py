import json
import random

import os


# ---------------- MEMORY ----------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "travel_memory.json")


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "preferences": {},
            "past_trips": []
        }


def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


# ---------------- TOOLS ----------------

def search_transport(source, destination):
    print("[TOOL] Searching transport...")

    options = [
        {
            "type": "Bus",
            "price": 900,
            "duration": "12 hours"
        },
        {
            "type": "Train",
            "price": 1200,
            "duration": "11 hours"
        },
        {
            "type": "Flight",
            "price": 3500,
            "duration": "1.5 hours"
        }
    ]

    return options


def search_hotels(destination, preference):
    print("[TOOL] Searching hotels...")

    hotels = [
        {
            "name": "Beachside Hostel",
            "price_per_day": 800,
            "type": "Budget"
        },
        {
            "name": "Goa Comfort Hotel",
            "price_per_day": 1800,
            "type": "Standard"
        },
        {
            "name": "Ocean View Resort",
            "price_per_day": 3500,
            "type": "Luxury"
        }
    ]

    matching_hotels = [
        hotel for hotel in hotels
        if hotel["type"].lower() == preference.lower()
    ]

    # If no exact preference is found, return all hotels
    if not matching_hotels:
        return hotels

    return matching_hotels


def check_weather(destination):
    print("[TOOL] Checking weather...")

    weather = random.choice([
        "Sunny",
        "Partly cloudy",
        "Light rain"
    ])

    return weather


def calculate_budget(transport, hotel, days):
    hotel_cost = hotel["price_per_day"] * days

    # Round trip transport
    transport_cost = transport["price"] * 2

    total = transport_cost + hotel_cost

    return {
        "transport": transport_cost,
        "hotel": hotel_cost,
        "total": total
    }


# ---------------- PLANNING ----------------

def create_plan(goal, memory):

    print("[PLANNER] Creating travel plan...")

    transport_options = search_transport(
        goal["source"],
        goal["destination"]
    )

    hotels = search_hotels(
        goal["destination"],
        goal["preference"]
    )

    weather = check_weather(
        goal["destination"]
    )

    # Start with cheapest available options
    transport = min(
        transport_options,
        key=lambda x: x["price"]
    )

    hotel = min(
        hotels,
        key=lambda x: x["price_per_day"]
    )

    budget = calculate_budget(
        transport,
        hotel,
        goal["days"]
    )

    return {
        "transport": transport,
        "hotel": hotel,
        "weather": weather,
        "budget": budget
    }


# ---------------- REASONING ----------------

def reason_about_plan(plan, goal):

    print("[REASONER] Checking plan...")

    total = plan["budget"]["total"]

    if total <= goal["budget"]:
        print("[REASONER] Plan is within budget.")

        return {
            "valid": True,
            "message": "Plan is within budget."
        }

    print("[REASONER] Plan exceeds budget.")

    return {
        "valid": False,
        "message": "Plan exceeds the user's budget."
    }


# ---------------- RE-PLANNING ----------------

def replan(goal):

    print("[RE-PLANNER] Searching for a cheaper alternative...")

    transport_options = search_transport(
        goal["source"],
        goal["destination"]
    )

    # Re-planning uses the cheapest hotel category
    hotels = search_hotels(
        goal["destination"],
        "Budget"
    )

    # Try different combinations
    for transport in sorted(
        transport_options,
        key=lambda x: x["price"]
    ):

        for hotel in sorted(
            hotels,
            key=lambda x: x["price_per_day"]
        ):

            budget = calculate_budget(
                transport,
                hotel,
                goal["days"]
            )

            if budget["total"] <= goal["budget"]:

                print("[RE-PLANNER] Alternative found.")

                weather = check_weather(
                    goal["destination"]
                )

                return {
                    "transport": transport,
                    "hotel": hotel,
                    "weather": weather,
                    "budget": budget
                }

    print("[RE-PLANNER] No suitable alternative found.")

    return None


# ---------------- MAIN AGENT ----------------

def run_agent(goal):

    memory = load_memory()

    # Remember current preference
    memory["preferences"]["hotel"] = goal["preference"]

    print("\n[AGENT] Understanding travel request...")
    print("[AGENT] Goal identified.")

    # Initial planning
    plan = create_plan(
        goal,
        memory
    )

    # Reason about plan
    reasoning = reason_about_plan(
        plan,
        goal
    )

    # Re-plan if necessary
    if not reasoning["valid"]:

        print("[OBSERVATION] Initial plan failed.")

        plan = replan(goal)

        if plan is None:

            return {
                "success": False,
                "requires_approval": False,
                "message": "No suitable travel plan found within the given budget."
            }

    # Return plan for human approval
    return {
        "success": True,
        "requires_approval": True,
        "message": "Travel plan created successfully.",
        "plan": plan
    }


# ---------------- HUMAN APPROVAL ----------------

def approve_booking(goal, plan):

    memory = load_memory()

    print("[ACTION] Booking approved by user.")

    trip = {
        "destination": goal["destination"],
        "days": goal["days"],
        "cost": plan["budget"]["total"]
    }

    memory["past_trips"].append(trip)

    save_memory(memory)

    return {
        "success": True,
        "message": "Booking action completed successfully."
    }