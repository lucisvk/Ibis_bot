import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ibis(self, ctx):
        await ctx.send(" Ugh… what do you want, human?")

    @discord.app_commands.command(
        name="ibis_commands",
        description="Show all IBIS commands"
    )
    async def ibis_commands(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            """
**IBIS Commands**

**General**
`!ibis` → Talk to IBIS
`/ibis_commands` → Show commands

**Moderation Commands**
`!ban @user [reason]` → Ban a user
`!ban_multi --member @user1 @user2 --reason <text> --days <n>` → Ban multiple users
`!unban <username/userid>` → Unban a user
`!kick @user [reason]` → Kick a user
`!mute @user [minutes] [reason]` → Timeout/mute a user
`!unmute @user` → Remove timeout from a user
`!addrole @user @role` → Add a role to a user
`!removerole @user @role` → Remove a role from a user
`!clear [amount]` → Delete messages (1-100)
`!warn @user [reason]` → Warn a user
`!userinfo [@user]` → Get user information

**Music** (Coming Soon)
`!play`
`!pause`
`!skip`

**Fun** (Coming Soon)
`!fact`
`!joke`
""",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(General(bot))