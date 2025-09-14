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


async def process_message(message: discord.Message, mode: DownloadMode):
    """Download video from supported link if not already processed."""
    if not should_process_message(message, client):
        return False
    parts = message.content.strip().split()
    url = parts[0]
    category = parts[1] if len(parts) > 1 else "Uncategorized"
    category_folder = getTargetFolder(mode, category)

    os.makedirs(category_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if category.lower() == "cars" or mode == DownloadMode.AUDIO:
        outputUri_template = os.path.join(category_folder, "%(title)s.%(ext)s")
    else:
        outputUri_template = os.path.join(category_folder, f"{category}_IG_{timestamp}.%(ext)s")

    try:
        subprocess.run(
            ["yt-dlp", "-o", outputUri_template, url] + (["-x"] if mode == DownloadMode.AUDIO else []),
            check=True
        )
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
