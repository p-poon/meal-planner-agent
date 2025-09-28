import os
import json
import logging
from typing import Dict, List, Tuple

# Using the RECOMMENDED stable package structure
from google import genai
from google.genai import types

class MealPlanCreatorAgent:
    """
    Agent responsible for generating a week-long meal plan using the Gemini API.
    """
    def __init__(self, family_size: int = 5, model_name: str = 'gemini-2.5-flash'):
        self.family_size = family_size
        self.model_name = model_name
        self.client = None
        
        # NOTE: The new SDK automatically picks up the GEMINI_API_KEY environment variable.
        try:
            # 1. Check for API key presence (good practice)
            if not os.getenv("GEMINI_API_KEY"):
                 raise ValueError("GEMINI_API_KEY environment variable is not set.")
            
            # 2. Initialize the Client
            self.client = genai.Client()
            logging.info(f"Meal Plan Agent initialized for a family of {self.family_size} using {self.model_name}.") # <-- Changed from print()
        
        except Exception as e:
            logging.error("ERROR: Failed to initialize Gemini Client.") # <-- Changed from print()
            logging.info(f"Please ensure the 'google-genai' package is installed and GEMINI_API_KEY is set. Details: {e}")

    def _get_user_prompt(self) -> str:
        """Prompts the user for details to build a detailed prompt for Gemini."""
        logging.info("\n--- Meal Preferences ---")
        logging.info(f"I'll plan for 7 days (Breakfast/Dinner) for {self.family_size} people.")
        
        user_input = input("Enter preferred dishes, allergies, or dietary goals (e.g., 'Tacos, Chicken, no nuts, high protein'):\n> ")
        return user_input

    def generate_plan(self) -> Dict:
        """
        Calls the Gemini API to create a structured JSON meal plan using schema enforcement.
        Returns a dictionary structure: {Day: {MealType: {dish: str, ingredients: List[str]}}}
        """
        if not self.client:
            return {}

        user_prefs = self._get_user_prompt()
        
        # 1. Define the desired structured output using types.Schema (The correct way for this SDK)
        meal_object_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "dish": types.Schema(type=types.Type.STRING, description="The name of the dish."),
                "ingredients": types.Schema(
                    type=types.Type.ARRAY, 
                    items=types.Schema(type=types.Type.STRING), 
                    description=f"List of ingredients with quantities suitable for {self.family_size} people."
                )
            },
            required=["dish", "ingredients"]
        )
        
        # 2. Define the overall meal plan schema for 7 days
        meal_plan_properties = {
            day: types.Schema(
                type=types.Type.OBJECT,
                properties={"Breakfast": meal_object_schema, "Dinner": meal_object_schema},
                required=["Breakfast", "Dinner"]
            ) 
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        }

        meal_plan_schema = types.Schema(
            type=types.Type.OBJECT,
            properties=meal_plan_properties,
            required=list(meal_plan_properties.keys())
        )

        # 3. Craft the detailed prompt
        system_instruction = (
            "You are an expert, helpful meal planning assistant for a Singaporean Chinese family. "
            "Your task is to generate a complete 7-day meal plan for a family of 5, including Breakfast and Dinner. "
            "**The dinner MUST include a Chinese soup (e.g., ABC soup, Lotus Root Soup, Old Cucumber Soup).** "
            "Prioritize Singaporean Chinese home-cooked dishes (e.g., Stir-fried vegetables, Steamed Fish, Tau Yew Bak, etc.). "
            "**CRITICAL BREAKFAST INSTRUCTIONS:** "
            "1. **Monday Breakfast** must be 'Ham and Cheese Sandwich'. "
            "2. **Wednesday Breakfast** must be 'Steamed Pau'. "
            "3. All other breakfasts should be simple, non-soup, fast-cooking options (e.g., soft boiled eggs, toast, congee)."
            "ONLY respond with a valid, clean JSON object that strictly adheres to the provided schema. "
            "Do not include any explanations, greetings, or formatting outside the JSON."
        )

        prompt = (
            f"Generate a 7-day family meal plan. The user has the following preferences/restrictions: '{user_prefs}'. "
            "Ensure the plan strictly follows the mandatory Monday (Ham/Cheese Sandwich) and Wednesday (Steamed Pau) breakfasts, "
            "and all dinners include a traditional Singaporean Chinese soup."
        )
        
        # 4. Configure the generation request for JSON output
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=meal_plan_schema,
            temperature=0.7 
        )

        logging.info("\n-- Calling Gemini API to generate meal plan... (This may take a moment) --")
        
        try:
            # 5. Call the API using the Client object
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            # --- NEW LOGGING STEP 1: Show Raw Gemini Response ---
            logging.info("\n🤖 [Gemini Response Received - Raw JSON]:")
            logging.info("="*60)
            logging.info(response.text)
            logging.info("="*60)
            
            # 6. Parse the JSON response
            meal_plan_json = json.loads(response.text)

            # --- NEW LOGGING STEP 2: Show Parsed Python Dictionary ---
            logging.info("\n✨ [Meal Plan Structured Output - Python Dict]:")
            logging.info(json.dumps(meal_plan_json, indent=2))
            logging.info("="*60)

            logging.info("\n--- Suggested Weekly Meal Plan (Generated by Gemini) ---")
            for day, meals in meal_plan_json.items():
                breakfast = meals.get("Breakfast", {}).get("dish", "N/A")
                dinner = meals.get("Dinner", {}).get("dish", "N/A")
                logging.info(f"**{day}**: Breakfast: {breakfast} | Dinner: {dinner}")

            return meal_plan_json

        except Exception as e:
            logging.info(f"\n❌ ERROR: Failed to get structured response from Gemini API: {e}")
            return {}

    def export_plan_to_anylist(self, meal_plan: Dict):
        """Placeholder method for AnyList meal plan integration."""
        if meal_plan:
            logging.info("\n[Integration Placeholder] Meal plan data ready for AnyList export (via external API call).")