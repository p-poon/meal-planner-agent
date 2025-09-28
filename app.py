# app.py

import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# --- Imports for Agents ---
from agents.meal_creator import MealPlanCreatorAgent
from agents.shopping_builder import ShoppingListBuilderAgent
from agents.email_sender import EmailSenderAgent
from config.settings import FAMILY_SIZE

# --- Initialization ---
load_dotenv()

app = Flask(__name__)

# Set up a logger for file output (similar to what was in main.py)
log_file_path = "web_agent_log.txt"
logging.basicConfig(
    filename=log_file_path, 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)
# Also log to console
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)

def initialize_agents(suppress_output=True):
    """Initializes and returns agent instances after environment is loaded."""

    # --- DEBUGGING CHECK ---
    if not os.getenv("GEMINI_API_KEY"):
        logging.error("FATAL: GEMINI_API_KEY is not loaded into the environment!")
    else:
        logging.info("DEBUG: GEMINI_API_KEY is present.")
    # -----------------------

    # Initialize agents without output suppression in this example
    planner = MealPlanCreatorAgent(family_size=FAMILY_SIZE, suppress_output=suppress_output)
    list_builder = ShoppingListBuilderAgent()
    email_sender = EmailSenderAgent()
    return planner, list_builder, email_sender

@app.route('/')
def index():
    """Serves the main HTML page."""
    # Assuming index.html is in a folder named 'templates'
    # You will need to move index.html into a new 'templates' folder.
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_meal_plan():
    """Handles the API request to generate the plan."""
    # 1. Initialize agents for THIS request (or use a caching pattern for production)
    # Using 'False' here to get console/file output during testing, but the web UI suppresses it.
    planner, list_builder, email_sender = initialize_agents(suppress_output=False) 

    data = request.get_json()
    user_preferences = data.get('preferences', '')
    
    logging.info(f"\n--- API Request Received ---")
    logging.info(f"User Preferences: '{user_preferences}'")

    try:
        # 2. Generate the Meal Plan (Uses the non-interactive method)
        # Assuming you've moved the core generation logic to this method in the agent file:
        weekly_meal_plan = planner.generate_plan_from_string(user_preferences) 
        
        if not weekly_meal_plan:
            logging.error("Failed to generate structured meal plan from Gemini.")
            return jsonify({"error": "Failed to generate meal plan from Gemini."}), 500

        # 3. Build the Shopping List
        grouped_shopping_list = list_builder.generate_shopping_list(weekly_meal_plan)
        
        # 4. Get Formatted Output
        formatted_list_output = list_builder.format_shopping_list(grouped_shopping_list)
        
        # 5. Execute Email Sending (Runs in the background, logging status)
        email_sender.send_plan(weekly_meal_plan, grouped_shopping_list)
        
        logging.info("Successfully generated and emailed plan. Returning log output to frontend.")
        
        # 6. Return the formatted text to the frontend
        return jsonify({
            "status": "success",
            "log": formatted_list_output
        })

    except Exception as e:
        logging.error(f"Critical error during agent execution: {e}", exc_info=True)
        return jsonify({"error": f"Internal server error: {type(e).__name__}: {str(e)}"}), 500

if __name__ == '__main__':
    # REMINDER: For a clean run, ensure agents are initialized cleanly before this line.
    app.run(debug=True)

# You will need to modify your agent classes to remove the input() prompt and accept 
# the preferences string directly.