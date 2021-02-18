from discord.ext import commands


# import ipc


class IpcRoutes(commands.Cog):
    pass
    # def __init__(self, bot):
    #     self.bot = bot

    # @ipc.server.route()
    # async def get_guild_count(self):
    #   return len(self.bot.guilds)
    # @ipc.server.route()
    # async def get_member_count(self):
    #     return len(self.bot.users)


def setup(bot):
    bot.add_cog(IpcRoutes(bot))
