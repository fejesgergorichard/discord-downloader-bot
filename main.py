import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

initial_cogs = ["cogs.downloader", "cogs.midjourney"]

@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user}")

async def main():
    async with bot:
        # Load extensions properly
        for cog in initial_cogs:
            await bot.load_extension(cog)
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
