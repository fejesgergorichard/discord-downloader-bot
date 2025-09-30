import discord
from discord.ext import commands
import subprocess, os
from datetime import datetime
from enum import Enum
import config

class DownloadMode(Enum):
    VIDEO = "video"
    AUDIO = "audio"

class Downloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def should_process(self, message: discord.Message) -> bool:
        if message.author == self.bot.user:
            return False
        if not any(domain in message.content for domain in ["instagram.com", "youtube.com", "youtu.be"]):
            return False

        for reaction in message.reactions:
            if reaction.me and str(reaction.emoji) == "✅":
                return False

        return True

    def getTargetFolder(self, mode: DownloadMode, category: str):
        if mode == DownloadMode.AUDIO:
            category_folder = config.AUDIO_OUTPUT_FOLDER
        else:
            category_folder = os.path.join(config.VIDEO_OUTPUT_FOLDER, category)
        return category_folder

    def build_yt_dlp_cmd(self, url: str, output: str, mode: DownloadMode, fallback: bool =False) -> list[str]:
        """Factory for yt-dlp commands."""
        if mode == DownloadMode.AUDIO:
            audio_format = "m4a" if fallback else "mp3"
            return ["yt-dlp", "-o", output, "-x", "--audio-format", audio_format, url]
        else:
            merge_format = "mkv" if fallback else "mp4"
            return ["yt-dlp", "-o", output, "--merge-output-format", merge_format, url]

    async def process_message(self, message: discord.Message, mode: DownloadMode):
        """Download video from supported link if not already processed."""
        if not self.should_process(message):
            return False
            
        print(f"Processing message: '{message}' in mode: '{mode}'")
        await message.add_reaction("👀")

        parts = message.content.strip().split()
        url = parts[0]
        category = parts[1] if len(parts) > 1 else "Uncategorized"
        title = f"{parts[2]}.%(ext)s" if len(parts) > 2 else "%(title)s.%(ext)s"
        category_folder = self.getTargetFolder(mode, category)

        os.makedirs(category_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if category.lower() == "cars" or mode == DownloadMode.AUDIO:
            outputUri_template = os.path.join(category_folder, title)
        else:
            outputUri_template = os.path.join(category_folder, f"{category}_{timestamp}.%(ext)s")

        try:
            cmd = self.build_yt_dlp_cmd(url, outputUri_template, mode, fallback=False)
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                fallback_cmd = self.build_yt_dlp_cmd(url, outputUri_template, mode, fallback=True)
                fallback_result = subprocess.run(fallback_cmd, capture_output=True, text=True)
                if fallback_result.returncode != 0:
                    raise Exception(
                        f"Both main format (mp4/mp3) and fallback (mkv,m4a) failed.\n"
                        f"MP4/MP3 error: {result.stderr}\n"
                        f"M4A/MKV error: {fallback_result.stderr}"
                    )

            await message.remove_reaction("👀", self.bot.user)
            await message.add_reaction("✅")
            return True

        except Exception as e:
            await message.add_reaction("❌")
            await message.channel.send(f"Error downloading {url}: {e}")
            return False

    async def check_channel_history(self, channel_id: int, mode: DownloadMode):
        """Re-check old messages in a channel when bot starts."""
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"⚠️ Could not find channel {channel_id}")
            return

        print(f"Checking history for channel {channel_id} ({mode})")
        count = 0
        success_count = 0

        async for message in channel.history(limit=200):
            if self.should_process(message):
                count += 1
                if await self.process_message(message, mode):
                    success_count += 1

        if count > 0:
            await channel.send(f"✅ Processed {success_count}/{count} messages in mode: {mode}.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == config.VIDEO_CHANNEL_ID:
            await self.process_message(message, DownloadMode.VIDEO)
        elif message.channel.id == config.AUDIO_CHANNEL_ID:
            await self.process_message(message, DownloadMode.AUDIO)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ Downloader Cog ready as {self.bot.user}")
        await self.check_channel_history(config.VIDEO_CHANNEL_ID, DownloadMode.VIDEO)
        await self.check_channel_history(config.AUDIO_CHANNEL_ID, DownloadMode.AUDIO)

async def setup(bot):
    await bot.add_cog(Downloader(bot))
