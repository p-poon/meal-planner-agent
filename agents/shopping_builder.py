from typing import Dict, List, Tuple

class ShoppingListBuilderAgent:
    """
    Agent responsible for generating a consolidated shopping list from a meal plan.
    """
    def __init__(self):
        print("Shopping List Agent initialized.")

    def generate_shopping_list(self, meal_plan: Dict) -> List[str]:
        """
        Parses the meal plan, consolidates ingredients, and creates a shopping list.
        """
        if not meal_plan:
            print("Cannot generate shopping list: Meal plan is empty or failed to generate.")
            return []
            
        all_ingredients = []
        
        # 1. Extract all ingredients from the Gemini-generated JSON structure
        for day in meal_plan.values():
            for meal_data in day.values():
                # 'meal_data' is the dictionary for 'Breakfast' or 'Dinner'
                ingredients = meal_data.get('ingredients', [])
                all_ingredients.extend(ingredients)

        # 2. Consolidate and deduplicate the list
        shopping_list = sorted(list(set(all_ingredients)))
        
        return shopping_list

    def format_shopping_list(self, shopping_list: List[str]) -> str:
        """Formats the list into an easy-to-read string."""
        if not shopping_list:
            return "The shopping list is empty."

        formatted_list = "\n--- Consolidated Shopping List ---\n"
        for i, item in enumerate(shopping_list, 1):
            formatted_list += f"{i}. {item}\n"
        
        return formatted_list

    def export_list_to_anylist(self, shopping_list: List[str]):
        """Placeholder method for AnyList shopping list integration."""
        if shopping_list:
            print("\n[Integration Placeholder] Shopping list data ready for AnyList export (via external API call).")

# This is just a class file, so the main execution block is removed here.