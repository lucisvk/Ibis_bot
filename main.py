import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

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

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    try:
        await member.send(
            f"Hey {member.name}, thanks for joining the server!"
        )
    except discord.Forbidden:
        pass

admin_log_channel_id = 1458266406062653614  # your admin channel ID

banned_words = ["shit", "nigga", "bitch"]



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if any(word in message.content.lower() for word in banned_words):
        await message.delete()

        # DM user
        try:
            await message.author.send(
                f"⚠️ Your message was deleted: `{message.content}` Please refrain from saying restricted words or you will be banned."
            )
        except discord.Forbidden:
            # Optionally notify admins
            admin_channel = bot.get_channel(admin_log_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"{message.author} tried to send a banned word but DMs are blocked."
                )

    await bot.process_commands(message)

    await bot.process_commands(message)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def ibis(ctx):
    await ctx.send(
        f"Ugh what do you want human {ctx.author.mention}!"
    )

@bot.tree.command(name="ibis_commands", description="Show IBIS commands")
async def ibis_commands(interaction: discord.Interaction):
    await interaction.response.send_message("""
       📌 **General**
`/ibis_commands` → Show this command list
`!ping` → Check bot status
`!about` → About IBIS

🎵 **Music**
`!play <song/URL>` → Play music
`!pause` → Pause music
`!resume` → Resume music
`!skip` → Skip song
`!stop` → Stop music

🎉 **Fun**
`!fact` → Random fact
`!joke` → Random joke
`!quote` → Random quote
`!poll <question>` → Create a poll

🛠 **Utility**
`!clear <number>` → Clear messages
`!serverinfo` → Server info
`!userinfo [@user]` → User info
    """, ephemeral=True)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)