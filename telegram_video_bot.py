import os
import uuid
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Replace with your Telegram Bot Token from BotFather
TOKEN = "8078385395:AAFM-CnO3zRuhHFgT1uwcfJGsyUfCAt1xaM"

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a video URL, and I’ll download it as an MP4 for you.")

# Function to download video and send it back
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    username = update.message.from_user.username or "Unknown"

    # Notify the user that processing has started
    await update.message.reply_text(f"Processing your video, @{username}...")

    # Generate a unique filename with UUID
    video_file = f"video_{uuid.uuid4()}.mp4"

    # yt-dlp options to handle Instagram and ensure playable MP4
    ydl_opts = {
        'format': 'best[ext=mp4]',  # Prefer a single, pre-merged MP4 file
        'outtmpl': video_file,  # Use UUID-based filename
        'noplaylist': True,  # Avoid downloading playlists
        'quiet': False,  # Show output for debugging
        'verbose': True,  # Extra debug info
        # Optional: Uncomment if Instagram blocks default requests
        # 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Downloaded file: {video_file} for @{username}")
            print(f"Video info: {info.get('formats', 'No formats found')}")
            print(f"File size: {os.path.getsize(video_file) if os.path.exists(video_file) else 'N/A'} bytes")

        # Check if file exists and is non-empty
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"File {video_file} not found after download!")
        if os.path.getsize(video_file) < 1024:  # Less than 1KB is likely corrupt
            raise ValueError(f"File {video_file} is too small and likely corrupted!")

        # Send the video file to the user
        with open(video_file, 'rb') as video:
            print(f"Sending file: {video_file} to @{username}")
            await context.bot.send_video(chat_id=chat_id, video=video, supports_streaming=True)

        # Clean up the downloaded file
        print(f"Removing file: {video_file} for @{username}")
        os.remove(video_file)

        await update.message.reply_text(f"Video sent, @{username}! Send another URL if you’d like.")

    except Exception as e:
        await update.message.reply_text(f"Sorry, something went wrong, @{username}: {str(e)}")
        print(f"Error details: {str(e)}")

# Main function to set up the bot
def main():
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()