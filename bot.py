import discord
import subprocess
import os
from datetime import datetime

# === CONFIG ===
TOKEN = "YOUR_BOT_TOKEN"  # replace with your bot token
CHANNEL_ID = 123456789012345678  # replace with the channel ID
OUTPUT_FOLDER = r"D:\MUSIC\GFX\ifeelmanythings\VIDEOS\Raw\Instagram"

# Setup intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

async def process_message(message: discord.Message):
    """Download video from Instagram link if not already processed."""
    if message.author == client.user:
        return

    if "instagram.com" not in message.content:
        return

    # Skip if already reacted ✅
    for reaction in message.reactions:
        if reaction.me and str(reaction.emoji) == "✅":
            return

    parts = message.content.strip().split()
    url = parts[0]
    category = parts[1] if len(parts) > 1 else "Uncategorized"

    category_folder = os.path.join(OUTPUT_FOLDER, category)
    os.makedirs(category_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_template = os.path.join(category_folder, f"{category}_IG_{timestamp}.%(ext)s")

    try:
        subprocess.run(
            ["yt-dlp", "-o", output_template, url],
            check=True
        )
        await message.add_reaction("✅")
    except Exception as e:
        await message.add_reaction("❌")
        await message.channel.send(f"Error downloading {url}: {e}")

@client.event
async def on_ready():
    print(f"✅ Bot connected as {client.user}")

    # Get the channel
    channel = client.get_channel(CHANNEL_ID)

    # Check last 200 messages for missed links
    async for message in channel.history(limit=200):
        await process_message(message)

@client.event
async def on_message(message):
    if message.channel.id == CHANNEL_ID:
        await process_message(message)

client.run(TOKEN)
