import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def setup_hook():
    """Called when the bot is being set up, before it connects to Discord."""
    await bot.load_extension("cogs.moderation")
    await bot.load_extension("cogs.utility")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f" IBIS online as {bot.user}")

bot.run(TOKEN, log_level=logging.INFO)