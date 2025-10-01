import discord
import os
import io
from discord.ext import commands
from datetime import datetime
from PIL import Image
import config
import re

class MidJourneyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(config.MIDJOURNEY_OUTPUT_FOLDER, exist_ok=True)

    def should_process(self, message: discord.Message) -> bool:
        if message.author == self.bot.user:
            return False

        if message.channel.id != config.MIDJOURNEY_CHANNEL_ID:
            return False

        if "midjourney" not in message.author.name.lower():
            return False
      
        if not message.attachments:
            return False

        for reaction in message.reactions:
            if reaction.me and str(reaction.emoji) == "✅":
                return False

        if not self.has_u_buttons(message):
            return False
        
        return True


    def has_u_buttons(self, message: discord.Message) -> bool:
        """Check if MidJourney grid message contains U1-U4 buttons."""
        if not message.components:
            print("message has no components")
            return False

        for row in message.components:  # ActionRow
            for component in row.children:
                # Component has .label attribute if it's a button
                if getattr(component, "label", None) and component.label.startswith("U"):
                    print(f"Found U button: {component.label}")
                    return True

        return False


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.process_message(message)

    async def process_message(self, message: discord.Message):
        print(f"Processing Midjourney message: '{message}'")
        prompt = message.content or "mj"
        short_prompt = "_".join(prompt.split()[:4]).replace(":", "").replace("/", "").replace("\\", "")
        safe_prompt = re.sub(r'[\\/*?:"<>|]', "", short_prompt)

        for attachment in message.attachments:
            if not attachment.filename.lower().endswith(("png", "jpg", "jpeg")):
                continue
            
            img_bytes = await attachment.read()
            img = Image.open(io.BytesIO(img_bytes))

            print("img read")

            w, h = img.size
            quadrants = [
                img.crop((0, 0, w // 2, h // 2)), 
                img.crop((w // 2, 0, w, h // 2)), 
                img.crop((0, h // 2, w // 2, h)),  
                img.crop((w // 2, h // 2, w, h)) 
            ]

            print(f"quadrants done {len(quadrants)}")

            timestamp = datetime.now().strftime("%Y_%m_%d")
            print(f"timestamp: {timestamp}")
            for idx, quad in enumerate(quadrants, start=1):
                base_filename = f"{timestamp}_{safe_prompt}_{idx}.png"
                filepath = os.path.join(config.MIDJOURNEY_OUTPUT_FOLDER, base_filename)

                counter = 1
                while os.path.exists(filepath):
                    base_filename = f"{timestamp}_{safe_prompt}_{idx}_{counter}.png"
                    filepath = os.path.join(config.MIDJOURNEY_OUTPUT_FOLDER, base_filename)
                    counter += 1

                try:
                    quad.save(filepath)
                    print(f"✅ Saved {filepath}")
                except Exception as e:
                    print(f"❌ Failed to save {filepath}: {e}")
                    return False

            await message.remove_reaction("👀", self.bot.user)
            await message.add_reaction("✅")
            await message.channel.send(f"Split MJ grid into 4 variants → saved in `{config.MIDJOURNEY_OUTPUT_FOLDER}`")

            return True

    async def check_channel_history(self, channel_id: int):
        """Re-check old messages in a channel when bot starts."""
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"⚠️ Could not find channel {channel_id}")
            return

        print(f"Checking history for channel {channel_id}")
        count = 0
        success_count = 0

        async for message in channel.history(limit=2):
            if self.should_process(message):
                await message.add_reaction("👀")
                count += 1
                if await self.process_message(message):
                    success_count += 1

        if count > 0:
            await channel.send(f"✅ Processed {success_count}/{count} messages.")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ Midjourney Cog ready as {self.bot.user}")
        await self.check_channel_history(config.MIDJOURNEY_CHANNEL_ID)

async def setup(bot):
    await bot.add_cog(MidJourneyCog(bot))