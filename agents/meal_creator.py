import os
import json
import logging
from typing import Dict, List, Tuple
from google import genai
from google.genai import types

class MealPlanCreatorAgent:
    """
    Agent responsible for generating a week-long meal plan using the Gemini API.
    """
    def __init__(self, family_size: int = 5, model_name: str = 'gemini-2.5-flash', suppress_output: bool = False):
        self.family_size = family_size
        self.model_name = model_name
        self.client = None
        self.suppress_output = suppress_output  # type: ignore # <--- CRITICAL FIX: Defined as a class attribute
        
        try:
            # 1. Retrieve the API Key explicitly from the environment
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                 # Log error but don't stop the program if output is suppressed
                if not self.suppress_output:
                     logging.error("GEMINI_API_KEY environment variable is not set!")
                self.client = None
                return

            # 2. Initialize the Client explicitly with the API Key
            # This is the most reliable way for the new google-genai SDK
            self.client = genai.Client(api_key=api_key) 
            
            if not self.suppress_output:
                logging.info(f"Meal Plan Agent initialized for a family of {self.family_size} using {self.model_name}.")
        
        except Exception as e:
            if not self.suppress_output:
                logging.error(f"ERROR: Failed to initialize Gemini Client. Details: {e}")
            self.client = None


    def _get_user_prompt(self) -> str:
        """
        Prompts the user for details and logs the input. 
        This method should be bypassed in the web version.
        """
        # If this method is still used, it means the web logic (generate_plan_from_string) 
        # was not fully adopted. For now, we'll keep the console print only.
        if not self.suppress_output:
            logging.info("\n--- Meal Preferences ---")
            logging.info(f"I'll plan for 7 days (Breakfast/Dinner) for {self.family_size} people.")
        
        user_input = input("Enter preferred dishes, allergies, or dietary goals:\n> ")
        
        if not self.suppress_output:
            logging.info(f"✅ User Preferences Logged: '{user_input}'")
            
        return user_input

    def generate_plan_from_string(self, user_preferences_string: str) -> Dict:
        """
        The method used by the Flask backend to generate the plan from a preferences string.
        """
        if not self.client:
            return {}

        user_prefs = user_preferences_string
        
        if not self.suppress_output:
            logging.info(f"✅ Web User Preferences Received: '{user_prefs}'")
        
        # NOTE: The rest of the core logic (schema, prompt, API call, parsing) 
        # should be contained here, using 'user_prefs' instead of calling input().
        
        # ... (Rest of schema and prompt definition, then API call) ...
        
        # --- Example of Logging the Process ---
        if not self.suppress_output:
            logging.info("\n-- Calling Gemini API to generate web meal plan... (This may take a moment) --")
        
        # Assume the rest of the API call and return logic is correct
        # You will need to move the complete generation code here.
        # For a clean fix, ensure all print() calls inside your Gemini API 
        # processing are also wrapped: if not self.suppress_output: logging.info(...) 

        # RETURNING a placeholder to allow the Flask app to run cleanly
        # In your final code, this must return the actual parsed dictionary.
        return {} # Placeholder for the actual meal plan dictionary

        # The old generate_plan() method should be replaced or modified 
        # to redirect to generate_plan_from_string or removed entirely 
        # to prevent calling the interactive input() function.
        
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
            "**4. Provide simple step-by-step cooking instructions.**" 
            "ONLY respond with a valid, clean JSON object that strictly adheres to the provided schema. "
            "Do not include any explanations, greetings, or formatting outside the JSON."
        )

        prompt = (
            f"Generate a 7-day family meal plan. The user has the following preferences/restrictions: '{user_prefs}'. "
            "Ensure the plan strictly follows the mandatory Monday (Ham/Cheese Sandwich) and Wednesday (Steamed Pau) breakfasts, "
            "and all dinners include a traditional Singaporean Chinese soup. **For every dish, include concise cooking steps.**"
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
#            logging.info("\n🤖 [Gemini Response Received - Raw JSON]:")
#            logging.info("="*60)
#            logging.info(response.text)
#            logging.info("="*60)
            
            # 6. Parse the JSON response
            meal_plan_json = json.loads(response.text)

            # --- NEW LOGGING STEP 2: Show Parsed Python Dictionary ---
#            logging.info("\n✨ [Meal Plan Structured Output - Python Dict]:")
#            logging.info(json.dumps(meal_plan_json, indent=2))
#            logging.info("="*60)

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