import os
from dotenv import load_dotenv
import sys
import logging

from agents.meal_creator import MealPlanCreatorAgent
from agents.shopping_builder import ShoppingListBuilderAgent
from agents.whatsapp_sender import WhatsAppSenderAgent # <--- NEW IMPORT
from agents.email_sender import EmailSenderAgent
from config.settings import FAMILY_SIZE

# Load environment variables from .env file
load_dotenv() 

def setup_logging(log_file_path):
    """Sets up Python's logging system to write to both console and a file."""
    # Create the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) 
    
    # Define a formatter for clean output
    formatter = logging.Formatter('%(message)s')

    # Handler 1: Console Output (stdout)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Handler 2: File Output
    fh = logging.FileHandler(log_file_path, mode='w')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    # We will use logging.info() instead of print() in the agents now.
    return logger

def run_application():
    """Defines and executes the agent workflow, now fully logging its output."""
    
    log_file_path = "meal_plan_log.txt"
    logger = setup_logging(log_file_path) # Setup logger
    
    logging.info("--- 🍽️ Meal Planning Agent System Starting ---")
    logging.info(f"Log output redirected to {log_file_path}\n")
    logging.info("-" * 50)

    # 1. Initialize Agents
    planner = MealPlanCreatorAgent(family_size=FAMILY_SIZE)
    list_builder = ShoppingListBuilderAgent()
    email_sender = EmailSenderAgent()
    
    # 2. Agent 1: Create the Meal Plan
    weekly_meal_plan = planner.generate_plan() # This runs, and prints to console

    if weekly_meal_plan:
        
        logging.info("\n>>> HANDOVER: Meal Plan Creator (Agent 1) finished. Data passed to Shopping List Builder (Agent 2).")
        logging.info("-" * 50)
        
        # 3. Agent 2: Build the Shopping List
        shopping_list_items = list_builder.generate_shopping_list(weekly_meal_plan)
        
        # 4. Get the formatted shopping list string and print it (logs it)
        formatted_list = list_builder.format_shopping_list(shopping_list_items)
        logging.info(formatted_list)
        
        logging.info("\n>>> HANDOVER: Shopping List Builder (Agent 2) finished. Data passed to Email Sender (Agent 3).")
        logging.info("-" * 50)
        
        # 5. Agent 3: Send via Email (This prints status messages which will be logged)
        email_sender.send_plan(weekly_meal_plan, shopping_list_items)
        
        # 6. Show integration points
        planner.export_plan_to_anylist(weekly_meal_plan)
        list_builder.export_list_to_anylist(shopping_list_items)
        
        # 7. Write the full email body to the log for easy reference
        try:
            full_email_body = email_sender.build_message_body(weekly_meal_plan, shopping_list_items)
            logging.info("\n\n--- FULL EMAIL BODY (For Log Reference) ---")
            logging.info(full_email_body)
            logging.info("--- LOG END ---")

        except Exception as file_error:
            logging.error(f"\nFATAL LOGGING ERROR: Could not write full email body to log. Details: {file_error}")
    
    logging.info("\n--- Agent System Finished ---")

if __name__ == "__main__":
    run_application()