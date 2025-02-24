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

    # Get the username of the sender (if available)
    username = update.message.from_user.username
    if not username:
        username = "Unknown"  # Fallback if user hasn’t set a username

    print(f"Username: {username}")

    # Notify the user that processing has started
    await update.message.reply_text("Processing your video...")

    # Generate a unique filename with UUID
    video_file = f"video_{uuid.uuid4()}.mp4"

    # yt-dlp options for MP4 output
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Prioritize MP4
        'outtmpl': video_file,  # Use UUID-based filename
        'merge_output_format': 'mp4',  # Ensure output is MP4
    }

    try:
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Downloaded file: {video_file}")  # Debug: confirm file name

        # Check if file exists before sending
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"File {video_file} not found after download!")

        # Send the video file to the user
        with open(video_file, 'rb') as video:
            print(f"Sending file: {video_file}")  # Debug: confirm sending
            await context.bot.send_video(chat_id=chat_id, video=video, supports_streaming=True)

        # Clean up the downloaded file
        print(f"Removing file: {video_file}")  # Debug: confirm deletion
        os.remove(video_file)

        await update.message.reply_text("Video sent! Send another URL if you’d like.")

    except Exception as e:
        await update.message.reply_text(f"Sorry, something went wrong: {str(e)}")

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