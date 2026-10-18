
"""
Trip Planning System with Human-in-the-Loop

This script demonstrates a simple HITL system for planning a trip
with three steps:
1. Destination selection with LLM suggestion
2. Flight selection with LLM suggestion
3. Itinerary generation with LLM suggestion

Each step includes human verification and modification options.

Note: Flights are fictional examples, not real flight listings.
"""

import os
from pathlib import Path
from typing import List
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field


# Load the OpenAI API key from the .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Verify the API key is loaded
print("ENV file found:", env_path.exists())
print("API key loaded:", bool(os.getenv("OPENAI_API_KEY")))


class FlightInfo(BaseModel):
    """Model for flight information."""

    flight_number: str = Field(description="Flight number")
    departure_time: str = Field(
        description="Departure time in HH:MM format"
    )
    arrival_time: str = Field(
        description="Arrival time in HH:MM format"
    )
    airline: str = Field(description="Name of the airline")


class Itinerary(BaseModel):
    """Model for daily itinerary."""

    daily_activities: List[List[str]] = Field(
        description="List of activities for each day of the trip"
    )


@dataclass
class TripPlan:
    """Represents a complete trip plan."""

    destination: str
    departure_city: str
    flight_info: FlightInfo
    itinerary: Itinerary


class TripPlanner:

    def __init__(self):
        """Initialize the trip planner."""

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.trip_plan = None

    def suggest_destination(self) -> str:
        """Use LLM to suggest a travel destination."""

        prompt = """
        Suggest an interesting travel destination.
        Consider factors like weather, tourist attractions,
        and cultural experiences.

        Return only the destination name, nothing else.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful travel assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error getting destination suggestion: {e}")
            return "Paris"  # Fallback destination

    def suggest_flight(
        self, departure_city: str, destination: str
    ) -> FlightInfo:
        """Use LLM to suggest a fictional flight."""

        prompt = f"""
        Generate a fictional flight from {departure_city}
        to {destination}.

        Include:
        - Flight number
        - Departure time
        - Arrival time
        - Airline

        This is a fictional example for a programming exercise.
        """

        try:
            response = self.client.responses.parse(
                model="gpt-4o-mini-2024-07-18",
                input=[
                    {
                        "role": "system",
                        "content": "You are a helpful travel assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                text_format=FlightInfo
            )

            if response.output_parsed is None:
                raise ValueError("No flight information returned.")

            return response.output_parsed

        except Exception as e:
            print(f"Error getting flight suggestion: {e}")

            return FlightInfo(
                flight_number="AA123",
                departure_time="10:00",
                arrival_time="12:00",
                airline="Example Airlines"
            )

    def generate_itinerary(self, destination: str) -> Itinerary:
        """Use LLM to generate a brief 3-day itinerary."""

        prompt = f"""
        Generate a brief 3-day itinerary for {destination}.

        Include 2-3 activities per day.
        Return exactly 3 days of activities.
        """

        try:
            response = self.client.responses.parse(
                model="gpt-4o-mini-2024-07-18",
                input=[
                    {
                        "role": "system",
                        "content": "You are a helpful travel assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                text_format=Itinerary
            )

            if response.output_parsed is None:
                raise ValueError("No itinerary returned.")

            return response.output_parsed

        except Exception as e:
            print(f"Error generating itinerary: {e}")

            return Itinerary(
                daily_activities=[
                    ["Morning activity", "Afternoon activity"],
                    ["Morning activity", "Afternoon activity"],
                    ["Morning activity", "Afternoon activity"]
                ]
            )

    def get_human_confirmation(self, prompt: str) -> bool:
        """Get human confirmation for a suggestion."""

        while True:
            choice = input(f"{prompt} (y/n): ").lower().strip()

            if choice in ["y", "n"]:
                return choice == "y"

            print("Please enter 'y' or 'n'.")

    def plan_trip(self) -> None:
        """Run the complete trip planning process."""

        print("\n=== Welcome to the Trip Planner! ===\n")

        # ==========================================
        # STEP 1: DESTINATION SELECTION
        # ==========================================

        suggested_destination = self.suggest_destination()

        print(f"\nSuggested destination: {suggested_destination}")

        # Human-in-the-loop: Destination confirmation
        if self.get_human_confirmation(
            "Would you like to use this destination?"
        ):
            destination = suggested_destination
        else:
            destination = input(
                "Enter your preferred destination: "
            ).strip()

        # ==========================================
        # STEP 2: FLIGHT SELECTION
        # ==========================================

        departure_city = input(
            "\nEnter your departure city: "
        ).strip()

        suggested_flight = self.suggest_flight(
            departure_city, destination
        )

        print("\nSuggested fictional flight:")
        print(f"Airline: {suggested_flight.airline}")
        print(f"Flight: {suggested_flight.flight_number}")
        print(f"Departure: {suggested_flight.departure_time}")
        print(f"Arrival: {suggested_flight.arrival_time}")

        # Human-in-the-loop: Flight confirmation
        if not self.get_human_confirmation(
            "Would you like to use this flight?"
        ):
            print("\nEnter your preferred flight details:")

            suggested_flight = FlightInfo(
                flight_number=input(
                    "Flight number: "
                ).strip(),
                departure_time=input(
                    "Departure time (HH:MM): "
                ).strip(),
                arrival_time=input(
                    "Arrival time (HH:MM): "
                ).strip(),
                airline=input(
                    "Airline: "
                ).strip()
            )

        # ==========================================
        # STEP 3: ITINERARY GENERATION
        # ==========================================

        suggested_itinerary = self.generate_itinerary(
            destination
        )

        print("\nSuggested itinerary:")

        for index, activities in enumerate(
            suggested_itinerary.daily_activities, 1
        ):
            print(f"\nDAY {index}:")

            for activity in activities:
                print(f"- {activity}")

        # Human-in-the-loop: Itinerary confirmation
        if not self.get_human_confirmation(
            "\nWould you like to use this itinerary?"
        ):
            print(
                "\nPlease enter your preferred activities for each day."
            )

            custom_itinerary = []

            for day in range(1, 4):
                activities = []

                print(
                    f"\nEnter activities for DAY {day} "
                    "(type 'done' when finished):"
                )

                while True:
                    activity = input("Activity: ").strip()

                    if activity.lower() == "done":
                        break

                    if activity:
                        activities.append(activity)

                custom_itinerary.append(activities)

            suggested_itinerary = Itinerary(
                daily_activities=custom_itinerary
            )

        # ==========================================
        # SAVE THE COMPLETE TRIP PLAN
        # ==========================================

        self.trip_plan = TripPlan(
            destination=destination,
            departure_city=departure_city,
            flight_info=suggested_flight,
            itinerary=suggested_itinerary
        )

        # ==========================================
        # DISPLAY THE FINAL TRIP PLAN
        # ==========================================

        print("\n=== Your Trip Plan ===")

        print(f"Destination: {self.trip_plan.destination}")
        print(f"Departure from: {self.trip_plan.departure_city}")

        print("\nFlight Information:")
        print(f"Airline: {self.trip_plan.flight_info.airline}")
        print(f"Flight: {self.trip_plan.flight_info.flight_number}")
        print(
            f"Departure: {self.trip_plan.flight_info.departure_time}"
        )
        print(
            f"Arrival: {self.trip_plan.flight_info.arrival_time}"
        )

        print("\nItinerary:")

        for index, activities in enumerate(
            self.trip_plan.itinerary.daily_activities, 1
        ):
            print(f"\nDAY {index}:")

            for activity in activities:
                print(f"- {activity}")

        print("\n=== Trip Planning Complete! ===")


def main():
    planner = TripPlanner()
    planner.plan_trip()


if __name__ == "__main__":
    main()
