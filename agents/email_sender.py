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

    def _format_instructions_by_sentence(self, instructions: str) -> str:
        """
        Splits a block of text into one sentence per line for readability.
        Uses a regex to find sentence-ending punctuation followed by a space.
        """
        import re
        if not instructions:
            return "No instructions available."
            
        # Regex looks for '.', '!', or '?' followed by optional quotes/spaces, and replaces it with the punctuation and a newline.
        # This is a robust way to split sentences in a block of text.
        sentences = re.sub(r'([.?!])\s+(?=["A-Z0-9\n])', r'\1\n', instructions).strip()
        
        # Add a bullet point to each line for a list format
        bulleted_sentences = [f"        - {line.strip()}" for line in sentences.split('\n') if line.strip()]

        return '\n'.join(bulleted_sentences)
    
    def build_message_body(self, meal_plan: Dict, grouped_shopping_list: Dict[str, List[str]]) -> str:
        """
        Formats the meal plan and grouped shopping list into a single, clean plain text message body.
        """
        
        # 1. Format Meal Plan
        meal_plan_text = "🍽️ WEEKLY MEAL PLAN (Singaporean Chinese Family of 5) 🍽️\n\n"

        for day, meals in meal_plan.items():
            meal_plan_text += f"================================\n"
            meal_plan_text += f"📅 {day}:\n"
            
            # Re-implementing meal detail formatting directly
            for meal_type in ["Breakfast", "Dinner"]:
                details = meals.get(meal_type, {})
                dish = details.get("dish", "N/A")
                instructions_raw = details.get("instructions", "No instructions available.")
                
                # --- NEW STEP: Format instructions ---
                instructions_formatted = self._format_instructions_by_sentence(instructions_raw)
                
                meal_plan_text += f"   - {meal_type} Dish: {dish}\n"
                meal_plan_text += f"     * Instructions:\n{instructions_formatted}\n" # <-- Inject formatted instructions

        meal_plan_text += "================================\n"
        
        # 2. Format Grouped Shopping List (NEW STRUCTURE)
        shopping_list_text = "\n\n🛒 **FINAL SHOPPING LIST**  🛒\n"
        
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