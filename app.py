from flask import Flask, request
from pyrogram import Client, filters
import os
from vars import API_ID, API_HASH, BOT_TOKEN

app = Flask(__name__)

# Initialize bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True  # Important for Vercel
)

@app.route('/webhook', methods=['POST'])
async def webhook():
    data = request.json
    # Process Telegram updates here
    await bot.handle_updates(data)
    return {"ok": True}

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
