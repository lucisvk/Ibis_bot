import discord
from discord.ext import commands
import pandas as pd
import re
from typing import List, Optional
from datetime import timedelta

ADMIN_LOG_CHANNEL_ID = 1458266406062653614

class BanFlags(commands.FlagConverter):
    member: List[discord.Member]
    reason: str = "No reason provided"
    days: int = 1

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_words = self.load_words()

    def load_words(self):
        try:
            df = pd.read_csv("data/Bannedwords.csv")
            return set(df["word"].str.lower().str.strip())
        except Exception as e:
            print("Failed to load banned words:", e)
            return set()


    @commands.command(name="ban", aliases=["banuser"])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Ban a member from the server"""
        if member is None:
            await ctx.send(" Please mention a user to ban.")
            return
        
        if member == ctx.author:
            await ctx.send("You cannot ban yourself.")
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("You cannot ban someone with equal or higher roles.")
            return
        
        try:
            await member.ban(reason=f"{ctx.author}: {reason}", delete_message_days=1)
            await ctx.send(f"🔨 Banned {member.mention} | Reason: {reason}")
        except discord.Forbidden:
            await ctx.send(" I don't have permission to ban this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(name="ban_multi", aliases=["banmultiple"])
    @commands.has_permissions(ban_members=True)
    async def ban_multi(self, ctx, *, flags: BanFlags):
        """Ban multiple members at once"""
        for member in flags.member:
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                continue
            try:
                await member.ban(
                    reason=flags.reason,
                    delete_message_days=flags.days
                )
            except:
                pass

        names = ", ".join(m.name for m in flags.member)
        await ctx.send(f"🔨 Banned {names} | Reason: {flags.reason}")

    @commands.command(name="unban", aliases=["unbanuser"])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """Unban a user from the server"""
        banned_users = [entry async for entry in ctx.guild.bans()]
        
        if isinstance(member, str):
            # Try to find by username#discriminator or user ID
            for ban_entry in banned_users:
                user = ban_entry.user
                if member.lower() in str(user).lower() or str(user.id) == member:
                    try:
                        await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author}")
                        await ctx.send(f" Unbanned {user.mention}")
                        return
                    except Exception as e:
                        await ctx.send(f"Failed to unban: {str(e)}")
                        return
        
        await ctx.send("User not found in ban list.")

    @commands.command(name="kick", aliases=["kickuser"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Kick a member from the server"""
        if member is None:
            await ctx.send("Please mention a user to kick.")
            return
        
        if member == ctx.author:
            await ctx.send(" You cannot kick yourself.")
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("You cannot kick someone with equal or higher roles.")
            return
        
        try:
            await member.kick(reason=f"{ctx.author}: {reason}")
            await ctx.send(f"👢 Kicked {member.mention} | Reason: {reason}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this user.")
        except Exception as e:
            await ctx.send(f" An error occurred: {str(e)}")

    @commands.command(name="mute", aliases=["timeout"])
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member = None, duration: int = 60, *, reason: str = "No reason provided"):
        """Timeout/mute a member (duration in minutes, max 28 days)"""
        if member is None:
            await ctx.send(" Please mention a user to mute.")
            return
        
        if member == ctx.author:
            await ctx.send(" You cannot mute yourself.")
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(" You cannot mute someone with equal or higher roles.")
            return
        
        # Limit to 28 days (40320 minutes)
        duration = min(duration, 40320)
        timeout_duration = timedelta(minutes=duration)
        
        try:
            await member.timeout(timeout_duration, reason=f"{ctx.author}: {reason}")
            await ctx.send(f"🔇 Muted {member.mention} for {duration} minutes | Reason: {reason}")
        except discord.Forbidden:
            await ctx.send(" I don't have permission to mute this user.")
        except Exception as e:
            await ctx.send(f" An error occurred: {str(e)}")

    @commands.command(name="unmute", aliases=["untimeout"])
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member = None):
        """Remove timeout/mute from a member"""
        if member is None:
            await ctx.send(" Please mention a user to unmute.")
            return
        
        try:
            await member.timeout(None, reason=f"Unmuted by {ctx.author}")
            await ctx.send(f"🔊 Unmuted {member.mention}")
        except discord.Forbidden:
            await ctx.send(" I don't have permission to unmute this user.")
        except Exception as e:
            await ctx.send(f" An error occurred: {str(e)}")

    @commands.command(name="addrole", aliases=["giverole", "roleadd"])
    @commands.has_permissions(manage_roles=True)
    async def add_role(self, ctx, member: discord.Member = None, *, role: discord.Role = None):
        """Add a role to a member"""
        if member is None:
            await ctx.send(" Please mention a user.")
            return
        
        if role is None:
            await ctx.send(" Please mention a role to add.")
            return
        
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(" You cannot assign a role equal to or higher than your highest role.")
            return
        
        if role in member.roles:
            await ctx.send(f" {member.mention} already has the {role.mention} role.")
            return
        
        try:
            await member.add_roles(role, reason=f"Added by {ctx.author}")
            await ctx.send(f" Added {role.mention} to {member.mention}")
        except discord.Forbidden:
            await ctx.send(" I don't have permission to add this role.")
        except Exception as e:
            await ctx.send(f" An error occurred: {str(e)}")

    @commands.command(name="removerole", aliases=["takerole", "roleremove"])
    @commands.has_permissions(manage_roles=True)
    async def remove_role(self, ctx, member: discord.Member = None, *, role: discord.Role = None):
        """Remove a role from a member"""
        if member is None:
            await ctx.send(" Please mention a user.")
            return
        
        if role is None:
            await ctx.send(" Please mention a role to remove.")
            return
        
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(" You cannot remove a role equal to or higher than your highest role.")
            return
        
        if role not in member.roles:
            await ctx.send(f" {member.mention} doesn't have the {role.mention} role.")
            return
        
        try:
            await member.remove_roles(role, reason=f"Removed by {ctx.author}")
            await ctx.send(f" Removed {role.mention} from {member.mention}")
        except discord.Forbidden:
            await ctx.send(" I don't have permission to remove this role.")
        except Exception as e:
            await ctx.send(f" An error occurred: {str(e)}")

    @commands.command(name="clear", aliases=["purge", "delete"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        """Clear/purge messages from the channel"""
        if amount < 1 or amount > 100:
            await ctx.send(" Please specify a number between 1 and 100.")
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
            await ctx.send(f"🗑️ Deleted {len(deleted) - 1} message(s)", delete_after=5)
        except discord.Forbidden:
            await ctx.send(" I don't have permission to delete messages.")
        except Exception as e:
            await ctx.send(f" An error occurred: {str(e)}")

    @commands.command(name="warn", aliases=["warning"])
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Warn a member"""
        if member is None:
            await ctx.send(" Please mention a user to warn.")
            return
        
        if member == ctx.author:
            await ctx.send(" You cannot warn yourself.")
            return
        
        try:
            await member.send(f" You have been warned in {ctx.guild.name}\nReason: {reason}")
            await ctx.send(f" Warned {member.mention} | Reason: {reason}")
        except discord.Forbidden:
            await ctx.send(f" Warned {member.mention} (could not DM) | Reason: {reason}")
        except Exception as e:
            await ctx.send(f" An error occurred: {str(e)}")

    @commands.command(name="userinfo", aliases=["whois", "user"])
    @commands.has_permissions(view_audit_log=True)
    async def user_info(self, ctx, member: discord.Member = None):
        """Get information about a user"""
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(title=f"User Info: {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.display_name, inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unknown", inline=False)
        embed.add_field(name="Roles", value=", ".join([r.mention for r in member.roles[1:]]) if len(member.roles) > 1 else "None", inline=False)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()

        for word in self.banned_words:
            if re.search(rf"\b{re.escape(word)}\b", content):
                await message.delete()
                try:
                    await message.author.send(
                        "Your message was removed for rule violations."
                    )
                except discord.Forbidden:
                    channel = self.bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                    if channel:
                        await channel.send(
                            f"{message.author} used banned words but has DMs closed."
                        )
                return
        
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            await member.send(f"Hey {member.name}, welcome to the server!")
        except discord.Forbidden:
            pass


async def setup(bot):
    await bot.add_cog(Moderation(bot))