import discord
from discord.ext import commands


class logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        pass


def setup(bot):
    bot.add_cog(logger(bot))
