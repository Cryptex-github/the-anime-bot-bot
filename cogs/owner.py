import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from utils.asyncstuff import asyncexe
from selenium import webdriver
import aiohttp
from jishaku.exception_handling import ReplResponseReactor
from jishaku.features.baseclass import Feature
from jishaku.paginators import WrappedPaginator
from jishaku.shell import ShellReader
import subprocess
from contextlib import redirect_stdout
import traceback
import io
import textwrap
import os
from utils.embed import EmbedBase
from utils.asyncstuff import asyncexe
from menus import menus
import random
import zipfile
from jishaku.paginators import PaginatorInterface
from io import BytesIO
from PIL import Image
import asyncio


class MyMenu(menus.Menu, timeout=9223372036854775807):
    async def send_initial_message(self, ctx, channel):
        self.counter = 0
        return await channel.send(f"Hello {ctx.author}")

    @menus.button("<:rooPopcorn:744346001304977488>")
    async def on_thumbs_up(self, payload):
        self.counter += 1
        await self.message.edit(content=f"{self.counter}")


class owners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    # self.reactionreload.start()

    # @commands.Cog.listener()
    # async def on_ready(self):
    #   task = asyncio.create_task(self.reactionreload())
    @classmethod
    def check(self, payload):
        return payload.user_id == 590323594744168494 and payload.emoji.name == "\{NBLACK UNIVERSAL RECYCLING SYMBOL}"

    @tasks.loop(minutes=1)
    async def reactionreload(self):
        while True:
            payload = await self.bot.wait_for("raw_reaction_add", check=self.check)
            channel = self.bot.get_channel(payload.channel_id)
            embed = discord.Embed(color=0x00ff6a, description=f"<a:loading:747680523459231834>")
            message = await channel.send(embed=embed)
            list_ = []
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    try:
                        self.bot.reload_extension(f"cogs.{file[:-3]}")
                        self.list.append(file[:-3])
                    except Exception as e:
                        embed = discord.Embed(color=0xFF0000, description=f"Error while reloading cogs \n {e}")
                        return await message.edit(embed=embed)
            text = "\n <:greenTick:596576670815879169>".join(list_)
            embed = discord.Embed(color=0x00ff6a,
                                  description=f"Reloaded All Cogs \n <:greenTick:596576670815879169> {text}")
            await message.edit(embed=embed)

    @staticmethod
    async def eval_(self, ctx, txt):
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "asyncio": asyncio
        }

        env.update(globals())

        body = self.cleanup_code(txt)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            result = exec(to_compile, env)
            await ctx.send(f"```py\n{result}\n```")
        except Exception as e:
            return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except:
                pass

            if ret is None:
                if value:
                    # await ctx.send(f"```py\n{value}\n```")
                    pass
                else:
                    self._last_result = ret
                    await ctx.send(f"```py\n{value}{ret}\n```")

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
    # async def takepic(self, ctx, *, website):
    #   await ctx.send(file=await self.takepic_(website))
    @commands.command()
    @commands.is_owner()
    async def rubroke(self, ctx):
        await ctx.send("no")

    @commands.command()
    async def takepic(self, ctx, *, website: str):
        """
        Disclaimer: even we already have nsfw check in sfw channel but we don't guarantee that is completely safe if anyone ever used the bot to screenshot nsfw website in sfw channel. We have 0 responsibility to that
        """
        website = website.replace("<", "").replace(">", "")
        if not website.startswith("http"):
            return await ctx.send("not a valid website")
        async with aiohttp.ClientSession(headers={'User-Agent': 'python-requests/2.20.0'},
                                         timeout=aiohttp.ClientTimeout(total=20)).get(website) as resp:
            if resp.status != 200:
                return await ctx.send("can not screenshot that website")
            soup = BeautifulSoup(await resp.text(), features="lxml")
            canonical = soup.find('link', {'rel': 'canonical'})
            if canonical == None:
                website_ = str(resp.real_url)
            else:
                website_ = str(canonical['href'])
        if ctx.channel.nsfw == False:
            lists = ["dick", "pussy", "horny", "porn", "cum", "cunt", "cock", "penis", "hole", "fuck", "shit", "bitch",
                     "gore", "nsfw"]
            if any(i in website_ for i in lists):
                return await ctx.send("Can not search nsfw words in non nsfw channel")
        lists2 = ["ip", "i+p", "ipv4", "ipv6"]
        if any(i in website_ for i in lists2):
            return await ctx.send("can not screenshot that website")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)).get(
                f"https://image.thum.io/get/png/{website}") as resp:
            pic = BytesIO(await resp.read())
        await ctx.send(file=discord.File(pic, f"website_{website}.png"))

    @commands.command()
    @commands.is_owner()
    async def enable(self, ctx, *, command):
        self.bot.get_command(command).enabled = True
        await ctx.send(f"Enabled {command}")

    @commands.command()
    @commands.is_owner()
    async def disable(self, ctx, *, command):
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
        lines.append(f"Total amount of messages cached {len(self.bot.cached_messages)}")
        for i in lines:
            i = str(i)
            paginator.add_line(i)
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)

    @commands.command()
    @commands.is_owner()
    async def speedtest(self, ctx):
        async with ReplResponseReactor(ctx.message):
            with ShellReader("speedtest-cli") as reader:
                prefix = "```" + reader.highlight

                paginator = WrappedPaginator(prefix=prefix, max_size=1975)
                paginator.add_line(f"{reader.ps1} 'speedtest-cli'\n")

                interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
                self.bot.loop.create_task(interface.send_to(ctx))

                async for line in reader:
                    if interface.closed:
                        return
                    await interface.add_line(line)

            await interface.add_line(f"\n[status] Return code {reader.close_code}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, text_):
        text_ = text_.lower()
        await ctx.message.add_reaction("<:greenTick:596576670815879169>")
        embed = discord.Embed(color=0x00ff6a, description=f"<a:loading:747680523459231834>")
        message = await ctx.reply(embed=embed)
        self.list = []
        if text_ == "all":
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    try:
                        self.bot.reload_extension(f"cogs.{file[:-3]}")
                        self.list.append(file[:-3])
                    except Exception as e:
                        embed = discord.Embed(color=0xFF0000, description=f"Error while reloading cogs \n {e}")
                        return await message.edit(embed=embed)
            text = "\n <:greenTick:596576670815879169>".join(self.list)
            embed = discord.Embed(color=0x00ff6a,
                                  description=f"Reloaded All Cogs \n <:greenTick:596576670815879169> {text}")
            await message.edit(embed=embed)
        else:
            for file in os.listdir("./cogs"):
                if file.startswith(f"{text_}.py"):
                    self.bot.reload_extension(f"cogs.{file[:-3]}")
                    embed = discord.Embed(color=0x00ff6a,
                                          description=f" <:greenTick:596576670815879169> Reloaded {file[:-3]}")
                    await message.edit(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, text_):
        if text_ == "all":
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    self.bot.unload_extension(f"cogs.{file[:-3]}")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, text_):
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
    async def clear(self, ctx, number: int):
        counter = 0
        async for message in ctx.channel.history(limit=1000):
            if message.author.id == ctx.bot.user.id:
                await message.delete()
                counter += 1
                if counter >= number:
                    break
        await ctx.send(f"cleared {counter} messages")

    @commands.command()
    @commands.is_owner()
    async def delete_id(self, ctx, *, id: int):
        await ctx.channel.get_partial_message(id).delete()

    @commands.command()
    # @commands.is_owner()
    async def say(self, ctx, *, text: str):
        # if ctx.author.id == 707250997407252531 or ctx.author.id == 590323594744168494:
        await ctx.send(text, allowed_mentions=discord.AllowedMentions.none())

    @commands.command()
    @commands.is_owner()
    async def change(self, ctx, *, status: str):
        await self.bot.change_presence(activity=discord.Game(name=status))


@commands.command()
@commands.is_owner()
async def ping_user(self, ctx, *, member: discord.Member):
    await ctx.send(f"{member.mention}")


@commands.command()
@commands.is_owner()
async def rate_limited(self, ctx):
    await ctx.trigger_typing()
    await ctx.reply(f"{self.bot.is_ws_ratelimited()}")


@commands.command()
@commands.has_permissions(manage_messages=True)
async def purge(self, ctx, limit: int):
    await ctx.trigger_typing()
    counts = await ctx.channel.purge(limit=limit)
    await ctx.reply(content=f" purged {len(counts)} messages", delete_after=10)

    @commands.command()
    @commands.is_owner()
    async def ping_user(self, ctx, *, member: discord.Member):
        await ctx.send(f"{member.mention}")

    @commands.command()
    @commands.is_owner()
    async def rate_limited(self, ctx):
        await ctx.trigger_typing()
        await ctx.reply(f"{self.bot.is_ws_ratelimited()}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int):
        await ctx.trigger_typing()
        counts = await ctx.channel.purge(limit=limit)
        await ctx.reply(content=f" purged {len(counts)} messages", delete_after=10)


def setup(bot):
    bot.add_cog(owners(bot))
