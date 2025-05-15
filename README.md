# Telegram YouTube Downloader

This Python application runs a Telegram bot that listens to a chat for YouTube links. When a YouTube link is detected, the application automatically downloads the video and stores it to a network location.

## Features
- Listens to messages in a Telegram bot chat
- Automatically detects YouTube links in messages
- Downloads YouTube videos in the highest available quality
- Stores downloaded videos to a configured network location
- Organizes videos in folders by date
- Runs as a system service on Raspberry Pi

## Requirements
- Python 3.7+
- Raspberry Pi (or any Debian-based Linux system)
- Network storage accessible from the Raspberry Pi

## Installation
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd medialoader
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the example environment file and edit it with your configuration:
   ```bash
   cp .env.example .env
   nano .env
   ```
5. Set the following variables in the `.env` file:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather
   - `MEDIA_STORAGE_PATH`: Path to your network storage (e.g., `/mnt/network_share/youtube_videos`)
   - `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

## Setting up Network Storage

1. Create a mount point:
   ```bash
   sudo mkdir -p /mnt/network_share
   ```

2. For NFS shares, add to `/etc/fstab`:
   ```
   server:/path/to/share /mnt/network_share nfs defaults 0 0
   ```

3. For SMB/CIFS shares, install cifs-utils and add to `/etc/fstab`:
   ```bash
   sudo apt-get install cifs-utils
   ```
   ```
   //server/share /mnt/network_share cifs username=user,password=pass,vers=3.0,uid=1000,gid=1000 0 0
   ```

4. Mount the network share:
   ```bash
   sudo mount -a
   ```

## Running as a Service

1. Copy the service file to the systemd directory:
   ```bash
   sudo cp telegram-youtube-bot.service /etc/systemd/system/
   ```

2. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable telegram-youtube-bot
   sudo systemctl start telegram-youtube-bot
   ```

3. Check the service status:
   ```bash
   sudo systemctl status telegram-youtube-bot
   ```

## Usage
1. Create a Telegram bot using [BotFather](https://core.telegram.org/bots#botfather) and obtain the bot token.
2. Add the bot to a chat or start a direct conversation with it.
3. Send a message with a YouTube link (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`).
4. The bot will download the video and save it to the configured network location.

## Logs
You can check the logs using:
```bash
sudo journalctl -u telegram-youtube-bot -f
```

## License
This project is licensed under the MIT License.