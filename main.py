import os
from dotenv import load_dotenv
from agents.meal_creator import MealPlanCreatorAgent
from agents.shopping_builder import ShoppingListBuilderAgent
from config.settings import FAMILY_SIZE

# Load environment variables from .env file
load_dotenv() 

def run_application():
    """Defines and executes the agent workflow."""
    print("--- 🍽️ Meal Planning Agent System Starting ---")

    # 1. Initialize Agents
    # The API key is loaded into the environment by dotenv, which the agent uses.
    planner = MealPlanCreatorAgent(family_size=FAMILY_SIZE)
    list_builder = ShoppingListBuilderAgent()
    
    # 2. Agent 1: Create the Meal Plan
    weekly_meal_plan = planner.generate_plan()
    
    if weekly_meal_plan:
        # 3. Agent 2: Build the Shopping List
        shopping_list_items = list_builder.generate_shopping_list(weekly_meal_plan)
        
        # 4. Display and integrate
        print(list_builder.format_shopping_list(shopping_list_items))
        
        # Optional: Call the AnyList integration placeholders
        planner.export_plan_to_anylist(weekly_meal_plan)
        list_builder.export_list_to_anylist(shopping_list_items)
        
    print("--- Agent System Finished ---")

if __name__ == "__main__":
    run_application()