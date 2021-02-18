import discord
from discord.ext import commands
from collections import namedtuple
import base64
import random
from utils.fuzzy import finder
import inspect
import asyncio
import os
import psutil
import humanize
import time
import datetime

start_time = time.time()
TOKEN = os.getenv("TOKEN")
from utils.subclasses import AnimeColor
from utils.embed import EmbedBase
from jishaku.paginators import WrappedPaginator, PaginatorInterface
import json
import aiohttp
import io
import pathlib


class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.countdownused = []
        self.thing = {}

    @commands.command(aliases=["randomtoken"])
    async def randombottoken(self, ctx, user: discord.User = None):
        """
        Generate a completely random token from a server member THE TOKEN IS NOT VALID so don't be scared
        """
        if not user:
            member = random.choice(ctx.guild.members)
        else:
            member = user
        byte_first = str(member.id).encode('ascii')
        first_encode = base64.b64encode(byte_first)
        first = first_encode.decode('ascii')
        time_rn = datetime.datetime.utcnow()
        epoch_offset = int(time_rn.timestamp())
        bytes_int = int(epoch_offset).to_bytes(10, "big")
        bytes_clean = bytes_int.lstrip(b"\x00")
        unclean_middle = base64.standard_b64encode(bytes_clean)
        middle = unclean_middle.decode('utf-8').rstrip("==")
        Pair = namedtuple("Pair", "min max")
        num = Pair(48, 57)  # 0 - 9
        cap_alp = Pair(65, 90)  # A - Z
        cap = Pair(97, 122)  # a - z
        select = (num, cap_alp, cap)
        last = ""
        for each in range(27):
            pair = random.choice(select)
            last += str(chr(random.randint(pair.min, pair.max)))
        final = ".".join((first, middle, last))
        embed = discord.Embed(color=self.bot.color, title=f"{member.display_name}'s token", description=final)
        await ctx.send(embed=embed)

    @commands.command()
    async def emoji(self, ctx, *, search: str = None):
        lists = []
        paginator = WrappedPaginator(max_size=500, prefix="", suffix="")
        if search is not None:
            emojis = finder(search, self.bot.emojis, key=lambda i: i.name, lazy=False)
            if not emojis:
                return await ctx.send("no emoji found")
            for i in emojis:
                if i.animated:
                    lists.append(f"{str(i)} `<a:{i.name}:{i.id}>`")
                else:
                    lists.append(f"{str(i)} `<:{i.name}:{i.id}>`")
            paginator.add_line("\n".join(lists))
            interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
            return await interface.send_to(ctx)
        for i in self.bot.emojis:
            if i.animated:
                lists.append(f"{str(i)} `<a:{i.name}:{i.id}>`")
            else:
                lists.append(f"{str(i)} `<:{i.name}:{i.id}>`")
        paginator.add_line("\n".join(lists))
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)

    @commands.command()
    async def vote(self, ctx):
        embed = discord.Embed(color=self.bot.color)
        embed.add_field(name="Click here to vote",
                        value="[Top.gg Link](https://top.gg/bot/787927476177076234/vote)\n[Bot for discord](https://botsfordiscord.com/bot/787927476177076234/vote)\n[discord bot list](https://discordbotlist.com/bots/anime-quotepic-bot/upvote)\n[botlist.space](https://botlist.space/bot/787927476177076234/upvote)\n[discord extreme list](https://discordextremelist.xyz/en-US/bots/787927476177076234)")
        embed.set_footer(text="Thank you so much <3",
                         icon_url="https://media.tenor.com/images/c5caf59fd029c206db34cbb14956b8e2/tenor.gif")
        await ctx.send(embed=embed)

    @commands.command()
    async def source(self, ctx):
        embed = discord.Embed(color=self.bot.color)
        embed.add_field(name="source of the bot",
                        value=f"the bot bot is currenly private source so dm {self.bot.get_user(590323594744168494).mention}")
        await ctx.send(embed=embed)
        # branch = 'main'
        # if command is None:
        #     return await ctx.send(source_url)

        # if command == 'help':
        #     src = type(self.bot.help_command)
        #     module = src.__module__
        #     filename = inspect.getsourcefile(src)
        # else:
        #     obj = self.bot.get_command(command.replace('.', ' '))
        #     if obj is None:
        #         return await ctx.send('Could not find command.')

        #     src = obj.callback.__code__
        #     module = obj.callback.__module__
        #     filename = src.co_filename

        # lines, firstlineno = inspect.getsourcelines(src)
        # if not module.startswith('discord'):
        #     location = os.path.relpath(filename).replace('\\', '/')
        # else:
        #     location = module.replace('.', '/') + '.py'
        #     source_url = 'https://github.com/Rapptz/discord.py'
        #     branch = 'master'

        # final_url = f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        # await ctx.send(final_url)

    @commands.command()
    async def charles(self, ctx, *, text):
        await ctx.trigger_typing()
        session = aiohttp.ClientSession()
        res = await session.post('https://bin.charles-bot.com/documents', data=text)
        if res.status != 200:
            raise commands.CommandError(f"charles bin down with status code {res.status}")
        data = await res.json()
        await ctx.send(f"https://bin.charles-bot.com/{data['key']}")

    @commands.command()
    async def type(self, ctx, seconds: int):
        """
      the bot will type for the time u provide yes idk what i made
        """

        def check(m):
            return m.author == ctx.author and m.content == "end"

        async with ctx.channel.typing():
            await asyncio.sleep(seconds)
            await ctx.send(f"typed for {seconds} seconds")

    @commands.command()
    @commands.Cooldown(1, 10, commands.BucketType.user)
    async def raw(self, ctx, message_id: int, channel_id: int = None):
        await ctx.trigger_typing()
        raw = await self.bot.http.get_message(channel_id or ctx.channel.id, message_id)
        # raw = str(resp).replace("|", "\u200b|").replace("*", "\u200b*").replace("`", "\u200b`").replace("~", "\u200b~").replace(">", "\u200b>").replace('"', "'")
        # raw = json.loads(raw)
        # raw = json.dumps(raw, indent=4)
        raw = json.dumps(raw, indent=4)
        raw = raw.replace("|", "\u200b|").replace("*", "\u200b*").replace("`", "\u200b`").replace("~",
                                                                                                  "\u200b~").replace(
            ">", "\u200b>")
        if len(raw) > 1900:
            paginator = WrappedPaginator(max_size=500, prefix="```json", suffix="```")
            paginator.add_line(raw)
            interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
            return await interface.send_to(ctx)
        embed = discord.Embed(color=AnimeColor.lighter_green(), description=f"```json\n{raw}```")
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        await ctx.trigger_typing()
        embed = await EmbedBase.embed(self, ctx)
        embed.set_author(name="Use this link to invite")
        embed.add_field(
            name="link ",
            value=
            "https://discord.com/api/oauth2/authorize?client_id=787927476177076234&permissions=2146823543&scope=bot"
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def dm(self, ctx):
        await ctx.trigger_typing()
        embed = await EmbedBase.embed(self, ctx)
        embed.set_author(
            name=
            "Most commands can be done here if you don't want other people to see it"
        )
        await ctx.author.send(embed=embed)
        embed = await EmbedBase.embed(self, ctx)
        embed.set_author(name="your dm here")
        await ctx.reply(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        start = time.perf_counter()
        await ctx.trigger_typing()
        end = time.perf_counter()
        final_latency = end - start
        embed = await EmbedBase.embed(self, ctx)
        embed.set_author(name="ping")
        embed.add_field(name="<:stab:744345955637395586>  websocket latency",
                        value=f"```{round(self.bot.latency * 1000)} ms ```")
        embed.add_field(name="<a:typing:597589448607399949> API latency",
                        value=f"```{round(final_latency * 1000)} ms ```")
        # start1 = time.perf_counter()
        # await self.bot.db.fetch("SELECT * FROM prefixes LIMIT 1")
        # final_latencty2 = time.perf_counter() - start1
        # embed.add_field(name="<a:typing:597589448607399949>  database latency", value=f"```{round(final_latencty2 * 1000)} ms ```")
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.Cooldown(1, 30, commands.BucketType.channel)
    async def rtt(self, ctx):
        lists = []
        for i in range(5):
            start = time.perf_counter()
            await ctx.trigger_typing()
            end = time.perf_counter()
            final_latency = end - start
            lists.append(str(round(final_latency * 1000)))
        lists = " ms \n".join(lists)
        embed = discord.Embed(color=0x00ff6a, description=f"```py\n{lists} ms```")
        await ctx.send(embed=embed)

    @commands.command()
    async def systeminfo(self, ctx):
        await ctx.trigger_typing()
        m = self.bot.psutil_process.memory_full_info()
        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name="System Infos", value=f"• `{humanize.naturalsize(m.rss)}` physical memory used\n",
                        inline=False)
        await ctx.reply(embed=embed)

    @commands.command(name="guilds", aliases=["servers"])
    async def gUILDSservERS(self, ctx):
        await ctx.trigger_typing()
        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name=" number of servers / guilds the bot in ", value=len(self.bot.guilds))
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefixforbot: str):
        await ctx.trigger_typing()
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = prefixforbot
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)
        embed = await EmbedBase.embed(self, ctx)
        embed.set_author(name=f"prefix changed to {prefixforbot}")
        embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
                         icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.Cooldown(1, 60, commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        await ctx.trigger_typing()
        channel = self.bot.get_channel(792568174167326720)
        embed = await EmbedBase.embed(self, ctx)
        embed.set_author(name=ctx.author)
        embed.add_field(name=" suggestion ", value=suggestion)
        embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
                         icon_url=ctx.author.avatar_url)
        await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    # @commands.command()
    # async def help(self, ctx):
    #   await ctx.message.add_reaction("<:mochaok:788473006606254080>")
    #   await ctx.trigger_typing()
    #   embed = discord.Embed(color=0x2ecc71)
    #   embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    #   embed.add_field(name="music \U0001f3b5", value="`join`, `leave`, `lyrics`, `now`, `pause`, `play`, `queue`, `remove`, `resume`, `shuffle`, `skip`, `stop`, `summon`, `volume`", inline=False)
    #   embed.add_field(name="anime <:ZeroTwoUWU:708570252350455848>", value="`addnewpicture`, `animequote`, `randomquote`", inline=False)
    #   # embed.add_field(name="currency 🍓 ", value="`balance`, `withdraw`, `deposit`, `shop`, `beg`, `slot`, `buy`, `sell`, `send`, `steal`, `bag`", inline=False)
    #   embed.add_field(name="moderation \U0001f6e1", value="`kick`, `ban`, `unban`", inline=False)
    #   embed.add_field(name="fun <a:milkandmochadance:788470536455585802>", value="`meme`, `scared`", inline=False)
    #   embed.add_field(name="Others <a:milkguitar:788469773599113247>", value="`usage`, `ping`, `dm`, `guilds`", inline=False)
    #   embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms", icon_url=ctx.author.avatar_url)
    #   await ctx.send(embed=embed)

    @commands.command(aliases=["info"])
    async def about(self, ctx):
        p = pathlib.Path('./')
        cm = cr = fn = cl = ls = fc = cc = 0
        for f in p.rglob('*.py'):
            if str(f).startswith("venv"):
                continue
            fc += 1
            with f.open() as of:
                for l in of.readlines():
                    l = l.strip()
                    cc += len(l)
                    if l.startswith('class'):
                        cl += 1
                    if l.startswith('def'):
                        fn += 1
                    if l.startswith('async def'):
                        cr += 1
                    if '#' in l:
                        cm += 1
                    ls += 1
        m = self.bot.psutil_process.memory_full_info()
        start = time.perf_counter()
        await ctx.trigger_typing()
        end = time.perf_counter()
        final_latency = end - start
        owner = await self.bot.application_info()
        owner = owner.owner
        embed = await EmbedBase.embed(self, ctx)
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        embed.add_field(name="infos",
                        value=f"Guilds: {len(self.bot.guilds)} \n Members: {len(self.bot.users)} \n Creators: {owner} \n Libary: discord.py \n Command used (since last reboot): {self.bot.counter} \n Invite link:  [click ](https://discord.com/api/oauth2/authorize?client_id=787927476177076234&permissions=2146823543&scope=bot) \n Messages Cached: {len(self.bot.cached_messages)}",
                        inline=False)
        embed.add_field(name="System Infos",
                        value=f"> `{humanize.naturalsize(m.rss)}` physical memory used\n> `{self.bot.psutil_process.cpu_percent() / psutil.cpu_count()}%` CPU usage\n> running on PID `{self.bot.psutil_process.pid}`\n> `{self.bot.psutil_process.num_threads()}` thread(s)",
                        inline=False)
        embed.add_field(name="<:stab:744345955637395586>  websocket latency",
                        value=f"```{round(self.bot.latency * 1000)} ms ```")
        embed.add_field(name="<a:typing:597589448607399949> API latency",
                        value=f"```{round(final_latency * 1000)} ms ```")
        embed.add_field(name=" stats ",
                        value=f"```file: {fc}\nline: {ls:,}\ncharacters: {cc} \nclass: {cl}\nfunction: {fn}\ncoroutine: {cr}\ncomment: {cm:,}```",
                        inline=False)
        embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
                         icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command()
    async def privacy(self, ctx):
        await ctx.message.add_reaction("<:mochaok:788473006606254080>")
        policy = """
    1. The only data the bot will collect is your userid.
    2. the userid is used for the currency system
    3. as I said is your user id is only for the currency system
    4. I do not share any data with anyone
    5. you may dm me for any concerns by joining this server https://discord.gg/DRBQMTqrNe
    6. if you wish to remove your data please feel free to dm me in this server https://discord.gg/DRBQMTqrNe
  """
        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name="policy", value=policy)
        embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        await ctx.trigger_typing()
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name="uptime ", value=text)
        embed.add_field(name="Check bot uptime", value="[Check bot uptime](https://stats.uptimerobot.com/v935zFWnqv)")
        await ctx.reply(embed=embed)

    @commands.command()
    async def countdown(self, ctx, count_to: int):
        if str(ctx.channel.id) in self.countdownused:
            await ctx.send("this channel already have a countdown started")
            return
        else:
            self.countdownused.append(str(ctx.channel.id))
            counter = count_to
            message = await ctx.reply(f"start counting down to {counter} will dm you when is done")
            for i in range(counter):
                counter -= 1
                await asyncio.sleep(1)
                if counter == 0:
                    await message.edit(content=str(counter))
                    await ctx.author.send("Countdown finshed")
                    self.countdownused.remove(str(ctx.channel.id))
                    return


def setup(bot):
    bot.add_cog(Others(bot))
