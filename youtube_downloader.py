#!/usr/bin/env python3
"""
YouTube Downloader Module
Contains functions for handling YouTube video extraction and downloading.
"""
import re
import logging
import datetime
from pathlib import Path
from pytubefix import YouTube

# Configure logging
logger = logging.getLogger(__name__)

# YouTube URL regex pattern
YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'

def extract_youtube_id(text: str) -> list:
    """Extract YouTube video IDs from text."""
    matches = re.finditer(YOUTUBE_REGEX, text, re.MULTILINE)
    video_ids = []
    
    for match in matches:
        # Group 6 contains the video ID
        video_ids.append(match.group(6))
    
    return video_ids

def download_youtube_video(video_id: str, storage_path: str) -> tuple:
    """
    Download a YouTube video using pytube.
    
    Args:
        video_id (str): The YouTube video ID
        storage_path (str): Base path for storing downloaded videos
        
    Returns:
        tuple: (success, message, file_path)
    """
    try:
        # Create YouTube object
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        logging.debug(f"Downloading video from URL: {youtube_url}")
        yt = YouTube(youtube_url)
        
        # Get video title and sanitize it for filesystem
        title = yt.title
        safe_title = "".join([c if c.isalnum() or c in ' ._-' else '_' for c in title]).strip()
        
        # Create today's date folder
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        save_dir = Path(storage_path) / today
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