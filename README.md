# 🍽️ Gemini-Powered Family Meal Planner Agent
This project is an agentic Python application designed to streamline weekly meal planning and grocery shopping for a family. It uses the Gemini API for intelligent meal creation based on user preferences and structured output (JSON mode) to automatically generate a precise shopping list.

# 🌟 Features
* Intelligent Meal Creation: The MealPlanCreatorAgent uses the Gemini API to generate a creative, 7-day meal plan (Breakfast and Dinner), adhering to specific dietary and cultural constraints (e.g., Singaporean Chinese cuisine with daily soups).

* Structured Output: Ensures reliable, machine-readable JSON output from the AI.

* Grouped Shopping List: The ShoppingListBuilderAgent consumes the meal plan and creates a single, consolidated list of ingredients, grouped by dish for efficient preparation and shopping.

* Secure Delivery: Sends the complete weekly plan and shopping list directly to the family email group via SMTP.

# 🛠️ Setup and Installation
Follow these steps to get the project running on your local machine.

## Prerequisites
1. Python 3.9+ installed.

1. A Gemini API Key (obtained from Google AI Studio).

1. SMTP Credentials (e.g., a Gmail App Password) for sending emails.

## Installation Steps
1. Clone the Repository:

```Bash
git clone https://github.com/yourusername/meal-planner-app.git
cd meal-planner-app```

1. Create and Activate Virtual Environment:

```Bash
python -m venv venv
source venv/bin/activate

1. Install Dependencies:```

```Bash
pip install -r requirements.txt```

1. Set Environment Variables (.env):

Create a file named .env in the project root and add your secret keys and configurations. *(This file is protected by .gitignore and should never be committed.)*

```Ini, TOML
# --- GEMINI API ---
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

# --- SMTP EMAIL CONFIGURATION ---
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
EMAIL_ADDRESS="your.meal.planner@gmail.com"
EMAIL_PASSWORD="YOUR_APP_PASSWORD" 
RECIPIENT_EMAIL="family.group@example.com"

# --- APPLICATION CONSTANTS ---
FAMILY_SIZE=5
```

## Running the Application
Execute the main orchestrator file:

```Bash
python main.py
```

The application will prompt you for any specific preferences, call the Gemini API, and display the meal plan before sending the results to the configured email address.

# 🔮 Future Upgrades and Integrations
This project is designed as a modular agent system, making it easy to swap out communication channels or add intelligence layers.

Current Status | Future Integration Goal |	Note
=================
Email Delivery	| WhatsApp Integration	| The current meal plan message is too long for simple WhatsApp message templates and exceeds character limits. Future work will integrate with the Twilio Conversations API or a similar service to handle large, structured group messages reliably.
Static Planning	| Cost & Budget Agent	| Add a new agent to estimate the weekly cost of the shopping list based on user-defined regional prices.
AnyList / Grocery App Integration	| Direct API Sync	| Implement direct data pushes to services like AnyList or Google Sheets using their respective APIs to eliminate the need for manual copy/paste from the email.

# 🙌 Acknowledgements
This project was built on the foundation of Google's powerful generative models.

A special acknowledgement goes to Google Gemini for providing the underlying AI intelligence that transforms a simple prompt into a structured, custom, and culturally sensitive weekly meal plan, making this complex agentic workflow possible.
