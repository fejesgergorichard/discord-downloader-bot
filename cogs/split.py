import os
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from PIL import Image
import io
import config


class Split(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="split", description="Split an image into parts")
    @app_commands.describe(
        image="Image to split",
        parts="How many parts to split into (default: 3)",
        direction="Split direction: vertical or horizontal"
    )
    async def split(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        parts: int = 3,
        direction: str = "vertical"
    ):
        """Slash command to split an image into N parts."""
        await interaction.response.defer()

        # Read image
        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes))
        w, h = img.size
        timestamp = datetime.now().strftime("%Y_%m_%d")

        files = []
        if direction.lower() == "vertical":
            slice_width = w // parts
            for i in range(parts):
                base_filename=f"{timestamp}_part_{i+1}.png"
                filepath = os.path.join(config.MIDJOURNEY_OUTPUT_FOLDER, base_filename)
                left = i * slice_width
                right = (i + 1) * slice_width if i < parts - 1 else w
                crop = img.crop((left, 0, right, h))
                buf = io.BytesIO()
                crop.save(buf, format="PNG")
                crop.save(filepath)
                buf.seek(0)
                files.append(discord.File(buf, filename=base_filename))

        else:  # horizontal
            slice_height = h // parts
            for i in range(parts):
                base_filename=f"{timestamp}_part_{i+1}.png"
                filepath = os.path.join(config.MIDJOURNEY_OUTPUT_FOLDER, base_filename)
                top = i * slice_height
                bottom = (i + 1) * slice_height if i < parts - 1 else h
                crop = img.crop((0, top, w, bottom))
                buf = io.BytesIO()
                crop.save(buf, format="PNG")
                crop.save(filepath)
                buf.seek(0)
                files.append(discord.File(buf, filename=base_filename))

        await interaction.followup.send(
            content=f"Here’s your image split into {parts} {direction} parts:",
            files=files
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Split(bot))
