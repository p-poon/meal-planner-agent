import os
from twilio.rest import Client
from typing import List, Dict

class WhatsAppSenderAgent:
    """
    Agent responsible for integrating with the Twilio API to send WhatsApp messages.
    """
    def __init__(self):
        # Retrieve credentials from environment variables
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from_number = os.getenv("WHATSAPP_SENDER_NUMBER") # Your Twilio number or Sandbox number (e.g., whatsapp:+14155238886)
        self.whatsapp_to_number = os.getenv("WHATSAPP_GROUP_ID") # The recipient's number (e.g., whatsapp:+6591234567)

        if not all([self.account_sid, self.auth_token, self.whatsapp_from_number, self.whatsapp_to_number]):
            print("WARNING: Twilio credentials or phone numbers are missing from .env. WhatsApp integration is disabled.")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                print("WhatsApp Sender Agent initialized (via Twilio).")
            except Exception as e:
                print(f"ERROR: Failed to initialize Twilio client: {e}")
                self.client = None

    def build_message_body(self, meal_plan: Dict, grouped_shopping_list: Dict[str, List[str]]) -> str:
        """Formats the meal plan and grouped shopping list into a single, readable message."""
        
        # 1. Format Meal Plan (This remains the same)
        meal_plan_text = "🍽️ WEEKLY MEAL PLAN (Family of 5) 🍽️\n"
        for day, meals in meal_plan.items():
            breakfast = meals.get("Breakfast", {}).get("dish", "N/A")
            dinner = meals.get("Dinner", {}).get("dish", "N/A")
            meal_plan_text += f"*{day}*: B: {breakfast} | D: {dinner}\n" # Using * for bold/italics
        
        # 2. Format Grouped Shopping List (NEW LOGIC)
        shopping_list_text = "\n🛒 SHOPPING LIST BY DISH 🛒\n"
        
        for dish, ingredients in grouped_shopping_list.items():
            # Bold the dish name
            shopping_list_text += f"\n*{dish}*:\n" 
            for item in ingredients:
                # Use standard WhatsApp markdown for bullet points
                shopping_list_text += f"  - {item}\n" 

        # 3. Add Final Consolidated List (Optional but helpful)
        all_ingredients = []
        for ingredients in grouped_shopping_list.values():
            all_ingredients.extend(ingredients)
        unique_items = sorted(list(set(all_ingredients)))

        shopping_list_text += "\n--- CONSOLIDATED TOTALS ---\n"
        for i, item in enumerate(unique_items, 1):
            shopping_list_text += f"• {item}\n"
        
        return meal_plan_text + "\n" + shopping_list_text

    def send_plan(self, meal_plan: Dict, shopping_list: Dict[str, List[str]]): # <--- Note: Type hint update for shopping_list
        """Builds the message and sends it via the Twilio API."""
        if not self.client:
            return

        message_body = self.build_message_body(meal_plan, shopping_list)
        
        try:
            message = self.client.messages.create(
                from_=self.whatsapp_from_number,
                to=self.whatsapp_to_number,
                body=message_body
            )
            print(f"\n✅ WhatsApp message sent successfully! SID: {message.sid}")
            print(f"   Check status: https://www.twilio.com/console/sms/{message.sid}")

        except Exception as e:
            print(f"\n❌ ERROR sending WhatsApp message: {e}")
            print("   (Ensure the recipient has joined your Twilio Sandbox by sending 'join <code>'.)")