import discord
from discord.ext import commands, tasks
from contextlib import suppress
import aiohttp


class web(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.func.start(bot)

    @tasks.loop(minutes=1)
    async def func(self, bot):
        try:
            async with aiohttp.ClientSession().get("https://api.botlist.space/v1/bots") as resp:
                bot.botlist = await resp.text()
        except:
            pass


def setup(bot):
    bot.add_cog(web(bot))
