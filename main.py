import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import pandas as pd
import re

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename='discord.log',
    encoding='utf-8',
    mode='w'
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


try:
    df = pd.read_csv("Bannedwords.csv")
    df.columns = df.columns.str.strip().str.lower()
    banned_words = set(df["word"].str.strip().str.lower())
    print(f"Loaded {len(banned_words)} banned words.")
except Exception as e:
    print(" Failed to load Bannedwords.csv:", e)
    banned_words = set()

admin_log_channel_id = 1458266406062653614


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f" System running Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        await member.send(f"Hey {member.name}, thanks for joining!")
    except discord.Forbidden:
        pass

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    for word in banned_words:
        if re.search(rf"\b{re.escape(word)}\b", content):
            await message.delete()
            try:
                await message.author.send(
                    "⚠️ Your message was removed for violating server rules."
                )
            except discord.Forbidden:
                admin_channel = bot.get_channel(admin_log_channel_id)
                if admin_channel:
                    await admin_channel.send(
                        f"⚠️ {message.author} used a banned word but DMs are disabled."
                    )
            return

    await bot.process_commands(message)


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def ibis(ctx):
    await ctx.send(f"Ugh what do you want, human {ctx.author.mention}?")

@bot.tree.command(name="ibis_commands", description="Show IBIS commands")
async def ibis_commands(interaction: discord.Interaction):
    await interaction.response.send_message(
        """
 **General**
`/ibis_commands` → Show commands
`!ibis` → Talk to IBIS

 **Music**
`!play <song>`
`!pause`
`!resume`
`!skip`
`!stop`

 **Fun**
`!fact`
`!joke`
`!quote`
`!poll <question>`
        """,
        ephemeral=True
    )


bot.run(token, log_handler=handler, log_level=logging.INFO)