import logging
from typing import Dict, List, Tuple

class ShoppingListBuilderAgent:
    """
    Agent responsible for generating a consolidated shopping list from a meal plan.
    """
    def __init__(self):
        logging.info("Shopping List Agent initialized.")

    def generate_shopping_list(self, meal_plan: Dict) -> Dict[str, List[str]]:
        """
        Parses the meal plan and groups ingredients by the dish they belong to.
        
        Returns a dictionary: { "Dish Name": ["Ingredient 1", "Ingredient 2", ...] }
        """
        if not meal_plan:
            logging.info("Cannot generate shopping list: Meal plan is empty or failed to generate.")
            return {}
            
        # New structure to hold ingredients grouped by dish
        # The key is the dish name, value is a list of its ingredients
        grouped_list: Dict[str, List[str]] = {}
        
        # 1. Iterate through the structured meal plan
        for day in meal_plan.values():
            for meal_data in day.values():
                # meal_data is expected to be a dict: {'dish': str, 'ingredients': List[str]}
                dish_name = meal_data.get('dish')
                ingredients = meal_data.get('ingredients', [])
                
                if dish_name and ingredients:
                    # In this simple model, we map ingredients to the dish.
                    # We use a set for deduplication per dish to ensure the list is clean
                    
                    # Consolidate: If the dish name already exists (e.g., 'Ham and Cheese Sandwich' on multiple days), 
                    # combine the ingredient lists and deduplicate.
                    existing_ingredients = set(grouped_list.get(dish_name, []))
                    new_ingredients = existing_ingredients.union(set(ingredients))
                    
                    grouped_list[dish_name] = sorted(list(new_ingredients))

        # We also want a final, fully consolidated list for reference, but the main output is grouped.
        # However, for this task, the grouped list is the primary output.
        return grouped_list

    def format_shopping_list(self, grouped_list: Dict[str, List[str]]) -> str:
        """Formats the list into an easy-to-read string, showing ingredients per dish."""
        if not grouped_list:
            return "The shopping list is empty."

        formatted_list = "\n--- Consolidated Shopping List by Dish 📋 ---\n"
        
        # 1. Grouping by Dish
        for dish, ingredients in grouped_list.items():
            formatted_list += f"\n🍜 **{dish}**:\n"
            for item in ingredients:
                # Indent ingredients for readability
                formatted_list += f"  - {item}\n"

        # 2. Add an optional section for fully consolidated items (helpful for shopping flow)
        all_ingredients = []
        for ingredients in grouped_list.values():
            all_ingredients.extend(ingredients)
        
        unique_items = sorted(list(set(all_ingredients)))
        
        formatted_list += "\n--- Total Unique Items to Buy ---\n"
        for i, item in enumerate(unique_items, 1):
            formatted_list += f"{i}. {item}\n"
        
        return formatted_list

    def export_list_to_anylist(self, shopping_list: List[str]):
        """Placeholder method for AnyList shopping list integration."""
        if shopping_list:
            logging.info("\n[Integration Placeholder] Shopping list data ready for AnyList export (via external API call).")

# This is just a class file, so the main execution block is removed here.