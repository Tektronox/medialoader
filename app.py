#!/usr/bin/env python3
"""
Telegram YouTube Downloader
A bot that listens to YouTube links in Telegram chats and downloads them.
"""
import os
import re
import logging
import datetime
import sys
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import Filters
from pytube import YouTube

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
STORAGE_PATH = os.getenv('STORAGE_PATH')
CHAT_ID = os.getenv('CHAT_ID')

# YouTube URL regex pattern
YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'Hi! I am a YouTube downloader bot. Send me a YouTube link, and I will download it for you.'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Send me a message containing a YouTube link, and I will download the video for you.\n'
        'Commands:\n'
        '/start - Start the bot\n'
        '/help - Show this help message'
    )

def extract_youtube_id(text: str) -> list:
    """Extract YouTube video IDs from text."""
    matches = re.finditer(YOUTUBE_REGEX, text, re.MULTILINE)
    video_ids = []
    
    for match in matches:
        # Group 6 contains the video ID
        video_ids.append(match.group(6))
    
    return video_ids

def download_youtube_video(video_id: str) -> tuple:
    """
    Download a YouTube video using pytube.
    Returns a tuple: (success, message, file_path)
    """
    try:
        # Create YouTube object
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(youtube_url)
        
        # Get video title and sanitize it for filesystem
        title = yt.title
        safe_title = "".join([c if c.isalnum() or c in ' ._-' else '_' for c in title]).strip()
        
        # Create today's date folder
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        save_dir = Path(STORAGE_PATH) / today
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Get highest resolution stream with both video and audio
        stream = yt.streams.get_highest_resolution()
        
        # Download the video
        file_path = stream.download(output_path=str(save_dir), filename=f"{safe_title}.mp4")
        
        logger.info(f"Successfully downloaded: {title}")
        return True, f"Downloaded: {title}", file_path
        
    except Exception as e:
        logger.error(f"Error downloading video {video_id}: {str(e)}")
        return False, f"Failed to download video: {str(e)}", None

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle messages containing YouTube links."""
    message_text = update.message.text
    chat_id = str(update.effective_chat.id)
    
    # Check if message is from the monitored chat
    if CHAT_ID and chat_id != CHAT_ID:
        logger.debug(f"Message from non-monitored chat: {chat_id}")
        return
    
    # Extract YouTube video IDs from the message
    video_ids = extract_youtube_id(message_text)
    
    if not video_ids:
        # No YouTube links found, ignore the message
        return
    
    for video_id in video_ids:
        # Send a status message
        status_message = update.message.reply_text(f"Downloading video {video_id}...")
        
        # Download the video
        success, message, file_path = download_youtube_video(video_id)
        
        # Update status message
        status_message.edit_text(message)
        
        if success:
            # Send additional information about where the file is stored
            storage_info = f"Saved to: {file_path}"
            update.message.reply_text(storage_info)

def main() -> None:
    """Start the bot."""
    # Validate environment variables
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set.")
        sys.exit(1)
    
    if not STORAGE_PATH:
        logger.error("STORAGE_PATH environment variable is not set.")
        sys.exit(1)
    
    if not CHAT_ID:
        logger.warning("CHAT_ID environment variable is not set. The bot will respond to all chats.")
    else:
        logger.info(f"Bot will only respond to chat ID: {CHAT_ID}")
    
    # Create storage directory if it doesn't exist
    Path(STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    
    # Create the Updater and pass it your bot's token
    updater = Updater(TELEGRAM_BOT_TOKEN)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    
    # Register message handler for YouTube links
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Start the Bot
    logger.info("Starting bot...")
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()