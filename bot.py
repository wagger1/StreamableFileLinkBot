import os
from datetime import datetime
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
FILE_CHANNEL = os.environ.get("FILE_CHANNEL")  # -100xxxx or @username
MONGO_URI = os.environ.get("MONGO_URI")  # MongoDB connection URI
DB_NAME = os.environ.get("DB_NAME", "file_to_link_bot")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "uploads")
# ----------------

# --- Initialize MongoDB ---
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
uploads_col = db[COLLECTION_NAME]

# --- Initialize Pyrogram ---
app = Client("file_to_link_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- Helper functions ---
def generate_link(channel, message_id):
    """Generate t.me link for channel message"""
    if not message_id:
        return None
    if str(channel).startswith("-100"):  # private channel
        return f"https://t.me/c/{str(channel)[4:]}/{message_id}"
    else:  # public channel username
        return f"https://t.me/{channel}/{message_id}"

async def upload_document(message):
    """Upload document to FILE_CHANNEL"""
    try:
        uploaded_msg = await app.send_document(chat_id=FILE_CHANNEL, document=message.document.file_id)
        # Log in MongoDB
        uploads_col.insert_one({
            "file_name": message.document.file_name,
            "file_size": message.document.file_size,
            "uploader_id": message.from_user.id if message.from_user else None,
            "uploaded_at": datetime.utcnow(),
            "channel_message_id": uploaded_msg.message_id
        })
        return uploaded_msg
    except Exception as e:
        return e

def build_buttons(message):
    """Create inline button for download"""
    message_id = getattr(message, "message_id", None)
    if not message_id:
        return None
    link = generate_link(FILE_CHANNEL, message_id)
    if not link:
        return None
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("📥 Download", url=link)]]
    )

# --- Handlers ---
@app.on_message(filters.private & filters.document)
async def handle_pm(client, message):
    uploaded = await upload_document(message)
    if isinstance(uploaded, Exception):
        await message.reply_text(f"❌ Failed to process file.\nError: {uploaded}")
        return

    buttons = build_buttons(uploaded)
    if not buttons:
        await message.reply_text("❌ Failed to create download link.")
        return

    caption = "✅ Your download link:"
    await message.reply_text(caption, reply_markup=buttons)

@app.on_message(filters.chat(FILE_CHANNEL) & filters.document)
async def handle_channel_post(client, message):
    buttons = build_buttons(message)
    if not buttons:
        return
    caption = "📥 Fast download link:"
    await message.reply_text(caption, reply_markup=buttons)

@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Send me any document file (PDF, ZIP, etc.)\n"
        "I will give you a fast download link!"
    )

@app.on_message(filters.private & filters.command("stats"))
async def stats(client, message):
    """Optional: Show upload stats from MongoDB"""
    count = uploads_col.count_documents({})
    await message.reply_text(f"📊 Total files uploaded: {count}")

# --- Run bot ---
if __name__ == "__main__":
    print("✅ Document File-to-Link Bot is running...")
    app.run()
