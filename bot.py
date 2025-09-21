import discord
import subprocess
import os
from enum import Enum
from datetime import datetime

# === CONFIG ===
TOKEN = "MTQxNDMyNDYzNzc3MjQxOTE2NA.GyOTki.fdy4bCyQQNMwWkD_ohKjmBjrhIK36rwkI7hmdU" 
VIDEO_CHANNEL_ID = 1413212543832555540 
VIDEO_OUTPUT_FOLDER = r"D:\MUSIC\GFX\ifeelmanythings\VIDEOS\Raw"

AUDIO_CHANNEL_ID = 1414330646955954317 
AUDIO_OUTPUT_FOLDER = r"D:\sidejoy_packs\_Song Samples"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

class DownloadMode(Enum):
    VIDEO = "video"
    AUDIO = "audio"

def should_process_message(message, client):
    """Check if the message is valid and should be processed."""
    if message.author == client.user:
        return False

    if not any(domain in message.content for domain in ["instagram.com", "youtube.com", "youtu.be"]):
        return False

    for reaction in message.reactions:
        if reaction.me and str(reaction.emoji) == "✅":
            return False

    return True

def getTargetFolder(mode: DownloadMode, category: str):
    if mode == DownloadMode.AUDIO:
        category_folder = AUDIO_OUTPUT_FOLDER
    else:
        category_folder = os.path.join(VIDEO_OUTPUT_FOLDER, category)
    return category_folder

def build_yt_dlp_cmd(url: str, output: str, mode: DownloadMode, fallback: bool = False) -> list[str]:
    """
    Factory for yt-dlp commands.
    - Audio: extracts audio, tries mp3 first, m4a if fallback=True.
    - Video: tries mp4 first, mkv if fallback=True.
    """
    if mode == DownloadMode.AUDIO:
        audio_format = "m4a" if fallback else "mp3"
        return [
            "yt-dlp",
            "-o", output,
            "-x",
            "--audio-format", audio_format,
            url,
        ]
    else:
        merge_format = "mkv" if fallback else "mp4"
        return [
            "yt-dlp",
            "-o", output,
            "--merge-output-format", merge_format,
            url,
        ]

async def process_message(message: discord.Message, mode: DownloadMode):
    """Download video from supported link if not already processed."""
    if not should_process_message(message, client):
        return False
        
    print(f"Processing message: '{message}' in mode: '{mode}'")
    await message.add_reaction("👀")

    parts = message.content.strip().split()
    url = parts[0]
    category = parts[1] if len(parts) > 1 else "Uncategorized"
    title = f"{parts[2]}.%(ext)s" if len(parts) > 2 else "%(title)s.%(ext)s"
    category_folder = getTargetFolder(mode, category)

    os.makedirs(category_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if category.lower() == "cars" or mode == DownloadMode.AUDIO:
        outputUri_template = os.path.join(category_folder, title)
    else:
        outputUri_template = os.path.join(category_folder, f"{category}_IG_{timestamp}.%(ext)s")

    try:
        cmd = build_yt_dlp_cmd(url, outputUri_template, mode, fallback=False)
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            fallback_cmd = build_yt_dlp_cmd(url, outputUri_template, mode, fallback=True)
            fallback_result = subprocess.run(fallback_cmd, capture_output=True, text=True)
            if fallback_result.returncode != 0:
                raise Exception(
                    f"Both main format (mp4/mp3) and fallback (mkv,m4a) failed.\n"
                    f"MP4/MP3 error: {result.stderr}\n"
                    f"M4A/MKV error: {fallback_result.stderr}"
                )

        await message.remove_reaction("👀", client.user)
        await message.add_reaction("✅")
        return True

    except Exception as e:
        await message.add_reaction("❌")
        await message.channel.send(f"Error downloading {url}: {e}")
        return False


async def check_channel_history(channelId: int, mode: DownloadMode):
    print(f"Checking channel history for channel: '{channelId}' in mode: '{mode}'")
    channel = client.get_channel(channelId)
    count = 0
    successCount = 0

    async for message in channel.history(limit=200):
        if should_process_message(message, client):
            count += 1
        success = await process_message(message, mode)

        if success:
            successCount += 1

    if count > 0:
        await channel.send(f"✅ Successfully Processed {successCount}/{count} messages in mode: {mode}.")


@client.event
async def on_ready():
    print(f"✅ Bot connected as {client.user}")
    await check_channel_history(VIDEO_CHANNEL_ID, DownloadMode.VIDEO)
    await check_channel_history(AUDIO_CHANNEL_ID, DownloadMode.AUDIO)

@client.event
async def on_message(message):
    if message.channel.id == VIDEO_CHANNEL_ID:
        await process_message(message, DownloadMode.VIDEO)
    if message.channel.id == AUDIO_CHANNEL_ID:
        await process_message(message, DownloadMode.AUDIO)

client.run(TOKEN)
