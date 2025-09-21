import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load config from environment variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
FILE_CHANNEL = int(os.environ.get("FILE_CHANNEL"))  # Channel ID (-100xxxxxxxxx)

app = Client(
    "streamable_file_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def handle_file(client, message):
    """
    Upload files to FILE_CHANNEL and generate streamable links for videos/audio.
    """
    try:
        if message.video:
            media = await client.send_video(
                chat_id=FILE_CHANNEL,
                video=message.video.file_id,
                caption=message.caption or ""
            )
        elif message.audio:
            media = await client.send_audio(
                chat_id=FILE_CHANNEL,
                audio=message.audio.file_id,
                caption=message.caption or ""
            )
        else:
            # Documents and other files
            media = await client.send_document(
                chat_id=FILE_CHANNEL,
                document=message.document.file_id,
                caption=message.caption or ""
            )

        # Generate Telegram link
        file_link = f"https://t.me/c/{str(FILE_CHANNEL)[4:]}/{media.message_id}"

        await message.reply_text(
            f"✅ Your file link:\n\n{file_link}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📥 Open File", url=file_link)]]
            )
        )
    except Exception as e:
        await message.reply_text(f"❌ Failed to process file.\nError: {e}")

@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Hi! Send me any video, audio, or document.\n"
        "Videos and audio will be streamable.\n"
        "Documents will be downloadable."
    )

@app.on_message(filters.private & filters.command("help"))
async def help_command(client, message):
    await message.reply_text(
        "📌 **How to use:**\n"
        "1. Send any video, audio, or document.\n"
        "2. I upload it to my channel.\n"
        "3. You get a Telegram link.\n\n"
        "✅ Videos/audio = Streamable\n"
        "✅ Documents = Downloadable"
    )

if __name__ == "__main__":
    print("Streamable File-to-Link Bot is running...")
    app.run()
