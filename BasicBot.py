import logging
import requests
import datetime
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your Telegram bot's API token
TOKEN = "7623220505:AAHTtOaL4JQKgcwMli0C5ZtMsdBKecBwLbk" # Store your token in an environment variable
BOT_USERNAME = "@AlexafnBot"

# OpenRouter API settings
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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" # Store API key in environment variable

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# Predefined responses for common questions
predefined_responses = {
    "who created you": "I am created by AFIN.",
    "who is your creator": "I am created by AFIN.",
    "who made you": "I am created by AFIN.",
    "who are you": "I am Alexa, your AI assistant, created by AFIN.",
    "what's your name": "My name is Alexa!",
    "what is your name": "My name is Alexa!",
    "hello": "Hello! How can I assist you today?",
    "hi": "Hey there! How can I help you?",
    "which language": "I can communicate in multiple languages! Let me know which one you'd like to use.",
}

# Function to get real-time date
def get_date():
    today = datetime.datetime.now().strftime("%B %d, %Y")  # Example: March 10, 2025
    return f"Today's date is {today}."

# Function to get response from OpenRouter AI
async def get_ai_response(user_input):
    lower_input = user_input.lower().strip()

    # Check if the input is a predefined question
    if lower_input in predefined_responses:
        return predefined_responses[lower_input]

    # Check for date-related query
    if "date" in lower_input:
        return get_date()

    # Check for weather query
    if "weather" in lower_input:
        return "I'm sorry, I currently can't fetch live weather data. Try checking sites like weather.com!"

    try:
        data = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "messages": [
                {"role": "system", "content": "Your name is Alexa. You are a friendly and helpful AI chatbot."},
                {"role": "user", "content": user_input}
            ]
        }
        
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                ai_message = result["choices"][0].get("message", {}).get("content", "").strip()
                return ai_message if ai_message else "I'm not sure about that, but I can try to find out!"
        else:
            return "Sorry, I'm having trouble processing your request."

    except Exception as e:
        logger.error(f"AI API error: {e}")
        return "Sorry, I encountered an issue. Try again later."

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! I'm Alexa, your AI assistant, created by AFIN. Ask me anything!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I’m Alexa, a smart AI chatbot. You can ask me anything, and I'll do my best to help!")

# Message handlers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = await get_ai_response(user_message)
    await update.message.reply_text(response)

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    app.add_error_handler(error)

    # Start polling
    print("Polling...")
    app.run_polling(timeout=3)  # FIXED: Changed poll_interval to timeout
