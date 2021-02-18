import discord
from discord.ext import commands
import copy
import datetime


class reactionrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_message_id = 810353319896940655
        self.emoji_to_role = {
            665620560503373834: 810331947133173810,
            708570252350455848: 810339401578184805,
            744576474551550041: 810336014887157760,
            694418426634043392: 810336158008737792,
            675167362366046238: 810337057544077363,
            788473301214822410: 810337124271783956,
            701513799869530173: 810337691282571304,
            615241758670061568: 810359228006793246
        }

    def cog_check(self, ctx):
        if not ctx.guild:
            return False
        elif not ctx.guild.id == 810331898278182952:
            return False
        else:
            return True

    @commands.command()
    async def wattpad(self, ctx):
        await ctx.send(
            f"Hello, {ctx.author.mention} Please type in your wattpad username in order to create your own role")

        def check(m):
            return m.guild.id == 810331898278182952 and m.author.id == ctx.author.id

        m = await self.bot.wait_for("message", check=check, timeout=120)
        for i in ctx.guild.roles:
            if str(ctx.author.id) in i.name:
                return await ctx.send("it seems like you already have a role")
        await ctx.send(
            f"ok so the username will be `{m.content}`, you may type `cancel` to redo the process if is correct type `yes`")
        m2 = await self.bot.wait_for("message", check=check, timeout=120)
        if m2.content == "end":
            return await ctx.send("ended")
        elif m2.content == "yes":
            pass
        role_ = await ctx.guild.create_role(name=f"{m.content}({ctx.author.id})", color=discord.Color.random(),
                                            mentionable=True)
        await ctx.send(f"I have created a role {role_.mention} for you")
        await ctx.author.add_roles(role_, reason="Wattpad command")

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        message = self.bot.deleted_message_cache.get(payload.message_id)
        if not message:
            return
        older_message = copy.copy(message)
        message._update(payload.data)
        if message.guild.id != 810331898278182952:
            return
        if message.author.bot:
            return
        embed = discord.Embed(color=self.bot.color, title="Message edit")
        embed.set_author(name=message.author.display_name, icon_url=str(message.author.avatar_url))
        embed.add_field(name="Before", value=older_message.content)
        embed.add_field(name="After", value=message.content)
        await self.bot.get_channel(811829054293934130).send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.guild_id == 810331898278182952:
            msg = self.bot.deleted_message_cache.get(payload.message_id)
            if not msg:
                return
            embed = discord.Embed(color=self.bot.color)
            embed.set_author(name=msg.author.display_name, icon_url=str(msg.author.avatar_url))
            embed.add_field(name="Message delete", value=f"Message: {msg.content}")
            await self.bot.get_channel(811829054293934130).send(embed=embed)
            self.bot.deleted_message_cache.pop(payload.message_id)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == 810331898278182952:
            embed = discord.Embed(color=self.bot.color, timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Member leave",
                            value=f"<:bsd_chuuyasob:810406446457159680> {member.mention} just leave. We now have {member.guild.member_count} members")
            await self.bot.get_channel(811815859982172211).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 810331898278182952:
            embed = discord.Embed(color=self.bot.color, timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Member join",
                            value=f"<:bsd_dazaisparkle:810407099883454534> Welcome, {member.mention} We now have {member.guild.member_count} members")
            await self.bot.get_channel(811815047898464266).send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Gives a role based on a reaction emoji."""
        # Make sure that the message the user is reacting to is the one we care about
        if payload.message_id != self.role_message_id:
            return

        try:
            role_id = self.emoji_to_role[payload.emoji.id]
        except KeyError:
            # If the emoji isn't the one we care about then exit as well.
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        try:
            # Finally add the role
            await payload.member.add_roles(role)
        except discord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Removes a role based on a reaction emoji."""
        # Make sure that the message the user is reacting to is the one we care about
        if payload.message_id != self.role_message_id:
            return

        try:
            role_id = self.emoji_to_role[payload.emoji.id]
        except KeyError:
            # If the emoji isn't the one we care about then exit as well.
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            # Makes sure the member still exists and is valid
            return

        try:
            # Finally, remove the role
            await member.remove_roles(role)
        except discord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass


def setup(bot):
    bot.add_cog(reactionrole(bot))
