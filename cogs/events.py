import asyncio
import discord
import logging
from discord.ext import commands, tasks

logging.getLogger('asyncio').setLevel(logging.CRITICAL)
import json
import time
from utils.subclasses import GlobalCooldown
import asyncpg
import os

discord_bot_list = os.getenv("discord_bot_list")
bots_for_discord = os.getenv("bots_for_discord")
topgg = os.getenv("topgg")
discord_extreme_list = os.getenv("discord_extreme_list")
botlist_space = os.getenv("botlist_space")
POSTGRE_DATABASE_URL = os.getenv("POSTGRE_DATABASE_URL")
import aiozaneapi
import subprocess
from utils.asyncstuff import asyncexe
from menus import menus
import aiohttp
import sys
import traceback
import json
import asyncdagpi


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.ws_recieved = 0
        self.bot.send = 0
        self.status.start(bot)
        self.post.start(bot)
        self.update.start(bot)
        self.chunk.start()
        # self.post.start()
        self.errors_list = []
        self.bot.counter = 0

    @tasks.loop(minutes=1)
    async def status(self, bot):
        await bot.wait_until_ready()
        await bot.change_presence(activity=discord.Game(name=f"{len(bot.guilds)} guilds and {len(bot.users)} users"))

    @tasks.loop(minutes=5)
    async def update(self, bot):
        await bot.wait_until_ready()
        message = bot.get_channel(809204640054640641).get_partial_message(809205344814891040)
        current_time = time.time()
        lists = []
        difference = int(current_time - bot.start_time) / 60
        lists.append(f"Received {bot.socket_receive} {bot.socket_receive // difference} per minute")
        for i, (n, v) in enumerate(bot.socket_stats.most_common()):
            lists.append(f"{n:<30} {v:<20} {round(v / difference, 3)} /minute")
        lists = "\n".join(lists)
        await message.edit(content=f"```\n{lists}\n```")

    @tasks.loop(minutes=1)
    async def chunk(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            if not guild.chunked:
                await guild.chunk()
            await asyncio.sleep(1)

    @tasks.loop(minutes=1)
    async def post(self, bot):
        await bot.wait_until_ready()
        session = aiohttp.ClientSession()
        await session.post("https://top.gg/api/bots/787927476177076234/stats", headers={"Authorization": topgg},
                           data=json.dumps({"server_count": len(bot.guilds), "shard_count": bot.shard_count}))
        await session.post("https://discordbotlist.com/api/v1/bots/anime-quotepic-bot/stats",
                           headers={"Authorization": discord_bot_list},
                           data={"voice_connections": len(bot.voice_clients), "users": len(bot.users),
                                 "guilds": len(bot.guilds)})
        async with aiohttp.ClientSession().post("https://api.discordextremelist.xyz/v2/bot/787927476177076234/stats",
                                                headers={"Authorization": discord_extreme_list,
                                                         "Content-Type": "application/json"}, data=json.dumps(
                        {"guildCount": len(bot.guilds), "shardCount": len(bot.shards)})) as resp:
            pass
        await session.post("https://botsfordiscord.com/api/bot/787927476177076234",
                           headers={"Content-Type": "application/json", "Authorization": bots_for_discord},
                           data=json.dumps({"server_count": len(bot.guilds)}))
        await session.post("https://api.botlist.space/v1/bots/787927476177076234",
                           headers={"Authorization": botlist_space, "Content-Type": "application/json"},
                           data=json.dumps({"shards": [len(bot.guilds) / 2, len(bot.guilds) / 2]}))
        await session.close()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.bot.counter += 1

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.bot.send += 1

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        pass

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        pass

    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild):
        pass

    @commands.Cog.listener()
    async def on_guild_available(self, guild):
        pass

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        pass

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        pass

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        pass

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        pass

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        pass

    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild):
        pass

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        pass

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        pass

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        pass

    @commands.Cog.listener()
    async def on_private_channel_pins_update(self, channel, last_pin):
        pass

    @commands.Cog.listener()
    async def on_private_channel_update(self, before, after):
        pass

    @commands.Cog.listener()
    async def on_private_channel_create(self, channel):
        pass

    @commands.Cog.listener()
    async def on_private_channel_delete(self, channel):
        pass

    @commands.Cog.listener()
    async def on_raw_reaction_clear_emoji(self, payload):
        pass

    @commands.Cog.listener()
    async def on_reaction_clear_emoji(self, reaction):
        pass

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        pass

    @commands.Cog.listener()
    async def on_reaction_clear(self, message, reactions):
        pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        pass

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        pass

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        pass

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        pass

    @staticmethod
    @asyncexe()
    def on_message_delete_(self, message):
        self.bot._message_cache.pop(message.id)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        try:
            await self.bot._message_cache.get(message.id).delete()
            await self.on_message_delete_(self, message)
        except:
            pass

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        pass

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        pass

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        pass

    @commands.Cog.listener()
    async def on_socket_raw_send(self, payload):
        pass

    @commands.Cog.listener()
    async def on_socket_raw_receive(self, msg):
        self.bot.ws_recieved += 1

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        pass

    @commands.Cog.listener()
    async def on_resumed(self):
        pass

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        pass

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        pass

    @commands.Cog.listener()
    async def on_disconnect(self):
        pass

    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id):
        pass

    @commands.Cog.listener()
    async def on_connect(self):
        pass

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        if not payload.cached_message:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if message.embeds != []:
                return
            await self.bot.process_commands(message)

    @staticmethod
    @asyncexe()
    def on_message_edit_(self, old):
        self.bot._message_cache.pop(old.id)

    @commands.Cog.listener()
    async def on_message_edit(self, old, new):
        if new.embeds:
            return
        await self.bot.process_commands(new)

    @staticmethod
    @asyncexe()
    def on_guild_join_(guild):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        prefixes[str(guild.id)] = "$"
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.on_guild_join_(guild)
        channel = self.bot.get_channel(798330449058725898)
        await channel.send(f"**{guild.name}** just added the bot with **{guild.member_count}** members ")

    @staticmethod
    @asyncexe()
    def on_guild_remove_(guild):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.on_guild_remove_(guild)
        channel = self.bot.get_channel(799806497118224415)
        await channel.send(f"**{guild.name}** just kicked the bot with **{guild.member_count}** members ")

    @commands.Cog.listener()
    async def on_message(self, message):
        self.bot.deleted_message_cache[message.id] = message
        if message.content == "<@!787927476177076234>" and not message.author.bot:
            await message.channel.send("Hii there why u ping me smh oh i mean hii my prefix is `ovo ` ")
        # mentions = message.mentions
        # try:
        #   for x in mentions:
        #     if x == self.bot.user:
        #       with open("prefixes.json", "r") as f:
        #         prefixes = json.load(f)
        #     prefix_for_guild = prefixes[str(message.guild.id)]
        #     embed = discord.Embed(color=0x2ecc71)
        #     embed.set_author(name=f"bot prefix for this guild is   {prefix_for_guild}")
        #     embed.set_footer(text=f"requested by {message.author} response time : {round(self.bot.latency * 1000)} ms", icon_url=message.author.avatar_url)
        #     await message.channel.send(embed=embed)
        # except:
        #   pass
        # if message.channel.id == 796603184587210752:
        #   voter = await self.bot.get_user(message.content)
        #   channel = self.bot.get_channel(791518421920907265)
        #   embed = discord.Embed(color=0x2ecc71)
        #   embed.set_author(name=voter, icon_url=voter.avatar_url, url="https://top.gg/bot/787927476177076234/vote")
        #   embed.add_field(name=f"{voter} just upvoted our bot yay", value="upvote our bot here https://top.gg/bot/787927476177076234/vote", inline=False)
        #   await channel.send(embed=embed)
        #   await voter.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(name=f"{len(self.bot.guilds)} guilds"))
        print(len(self.bot.guilds))
        print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(self.bot))

    @staticmethod
    @asyncexe()
    def embed(text):
        embed = discord.Embed(color=0xFF0000, title="An error occured", description=text)
        return embed

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = commands.CommandNotFound
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return
        self.errors_list.append(error)
        if isinstance(error, commands.DisabledCommand):
            embed = await self.embed(f"{ctx.command} has been disabled.")
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.NSFWChannelRequired):
            embed = await self.embed("this command must be used in NSFW channel")
            return await ctx.send(embed=embed)
        elif isinstance(error, asyncio.TimeoutError):
            embed = await self.embed("timeout")
            return await ctx.send(embed=embed)
        elif isinstance(error, discord.errors.HTTPException):
            embed = await self.embed(f"HTTPException {error.text}")
            return await ctx.send(embed=embed)
        elif isinstance(error, GlobalCooldown):
            embed = await self.embed(
                f"You have hit the global ratelimit try again in {round(error.retry_after)} seconds")
            return await ctx.send(embed=embed)
        elif isinstance(error, aiozaneapi.GatewayError):
            embed = await self.embed("Zane api have a error")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.errors.NotOwner):
            embed = await self.embed("You must be the bot owner to use this command")
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                embed = await self.embed("{ctx.command} can not be used in Private Messages.")
                await ctx.author.send(embed=embed)
            except discord.HTTPException:
                pass
        elif isinstance(error, AttributeError):
            return
        elif isinstance(error, commands.errors.InvalidEndOfQuotedStringError):
            embed = await self.embed("Make sure to put a space between the quotes")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.ConversionError):
            embed = await self.embed(f"Unable to convert {error.converter}")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = await self.embed(f"Unable to convert")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = await self.embed(f"You are missing `{error.param.name}` argument")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            embed = await self.embed(f"dude chill try again in {round(error.retry_after)} seconds")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = await self.embed(f"Bot is missing {error.missing_perms} to do that")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = await self.embed("you do not have permission to do that")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = await self.embed("the bot do not have permission to do that")
            await ctx.reply(embed=embed)
        elif isinstance(error, asyncdagpi.errors.BadUrl):
            embed = await self.embed("You did not pass in the right arguments")
            await ctx.reply(embed=embed)
        elif isinstance(error, asyncdagpi.errors.ApiError):
            embed = await self.embed("The image API have a error")
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(color=0xFF0000, description=f"```py\n{error}```")
            await ctx.send(embed=embed)
            # # print(''.join(prettify_exceptions.DefaultFormatter().format_exception(type(error), error, error.__traceback__)))
            # print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            # # traceback.print_exception(''.join(prettify_exceptions.DefaultFormatter().format_exception(type(error), error, error.__traceback__)))
            # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command()
    @commands.is_owner()
    async def fix_errors(self, ctx):
        counter = 0
        for count in self.errors_list:
            counter += 1
        self.errors_list.clear()
        await ctx.reply(f"thanks for fixing {counter} errors")

    @commands.command()
    @commands.is_owner()
    async def errors(self, ctx):
        await ctx.reply(self.errors_list)


def setup(bot):
    bot.add_cog(Events(bot))
