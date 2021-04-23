import asyncio
import typing
import io
import os
import random
import asyncpg
import subprocess
import textwrap
import traceback
from utils.subclasses import AnimeContext
import zipfile
from contextlib import redirect_stdout
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import collections
import contextlib
import import_expression
import inspect
import asyncio
import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from menus import menus
from PIL import Image
from selenium import webdriver
from utils.asyncstuff import asyncexe
from utils.embed import embedbase

from jishaku.exception_handling import ReactionProcedureTimer
from jishaku.paginators import PaginatorInterface, WrappedPaginator
from jishaku.shell import ShellReader


class MyMenu(menus.Menu, timeout=9223372036854775807):
    async def send_initial_message(self, ctx: AnimeContext, channel):
        self.counter = 0
        return await channel.send(f"Hello {ctx.author}")

    @menus.button("<:rooPopcorn:744346001304977488>")
    async def on_thumbs_up(self, payload):
        self.counter += 1
        await self.message.edit(content=f"{self.counter}")


class owners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.author.id not in self.bot.owner_ids:
            raise commands.NotOwner
        else:
            return True

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if (
            payload.user_id == 590323594744168494
            and payload.emoji.name == "\U0001f6ae"
        ):
            try:
                await self.bot.http.delete_message(
                    payload.channel_id,
                    payload.message_id,
                    reason="delete reaction detected",
                )
            except:
                pass

    @commands.command()
    async def viewlog(self, ctx):
        proc = await asyncio.create_subprocess_shell(
            "systemctl status animebot",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            await ctx.send(
                f'```py\n{stdout.decode().replace("jadonvps", "secrect")}\n```'
            )
        if stderr:
            await ctx.send(
                f'```py\n{stderr.decode().replace("jadonvps", "secrect")}\n```'
            )

    @commands.command(aliases=["sync"])
    @commands.is_owner()
    async def pull(self, ctx):
        proc = await asyncio.create_subprocess_shell(
            "git pull",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        stdout = f"{stdout.decode()}" if stdout != b"" else ""
        stderr = f"\n{stderr.decode()}" if stderr != b"" else ""
        return await ctx.send(
            embed=discord.Embed(
                color=self.bot.color,
                title="Pulling from GitHub...",
                description=f"```\n{stdout}\n{stderr}\n```",
            )
        )

    @classmethod
    def check(self, payload):
        return (
            payload.user_id == 590323594744168494
            and payload.emoji.name == "\{NBLACK UNIVERSAL RECYCLING SYMBOL}"
        )

    @commands.command(aliases=["exe"])
    @commands.is_owner()
    async def execute(self, ctx, *, code):
        if not code.startswith("`"):
            code = code
        else:
            last = collections.deque(maxlen=3)
            backticks = 0
            in_language = False
            in_code = False
            language = []
            code_ = []

            for char in code:
                if char == "`" and not in_code and not in_language:
                    backticks += 1
                if (
                    last
                    and last[-1] == "`"
                    and char != "`"
                    or in_code
                    and "".join(last) != "`" * backticks
                ):
                    in_code = True
                    code_.append(char)
                if char == "\n":
                    in_language = False
                    in_code = True
                elif "".join(last) == "`" * 3 and char != "`":
                    in_language = True
                    language.append(char)
                elif in_language:
                    language.append(char)

                last.append(char)

            if not code_ and not language:
                code_[:] = last
            code = "".join(code_[len(language) : -backticks])
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "discord": discord,
            "commands": commands,
            "message": ctx.message,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "author": ctx.author,
            "inspect": inspect,
            "asyncio": asyncio,
            "aiohttp": aiohttp,
        }
        env.update(globals())
        to_execute = f"async def execute():\n{textwrap.indent(code, '  ')}"
        async with ReactionProcedureTimer(ctx.message, self.bot.loop):
            try:
                import_expression.exec(to_execute, env)
            except Exception as e:
                return await ctx.send(e)
            to_execute = env["execute"]
            f = io.StringIO()
            try:
                with contextlib.redirect_stdout(f):
                    if inspect.isasyncgenfunction(to_execute):
                        async for i in to_execute():
                            await ctx.send(i)
                        await ctx.send(f.getvalue()) if f.getvalue() else ...
                        return
                    result = await to_execute()
            except Exception as e:
                return (
                    await ctx.send(
                        f"```py\n{f.getvalue()}\n{traceback.format_exc()}\n```"
                    )
                    if len(
                        f"```py\n{f.getvalue()}\n{traceback.format_exc()}\n```"
                    )
                    <= 2000
                    else await ctx.send(
                        await ctx.paste(
                            f"```py\n{f.getvalue()}\n{traceback.format_exc()}\n```"
                        )
                    )
                )
            if result == " " and not f.getvalue():
                return await ctx.send("\u200b")
            result = result or ""
            if result or f.getvalue():
                await ctx.send(f"{f.getvalue()}\n{result}") if len(
                    f"{f.getvalue()}\n{result}"
                ) <= 2000 else await ctx.send(
                    await ctx.paste(f"{f.getvalue()}\n{result}")
                )

    # @staticmethod
    # @asyncexe()
    # def takepic_(website):
    #   browser = webdriver.Chrome("/home/runner/kageyama-bot/chromedriver")
    #   browser.get(website)
    #   file = discord.File(fp=BytesIO(browser.get_screenshot_as_file("website.png")), filename="takepic.png")
    #   browser.quit()
    #   return file

    # @commands.command()
    # @commands.is_owner()
    # async def takepic(self, ctx: AnimeContext, *, website):
    #   await ctx.send(file=await self.takepic_(website))
    @staticmethod
    @asyncexe()
    def zip_emojis(emojis):
        file_ = BytesIO()
        with zipfile.ZipFile(
            file_, mode="w", compression=zipfile.ZIP_BZIP2, compresslevel=9
        ) as zipfile_:
            for n, v in emojis:
                zipfile_.writestr(n, v.getvalue())
        file_.seek(0)
        return discord.File(file_, "emojis.zip")

    @commands.command()
    @commands.is_owner()
    async def zipallemoji(self, ctx):
        emojis = []
        for i in ctx.bot.emojis:
            e = await i.url_as().read()
            e = (
                f"{i.name}.png" if not i.animated else f"{i.name}.gif",
                BytesIO(e),
            )
            emojis.append(e)
        await ctx.send(file=await self.zip_emojis(emojis))

    @commands.command()
    @commands.is_owner()
    async def rubroke(self, ctx):
        await ctx.send("no")

    @commands.command()
    @commands.is_nsfw()
    async def takepic(self, ctx: AnimeContext, *, website: str):
        """
        take picture of website
        """
        website = website.replace("<", "").replace(">", "")
        if not website.startswith("http"):
            return await ctx.send("not a valid website")
        async with self.bot.session.get(
            f"https://image.thum.io/get/png/{website}"
        ) as resp:
            pic = BytesIO(await resp.read())
        await ctx.send(
            file=discord.File(pic, f"website_screemshot_{website}.png")
        )

    @commands.command()
    @commands.is_owner()
    async def enable(self, ctx: AnimeContext, *, command):
        self.bot.get_command(command).enabled = True
        await ctx.send(f"Enabled {command}")

    @commands.command()
    @commands.is_owner()
    async def disable(self, ctx: AnimeContext, *, command):
        self.bot.get_command(command).enabled = False
        await ctx.send(f"Disabled {command}")

    @commands.command()
    @commands.is_owner()
    async def cache(self, ctx):
        """
        tell you how many messages the bot have cached if you don't know what is cache then this is not the right command for you
        """
        paginator = commands.Paginator(max_size=1000)
        lines = list(self.bot.cached_messages)
        lines.append(
            f"Total amount of messages cached {len(self.bot.cached_messages)}"
        )
        for i in lines:
            i = str(i)
            paginator.add_line(i)
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)

    @commands.command()
    @commands.is_owner()
    async def speedtest(self, ctx):
        async with ReplResponseReactor(ctx.message):
            with ShellReader("speedtest-cli --simple") as reader:
                prefix = "```" + reader.highlight

                paginator = WrappedPaginator(prefix=prefix, max_size=1975)
                paginator.add_line(f"{reader.ps1} 'speedtest-cli --simple'\n")

                interface = PaginatorInterface(
                    ctx.bot, paginator, owner=ctx.author
                )
                self.bot.loop.create_task(interface.send_to(ctx))

                async for line in reader:
                    if interface.closed:
                        return
                    await interface.add_line(line)

            await interface.add_line(
                f"\n[status] Return code {reader.close_code}"
            )

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: AnimeContext, text_):
        text_ = text_.lower()
        await ctx.message.add_reaction("<:greenTick:596576670815879169>")
        embed = discord.Embed(
            color=0x00FF6A, description=f"<a:loading:747680523459231834>"
        )
        message = await ctx.reply(embed=embed)
        self.list = []
        if text_ == "all":
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    try:
                        self.bot.reload_extension(f"cogs.{file[:-3]}")
                        self.list.append(file[:-3])
                    except Exception as e:
                        embed = discord.Embed(
                            color=0xFF0000,
                            description=f"Error while reloading cogs \n {e}",
                        )
                        return await message.edit(embed=embed)
            text = "\n <:greenTick:596576670815879169>".join(self.list)
            embed = discord.Embed(
                color=0x00FF6A,
                description=f"Reloaded All Cogs \n <:greenTick:596576670815879169> {text}",
            )
            await message.edit(embed=embed)
        else:
            for file in os.listdir("./cogs"):
                if file.startswith(f"{text_}.py"):
                    self.bot.reload_extension(f"cogs.{file[:-3]}")
                    embed = discord.Embed(
                        color=0x00FF6A,
                        description=f" <:greenTick:596576670815879169> Reloaded {file[:-3]}",
                    )
                    await message.edit(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: AnimeContext, text_):
        if text_ == "all":
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    self.bot.unload_extension(f"cogs.{file[:-3]}")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: AnimeContext, text_):
        if text_ == "all":
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    self.bot.load_extension(f"cogs.{file[:-3]}")

    @commands.command()
    @commands.is_owner()
    async def menus(self, ctx):
        m = MyMenu()
        await m.start(ctx)

    @commands.command()
    @commands.is_owner()
    async def clear(self, ctx: AnimeContext, number: int):
        counter = 0
        async for message in ctx.channel.history(limit=100):
            if message.author.id == ctx.bot.user.id:
                await message.delete()
                counter += 1
            if counter >= number:
                break
        await ctx.send(f"cleared {number} messages")

    @commands.command(aliases=["del"])
    @commands.is_owner()
    async def delete_id(self, ctx: AnimeContext, *, id: int = None):
        if ctx.message.reference:
            id = ctx.message.reference.message_id
        try:
            await asyncio.wait_for(
                ctx.channel.get_partial_message(id).delete(), timeout=5
            )
        except asyncio.TimeoutError:
            try:
                await asyncio.wait_for(
                    self.bot.http.delete_message(ctx.channel.id, id), timeout=5
                )
            except asyncio.TimeoutError:
                await ctx.send(
                    "guess what retarded discord ratelimit me again"
                )

    @commands.command()
    # @commands.is_owner()
    async def say(self, ctx: AnimeContext, *, text: str):
        if ctx.channel.nsfw == False:
            lists = [
                "dick",
                "pussy",
                "horny",
                "porn",
                "cum",
                "cunt",
                "cock",
                "penis",
                "hole",
                "fuck",
                "shit",
                "bitch",
                "gore",
                "nsfw",
            ]
            if any(i in text for i in lists):
                return await ctx.send(
                    "Can not say nsfw words in non nsfw channel"
                )
        # if ctx.author.id == 707250997407252531 or ctx.author.id == 590323594744168494:
        text = (
            text.replace("|", "\u200b|")
            .replace("*", "\u200b*")
            .replace("`", "\u200b`")
            .replace("~", "\u200b~")
            .replace(">", ">\u200b")
            .replace("[", "\u200b[")
            .replace("]", "\u200b]")
            .replace("(", "\u200b(")
            .replace(")", "\u200b)")
        )
        embed = discord.Embed(
            color=self.bot.color, description=f"**said:** {str(text)}"
        )
        embed.set_author(
            name=ctx.author.display_name, icon_url=str(ctx.author.avatar_url)
        )
        await ctx.send(
            embed=embed, allowed_mentions=discord.AllowedMentions.none()
        )

    @commands.command()
    @commands.is_owner()
    async def change(self, ctx: AnimeContext, *, status: str):
        await self.bot.change_presence(activity=discord.Game(name=status))

    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx: AnimeContext, *, query: str):
        """Run some SQL."""
        # the imports are here because I imagine some people would want to use
        # this cog as a base for their other cog, and since this one is kinda
        # odd and unnecessary for most people, I will make it easy to remove
        # for those people.
        from utils.format import TabularData, plural
        import time

        query = self.cleanup_code(query)

        is_multistatement = query.count(";") > 1
        if is_multistatement:
            # fetch does not support multiple statements
            strategy = self.bot.db.execute
        else:
            strategy = self.bot.db.fetch

        try:
            start = time.perf_counter()
            results = await strategy(query)
            dt = (time.perf_counter() - start) * 1000.0
        except Exception:
            return await ctx.send(f"```py\n{traceback.format_exc()}\n```")

        rows = len(results)
        if is_multistatement or rows == 0:
            return await ctx.send(f"`{dt:.2f}ms: {results}`")

        headers = list(results[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in results)
        render = table.render()

        fmt = (
            f"```\n{render}\n```\n*Returned {plural(rows):row} in {dt:.2f}ms*"
        )
        if len(fmt) > 2000:
            return await ctx.send(await ctx.paste(fmt))
        else:
            await ctx.send(fmt)


@commands.command()
@commands.is_owner()
async def ping_user(self, ctx: AnimeContext, *, member: discord.Member):
    await ctx.send(f"{member.mention}")


@commands.command()
@commands.is_owner()
async def rate_limited(self, ctx):
    await ctx.trigger_typing()
    await ctx.reply(f"{self.bot.is_ws_ratelimited()}")


@commands.command()
@commands.has_permissions(manage_messages=True)
async def purge(self, ctx: AnimeContext, limit: int):
    await ctx.trigger_typing()
    counts = await ctx.channel.purge(limit=limit)
    await ctx.reply(content=f" purged {len(counts)} messages", delete_after=10)

    @commands.command()
    @commands.is_owner()
    async def ping_user(self, ctx: AnimeContext, *, member: discord.Member):
        await ctx.send(f"{member.mention}")

    @commands.command()
    @commands.is_owner()
    async def rate_limited(self, ctx):
        await ctx.trigger_typing()
        await ctx.reply(f"{self.bot.is_ws_ratelimited()}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: AnimeContext, limit: int):
        await ctx.trigger_typing()
        counts = await ctx.channel.purge(limit=limit)
        await ctx.reply(
            content=f" purged {len(counts)} messages", delete_after=10
        )


def setup(bot):
    bot.add_cog(owners(bot))
