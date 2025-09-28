import os
import smtplib
from email.message import EmailMessage
from typing import Dict, List

class EmailSenderAgent:
    """
    Agent responsible for formatting the meal plan and shopping list and 
    sending it via an outbound SMTP server.
    """
    def __init__(self):
        # Retrieve credentials from environment variables using os.getenv()
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = os.getenv("SMTP_PORT")
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")

        # Check if configuration is complete
        if not all([self.smtp_server, self.smtp_port, self.email_address, self.email_password, self.recipient_email]):
            print("WARNING: SMTP credentials or email addresses are missing from .env. Email integration is disabled.")
            self.is_configured = False
        else:
            self.is_configured = True
            print("Email Sender Agent initialized.")
    
    def build_message_body(self, meal_plan: Dict, grouped_shopping_list: Dict[str, List[str]]) -> str:
        """
        Formats the meal plan and grouped shopping list into a single, clean plain text message body.
        """
        
        # 1. Format Meal Plan
        meal_plan_text = "🍽️ WEEKLY MEAL PLAN (Singaporean Chinese Family of 5) 🍽️\n\n"

        for day, meals in meal_plan.items():
            meal_plan_text += f"================================\n"
            meal_plan_text += f"📅 {day}:\n"
            
            # Helper to format each meal type
            def format_meal_details(meal_type: str, details: Dict) -> str:
                dish = details.get("dish", "N/A")
                instructions = details.get("instructions", "No instructions available.")
                link = details.get("youtube_link", "No link provided.")
                
                output = f"   - {meal_type} Dish: {dish}\n"
                output += f"     * Instructions: {instructions}\n"
                output += f"     * Video Link: {link}\n"
                return output

            # Add Breakfast details
            breakfast_details = meals.get("Breakfast", {})
            meal_plan_text += format_meal_details("Breakfast", breakfast_details)

            # Add Dinner details
            dinner_details = meals.get("Dinner", {})
            meal_plan_text += format_meal_details("Dinner", dinner_details)

        meal_plan_text += "================================\n"
        
        # 2. Format Grouped Shopping List (NEW STRUCTURE)
        shopping_list_text = "\n\n🛒 SHOPPING LIST BY DISH 🛒\n"
        
        for dish, ingredients in grouped_shopping_list.items():
            shopping_list_text += f"\n🍜 {dish} Ingredients:\n"
            for item in ingredients:
                shopping_list_text += f"  - {item}\n" 

        # 3. Add Final Consolidated List (for quick shopping)
        all_ingredients = []
        for ingredients in grouped_shopping_list.values():
            all_ingredients.extend(ingredients)
        unique_items = sorted(list(set(all_ingredients)))

        shopping_list_text += "\n--- CONSOLIDATED TOTALS (For Shopping Cart) ---\n"
        for i, item in enumerate(unique_items, 1):
            shopping_list_text += f"{i}. {item}\n"
        
        return meal_plan_text + shopping_list_text

    def send_plan(self, meal_plan: Dict, shopping_list: Dict[str, List[str]]):
        """Builds the email and sends it via SMTP."""
        if not self.is_configured:
            return

        message_body = self.build_message_body(meal_plan, shopping_list)
        
        msg = EmailMessage()
        # Ensure FAMILY_SIZE is retrieved correctly from os.environ
        family_size = os.getenv('FAMILY_SIZE', '5')
        msg['Subject'] = f"Weekly Meal Plan & Shopping List ({family_size} People)"
        msg['From'] = self.email_address
        msg['To'] = self.recipient_email
        msg.set_content(message_body)

        try:
            # Connect to the SMTP server and send
            # Ensure SMTP_PORT is cast to int as os.getenv returns strings
            with smtplib.SMTP(self.smtp_server, int(self.smtp_port)) as server:
                server.starttls() # Secure the connection
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"\n✅ Email sent successfully to {self.recipient_email}!")

        except smtplib.SMTPAuthenticationError:
            print("\n❌ SMTP Authentication Error: Check your EMAIL_PASSWORD. If using Gmail, ensure you are using an 'App Password'.")
        except smtplib.SMTPException as e:
            print(f"\n❌ SMTP Error occurred: {e}")
        except Exception as e:
            print(f"\n❌ An unexpected error occurred during email sending: {e}")