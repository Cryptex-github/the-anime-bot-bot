import asyncio
import ujson
import typing
import config
import base64
import datetime
import inspect
import io
import json
import os
import pathlib
import random
import time
from collections import namedtuple

import aiohttp
import discord
import humanize
import psutil
from discord.ext import commands
from utils.subclasses import AnimeContext

# from github import Github
from utils.asyncstuff import asyncexe
from utils.embed import embedbase
from utils.fuzzy import finder
from utils.subclasses import AnimeColor

from jishaku.paginators import (
    PaginatorEmbedInterface,
    PaginatorInterface,
    WrappedPaginator,
)

gittoken = config.gittoken
# g = Github(gittoken)
TOKEN = config.TOKEN


def is_in_server():
    async def predicate(ctx):
        guild = ctx.bot.get_guild(796459063982030858)
        await guild.chunk()
        lists = [i.id for i in guild.members if not i.bot]
        return ctx.message.author.id in lists

    return commands.check(predicate)


class others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.countdownused = []
        self.thing = {}

    @commands.command()
    @is_in_server()
    async def ree(
        self, ctx: AnimeContext, *id: typing.Union[int, discord.abc.User]
    ):
        channel = self.bot.get_channel(823418220832751646)
        for id in id:
            if isinstance(id, discord.abc.User):
                id = id.id
            await channel.send(
                f"<https://discord.com/api/oauth2/authorize?client_id={id}&guild_id=796459063982030858&scope=bot%20applications.commands&permissions=641195745>"
            )

    @commands.command()
    async def owners(self, ctx):
        embed = discord.Embed(
            color=self.bot.color,
            description=f"""
      <:rooSip:824129426181980191> Owner: {str(self.bot.get_user(590323594744168494)) if self.bot.get_user(590323594744168494) else str(await self.bot.fetch_user(590323594744168494))}
      <:rooSellout:739614245343199234> Rich Co-owner: {str(self.bot.get_user(711057339360477184)) if self.bot.get_user(711057339360477184) else str(await self.bot.fetch_user(711057339360477184))}
""",
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def emojioptions(self, ctx: AnimeContext, enabled: bool):
        await self.bot.db.execute(
            "INSERT INTO emojioptions (user_id, enabled) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET enabled = $2 WHERE emojioptions.user_id = $1 ",
            ctx.author.id,
            enabled,
        )
        self.bot.emojioptions[ctx.author.id] = enabled
        await ctx.send(
            embed=discord.Embed(
                color=self.bot.color,
                description=f"you have set emoji auto response to {enabled}",
            )
        )

    @commands.command()
    async def votes(self, ctx):
        async with self.bot.session.get(
            "https://top.gg/api/bots/787927476177076234/votes",
            headers={"Authorization": (config.topgg)},
        ) as resp:
            js = await resp.json()
            js = js[:5]
            voters = [f"**{i.get('username')}**" for i in js]
            embed = discord.Embed(
                color=self.bot.color,
                title="Top 5 Voters",
                description="\n".join(voters),
            )
            embed.set_footer
            await ctx.send(embed=embed)

    @commands.command()
    async def snipe(self, ctx):
        """
        no this is never happening, people delete message for a reason and you just snipe that just not right.
        """
        await ctx.send(
            "no this is never happening, people delete message for a reason and you just snipe that just not right."
        )

    @commands.command()
    async def support(self, ctx):
        await ctx.send("https://discord.gg/bUpF6d6bP9")

    @commands.command(aliases=["randomtoken"])
    async def randombottoken(
        self, ctx: AnimeContext, user: discord.User = None
    ):
        """
        Generate a completely random token from a server member THE TOKEN IS NOT VALID so don't be scared
        """
        member = random.choice(ctx.guild.members) if not user else user
        byte_first = str(member.id).encode("ascii")
        first_encode = base64.b64encode(byte_first)
        first = first_encode.decode("ascii")
        time_rn = datetime.datetime.utcnow()
        epoch_offset = int(time_rn.timestamp())
        bytes_int = int(epoch_offset).to_bytes(10, "big")
        bytes_clean = bytes_int.lstrip(b"\x00")
        unclean_middle = base64.standard_b64encode(bytes_clean)
        middle = unclean_middle.decode("utf-8").rstrip("==")
        Pair = namedtuple("Pair", "min max")
        num = Pair(48, 57)  # 0 - 9
        cap_alp = Pair(65, 90)  # A - Z
        cap = Pair(97, 122)  # a - z
        select = (num, cap_alp, cap)
        last = ""
        for _ in range(27):
            pair = random.choice(select)
            last += str(chr(random.randint(pair.min, pair.max)))
        final = ".".join((first, middle, last))
        embed = discord.Embed(
            color=self.bot.color,
            title=f"{member.display_name}'s token",
            description=final,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def emoji(self, ctx: AnimeContext, *, search: str = None):
        lists = []
        paginator = WrappedPaginator(max_size=500, prefix="", suffix="")
        if search != None:
            emojis = finder(
                search, self.bot.emojis, key=lambda i: i.name, lazy=False
            )
            if emojis == []:
                return await ctx.send("no emoji found")
            for i in emojis:
                if i.animated == True:
                    lists.append(f"{str(i)} `<a:{i.name}:{i.id}>`")
                else:
                    lists.append(f"{str(i)} `<:{i.name}:{i.id}>`")
            paginator.add_line("\n".join(lists))
            interface = PaginatorInterface(
                ctx.bot, paginator, owner=ctx.author
            )
            return await interface.send_to(ctx)
        for i in self.bot.emojis:
            if i.animated == True:
                lists.append(f"{str(i)} `<a:{i.name}:{i.id}>`")
            else:
                lists.append(f"{str(i)} `<:{i.name}:{i.id}>`")
        paginator.add_line("\n".join(lists))
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)

    @commands.command()
    async def vote(self, ctx):
        embed = discord.Embed(color=self.bot.color)
        embed.add_field(
            name="Click here to vote",
            value="[Top.gg Link](https://top.gg/bot/787927476177076234/vote)\n[Bot for discord](https://botsfordiscord.com/bot/787927476177076234/vote)\n[discord bot list](https://discordbotlist.com/bots/anime-quotepic-bot/upvote)\n[botlist.space](https://botlist.space/bot/787927476177076234/upvote)\n[discord extreme list](https://discordextremelist.xyz/en-US/bots/787927476177076234)",
        )
        embed.set_footer(
            text="Thank you so much <3",
            icon_url="https://media.tenor.com/images/c5caf59fd029c206db34cbb14956b8e2/tenor.gif",
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def source(self, ctx: AnimeContext, *, command: str = None):
        embed = discord.Embed(color=self.bot.color)
        embed.add_field(
            name="source of the bot",
            value=f"oh hi another source rob rob human\nMy sources are on github find it yourself\n[if you really want it](https://github.com/Cryptex-github/the-anime-bot-bot)\n\n[Licensed under GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.txt)",
        )
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
    async def charles(self, ctx: AnimeContext, *, text):
        await ctx.trigger_typing()
        res = await self.bot.session.post(
            "https://bin.charles-bot.com/documents", data=text
        )
        if res.status != 200:
            raise commands.CommandError(
                f"charles bin down with status code {res.status}"
            )
        data = await res.json()
        await ctx.send(f"https://bin.charles-bot.com/{data['key']}")

    @commands.command()
    async def type(self, ctx: AnimeContext, seconds: int):
        """
        the bot will type for the time u provide yes idk what i made the max is 5 minute :O
        """
        seconds = min(seconds, 300)

        async with ctx.channel.typing():
            await asyncio.sleep(seconds)
            await ctx.send(f"typed for {seconds} seconds")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def raw(
        self, ctx: AnimeContext, message_id: int, channel_id: int = None
    ):
        await ctx.trigger_typing()
        raw = await self.bot.http.get_message(
            channel_id or ctx.channel.id, message_id
        )
        # raw = str(resp).replace("|", "\u200b|").replace("*", "\u200b*").replace("`", "\u200b`").replace("~", "\u200b~").replace(">", "\u200b>").replace('"', "'")
        # raw = json.loads(raw)
        # raw = json.dumps(raw, indent=4)
        raw = ujson.dumps(raw, indent=4)
        raw = (
            raw.replace("|", "\u200b|")
            .replace("*", "\u200b*")
            .replace("`", "\u200b`")
            .replace("~", "\u200b~")
            .replace(">", "\u200b>")
        )
        if len(raw) > 1900:
            paginator = WrappedPaginator(
                max_size=500, prefix="```json", suffix="```"
            )
            paginator.add_line(raw)
            interface = PaginatorInterface(
                ctx.bot, paginator, owner=ctx.author
            )
            return await interface.send_to(ctx)
        embed = discord.Embed(
            color=AnimeColor.lighter_green(), description=f"```json\n{raw}```"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        await ctx.trigger_typing()
        embed = await embedbase.embed(self, ctx)
        embed.set_author(name="Use this link to invite")
        embed.add_field(
            name="link ",
            value="[Invite me](https://cryptex-github.github.io/the-anime-bot-bot/invite)",
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def dm(self, ctx):
        await ctx.trigger_typing()
        embed = await embedbase.embed(self, ctx)
        embed.set_author(
            name="Most commands can be done here if you don't want other people to see it"
        )
        await ctx.author.send(embed=embed)
        embed = await embedbase.embed(self, ctx)
        embed.set_author(name="your dm here")
        await ctx.reply(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        start = time.perf_counter()
        await ctx.trigger_typing()
        end = time.perf_counter()
        final_latency = end - start
        start = time.perf_counter()
        await self.bot.db.fetch("SELECT 1")
        postgres = time.perf_counter() - start
        postgres = round(postgres * 1000)
        embed = await embedbase.embed(self, ctx)
        embed.set_author(name="ping")
        embed.add_field(
            name="<:stab:744345955637395586>  websocket latency",
            value=f"```{round(self.bot.latency * 1000)} ms ```",
        )
        embed.add_field(
            name="<:postgres:821095695746203689> Postgre sql latency",
            value=f"```{postgres} ms```",
        )
        embed.add_field(
            name="<a:typing:597589448607399949> API latency",
            value=f"```{round(final_latency * 1000)} ms ```",
        )
        # start1 = time.perf_counter()
        # await self.bot.db.fetch("SELECT * FROM prefixes LIMIT 1")
        # final_latencty2 = time.perf_counter() - start1
        # embed.add_field(name="<a:typing:597589448607399949>  database latency", value=f"```{round(final_latencty2 * 1000)} ms ```")
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.channel)
    async def rtt(self, ctx):
        lists = []
        for _ in range(5):
            start = time.perf_counter()
            await ctx.trigger_typing()
            end = time.perf_counter()
            final_latency = end - start
            lists.append(str(round(final_latency * 1000)))
        lists = " ms \n".join(lists)
        embed = discord.Embed(
            color=0x00FF6A, description=f"```py\n{lists} ms```"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def systeminfo(self, ctx):
        await ctx.trigger_typing()
        m = self.bot.psutil_process.memory_full_info()
        embed = await embedbase.embed(self, ctx)
        embed.add_field(
            name="System Info",
            value=f"• `{humanize.naturalsize(m.rss)}` physical memory used\n",
            inline=False,
        )
        await ctx.reply(embed=embed)

    @commands.command(name="guilds", aliases=["servers"])
    async def gUILDSservERS(self, ctx):
        await ctx.trigger_typing()
        embed = await embedbase.embed(self, ctx)
        embed.add_field(
            name=" number of servers / guilds the bot in ",
            value=len(self.bot.guilds),
        )
        await ctx.reply(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx):
        """
        Shows prefixes and avaiable prefix commands
        """
        embed = discord.Embed(
            color=self.bot.color,
            title="Change prefix",
            description=f"Current guild prefixes are: `{', '.join(self.bot.prefixes[ctx.guild.id])}`\n\nTo add a prefix run: {ctx.prefix}prefix add `prefix`\n\nTo remove a prefix run: {ctx.prefix}prefix remove `prefix`",
        )
        return await ctx.send(embed=embed)

    @prefix.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def prefix_remove(self, ctx: AnimeContext, prefix_to_remove: str):
        """
        Remove a prefix for your server
        Example:
        ovo prefix remove prefixname
        if your prefix contain space:
        ovo prefix remove "prefixname "
        """
        if prefix_to_remove not in self.bot.prefixes[ctx.guild.id]:
            return await ctx.send(
                "This prefix don't exist maybe you made a typo? Case and space Sensitive"
            )
        old_prefixes = await self.bot.db.fetchrow(
            "SELECT * FROM prefix WHERE guild_id=$1", ctx.guild.id
        )
        old_prefixes = old_prefixes["prefix"]
        new_prefixes = old_prefixes
        new_prefixes.remove(prefix_to_remove)
        await self.bot.db.execute(
            "INSERT INTO prefix (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2 WHERE prefix.guild_id = $1",
            ctx.guild.id,
            new_prefixes,
        )
        self.bot.prefixes[ctx.guild.id] = new_prefixes
        embed = discord.Embed(
            color=self.bot.color,
            title="Change prefix",
            description=f"Succefully appended new prefix New prefixes are: {', '.join(new_prefixes)}",
        )
        return await ctx.send(embed=embed)

    @prefix.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def prefix_add(self, ctx: AnimeContext, prefixforbot: str):
        """
        Add a new prefix for your server
        Example:
        ovo prefix add newprefix
        if your prefix contain space:
        ovo prefix add "newprefix "
        """
        old_prefixes = await self.bot.db.fetchrow(
            "SELECT * FROM prefix WHERE guild_id=$1", ctx.guild.id
        )
        old_prefixes = old_prefixes["prefix"]
        new_prefixes = old_prefixes
        new_prefixes.append(prefixforbot)
        await self.bot.db.execute(
            "INSERT INTO prefix (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2 WHERE prefix.guild_id = $1",
            ctx.guild.id,
            new_prefixes,
        )
        self.bot.prefixes[ctx.guild.id] = new_prefixes
        embed = discord.Embed(
            color=self.bot.color,
            title="Change prefix",
            description=f"Succefully appended new prefix New prefixes are: {', '.join(new_prefixes)}",
        )
        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def suggest(self, ctx: AnimeContext, *, suggestion):
        await ctx.trigger_typing()
        channel = self.bot.get_channel(792568174167326720)
        embed = await embedbase.embed(self, ctx)
        embed.set_author(name=ctx.author)
        embed.add_field(name=" suggestion ", value=suggestion)
        embed.set_footer(
            text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
            icon_url=ctx.author.avatar_url,
        )
        await channel.send(
            embed=embed, allowed_mentions=discord.AllowedMentions.none()
        )
        await ctx.reply(
            embed=embed, allowed_mentions=discord.AllowedMentions.none()
        )

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
    #   embed.add_field(name="others <a:milkguitar:788469773599113247>", value="`usage`, `ping`, `dm`, `guilds`", inline=False)
    #   embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms", icon_url=ctx.author.avatar_url)
    #   await ctx.send(embed=embed)

    # @staticmethod
    # @asyncexe()
    # def commits_():
    #     repo = g.get_repo(
    #         "Cryptex-github/the-anime-bot-bot").get_commits()
    #     lists = [
    #         f"[`{i.commit.sha[:7]}`]({i.commit.html_url}) {i.commit.message}"
    #         for i in repo
    #     ]

    #     paginator = commands.Paginator(prefix="", suffix="", max_size=1000)
    #     for i in lists:
    #         paginator.add_line(i)
    #     return paginator

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    async def commits(self, ctx):
        await ctx.send("Getting commits")
        async with self.bot.session.get(
            "https://api.github.com/repos/Cryptex-github/the-anime-bot-bot/commits",
            headers={"Authorization": "token " + gittoken},
        ) as resp:
            repo = await resp.json()
        lists = [
            f"[`{i.get('sha')[:7]}`]({i.get('html_url')}) {i.get('commit').get('message')}"
            for i in repo
        ]

        paginator = commands.Paginator(prefix="", suffix="", max_size=1000)
        for i in lists:
            paginator.add_line(i)
        interface = PaginatorEmbedInterface(
            ctx.bot, paginator, owner=ctx.author
        )
        await interface.send_to(ctx)

    @commands.command(aliases=["info"])
    async def about(self, ctx):
        p = pathlib.Path("./cogs")
        cm = cr = fn = cl = ls = fc = cc = 0
        for f in p.rglob("*.py"):
            if str(f).startswith("venv"):
                continue
            fc += 1
            with f.open() as of:
                for l in of.readlines():
                    l = l.strip()
                    cc += len(l)
                    if l.startswith("class"):
                        cl += 1
                    if l.startswith("def"):
                        fn += 1
                    if l.startswith("async def"):
                        cr += 1
                    if "#" in l:
                        cm += 1
                    ls += 1
        m = self.bot.psutil_process.memory_full_info()
        start = time.perf_counter()
        await ctx.trigger_typing()
        end = time.perf_counter()
        final_latency = end - start
        owner = await self.bot.application_info()
        owner = owner.owner
        embed = await embedbase.embed(self, ctx)
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        embed.add_field(
            name="Info",
            value=f"Guilds: {len(self.bot.guilds)} \nMembers: {len(self.bot.users)} \nCreator: {owner} \nLibrary: discord.py \nCommands used (since last reboot): {self.bot.counter} \nInvite link: [click here](https://discord.com/api/oauth2/authorize?client_id=787927476177076234&permissions=2146823543&scope=bot) \nMessages Cached: {len(self.bot.cached_messages)}",
            inline=False,
        )
        embed.add_field(
            name="System Info",
            value=f"> `{humanize.naturalsize(m.rss)}` physical memory used\n> `{self.bot.psutil_process.cpu_percent()/psutil.cpu_count()}%` CPU usage\n> running on PID `{self.bot.psutil_process.pid}`\n> `{self.bot.psutil_process.num_threads()}` thread(s)",
            inline=False,
        )
        embed.add_field(
            name="<:stab:744345955637395586>  Websocket Latency",
            value=f"```{round(self.bot.latency * 1000)} ms ```",
        )
        embed.add_field(
            name="<a:typing:597589448607399949> API Latency",
            value=f"```{round(final_latency * 1000)} ms ```",
        )
        # repo = g.get_repo("Cryptex-github/the-anime-bot-bot").get_commits()[:3]
        # lists = []
        # for i in repo:
        #     lists.append(
        #         f"[{i.commit.sha[:7]}]({i.commit.html_url}) {i.commit.message}")
        # embed.add_field(name="Recent changes",
        #                 value="\n".join(lists), inline=False)
        embed.add_field(
            name=" stats ",
            value=f"```file: {fc:,}\nline: {ls:,}\ncharacters: {cc:,} \nclass: {cl:,}\nfunction: {fn:,}\ncoroutine: {cr:,}\ncomment: {cm:,}```",
            inline=False,
        )
        embed.set_footer(
            text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
            icon_url=ctx.author.avatar_url,
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def privacya(self, ctx):
        await ctx.message.add_reaction("<:mochaok:788473006606254080>")
        policy = "[Our Privacy Policy](https://cryptex-github.github.io/the-anime-bot-bot/privacy)"
        embed = await embedbase.embed(self, ctx)
        embed.add_field(name="policy", value=policy)
        embed.set_footer(
            text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
            icon_url=ctx.author.avatar_url,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        await ctx.trigger_typing()
        current_time = time.time()
        difference = current_time - self.bot.start_time
        text = humanize.precisedelta(datetime.timedelta(seconds=difference))
        embed = await embedbase.embed(self, ctx)
        embed.add_field(name="uptime ", value=text)
        await ctx.reply(embed=embed)

    @commands.command()
    async def countdown(self, ctx: AnimeContext, count_to: int):
        if str(ctx.channel.id) in self.countdownused:
            await ctx.send("this channel already have a countdown started")
            return
        else:
            self.countdownused.append(str(ctx.channel.id))
            counter = count_to
            message = await ctx.reply(
                f"start counting down to {counter} will dm you when is done"
            )
            for _ in range(counter):
                counter -= 1
                await asyncio.sleep(1)
                if counter == 0:
                    await message.edit(content=str(counter))
                    await ctx.author.send("Countdown finshed")
                    self.countdownused.remove(str(ctx.channel.id))
                    return


def setup(bot):
    bot.add_cog(others(bot))
