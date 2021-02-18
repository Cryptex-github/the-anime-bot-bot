import discord
from discord.ext import commands
from utils.fuzzy import finder


class moderations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # @commands.has_permissions(manage_messages=True)
    # @commands.bot_has_permissions(manage_roles=True)
    # async def unmute(self, ctx, user: discord.Member, *, reason="None"):
    #   if finder("Muted", user.roles, key=lambda t: t.name, lazy=False)[:3] == []:
    #     return await ctx.send("user not muted")
    #   role = finder("Muted", user.roles, key=lambda t: t.name, lazy=False)[0]
    #   await user.remove_roles(role, reason=f"{ctx.author}: {reason} ({ctx.author.id})")
    #   embed = discord.Embed(color=self.bot.color)
    #   embed.add_field(name=f"`{user}` have been unmuted", value=f"with reason: `{reason}`")
    #   return await ctx.send(embed=embed)
    # @commands.command()
    # @commands.has_permissions(manage_messages=True)
    # @commands.bot_has_permissions(manage_roles=True)
    # async def mute(self, ctx, user: discord.Member, *, reason="None"):
    #   permissions=discord.Permissions.text()
    #   permissions.send_messages=False
    #   if finder("Muted", user.roles, key=lambda t: t.name, lazy=False)[:3] != []:
    #     return await ctx.send("user already muted")
    #   if finder("Muted", ctx.guild.roles, key=lambda t: t.name, lazy=False)[:3] == []:
    #     role = await ctx.guild.create_role(name="Muted", permissions=permissions, reason="Muted role")
    #     await user.add_roles(role, reason=f"{ctx.author}: {reason} ({ctx.author.id})")
    #     embed = discord.Embed(color=self.bot.color)
    #     embed.add_field(name=f"`{user}` have been muted", value=f"with reason: `{reason}`")
    #     return await ctx.send(embed=embed)
    #   else:
    #     role = finder("Muted", ctx.guild.roles, key=lambda t: t.name, lazy=False)[0]
    #     if role.permissions != permissions:
    #       await role.edit(permissions=permissions)
    #     await user.add_roles(role, reason=f"{ctx.author}: {reason} ({ctx.author.id})")
    #     embed = discord.Embed(color=self.bot.color)
    #     embed.add_field(name=f"`{user}` have been muted", value=f"with reason: `{reason}`")
    #     return await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member, *, reason):
        embed = discord.Embed(color=self.bot.color)
        embed.add_field(name=f"`{user}` have been warned", value=f"with reason: `{reason}`")
        await ctx.send(embed=embed)
        embed = discord.Embed(color=self.bot.color)
        embed.add_field(name=f"You have been warned", value=f"with reason: `{reason}`")
        await user.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int):
        await ctx.trigger_typing()
        counts = await ctx.channel.purge(limit=limit)
        await ctx.send(content=f" purged {len(counts)} messages", delete_after=10)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member.id == 590323594744168494:
            return await ctx.reply("hmm nope not gonna do that")
        if ctx.author.top_role < member.top_role:
            return await ctx.reply(f"Your role is lower then {member}")
        await ctx.trigger_typing()
        await member.kick(reason=reason)
        await ctx.reply(f"Kicked {member}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member.id == 590323594744168494:
            return await ctx.reply("hmm nope not gonna do that")
        if ctx.author.top_role < member.top_role:
            return await ctx.reply(f"Your role is lower then {member}")
        await ctx.trigger_typing()
        await member.ban(reason=reason)
        await ctx.reply(f"banned {member}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, *, member: discord.User):
        await ctx.trigger_typing()
        member = discord.Object(id=member.id)
        try:
            await member.unban(reason=f"{ctx.author.id}: unbanned")
        except:
            await ctx.send("can not unban")


def setup(bot):
    bot.add_cog(moderations(bot))
