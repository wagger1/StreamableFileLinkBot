import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
FILE_CHANNEL = os.environ.get("FILE_CHANNEL")  # -100xxxx or @username
# ----------------

app = Client("file_to_link_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def generate_link(channel, message_id):
    """Generate t.me link for channel message"""
    if str(channel).startswith("-100"):  # private channel
        return f"https://t.me/c/{str(channel)[4:]}/{message_id}"
    else:  # public channel username
        return f"https://t.me/{channel}/{message_id}"

async def upload_document(message):
    """Upload document to FILE_CHANNEL"""
    try:
        return await app.send_document(chat_id=FILE_CHANNEL, document=message.document.file_id)
    except Exception as e:
        return e

def build_buttons(message):
    """Create inline button for download"""
    link = generate_link(FILE_CHANNEL, message.message_id)
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("📥 Download", url=link)]]
    )

# --- Handle PM forwards ---
@app.on_message(filters.private & filters.document)
async def handle_pm(client, message):
    uploaded = await upload_document(message)
    if isinstance(uploaded, Exception):
        await message.reply_text(f"❌ Failed to process file.\nError: {uploaded}")
        return

    caption = "✅ Your download link:"
    await message.reply_text(caption, reply_markup=build_buttons(uploaded))

# --- Handle documents sent in channel ---
@app.on_message(filters.chat(FILE_CHANNEL) & filters.document)
async def handle_channel_post(client, message):
    caption = "📥 Fast download link:"
    await message.reply_text(caption, reply_markup=build_buttons(message))

# --- Start command ---
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Send me any document file (PDF, ZIP, etc.)\n"
        "I will give you a fast download link!"
    )

from flask import Flask
import threading

app_web = Flask("health")

@app_web.route("/")
def home():
    return "Bot is running ✅"

def run_web():
    app_web.run(host="0.0.0.0", port=8000)

# Run Flask in a separate thread
import threading
threading.Thread(target=run_web).start()

if __name__ == "__main__":
    print("Document File-to-Link Bot is running...")
    app.run()
