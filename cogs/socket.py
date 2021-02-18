import discord
from discord.ext import commands
from jishaku.paginators import PaginatorInterface
from collections import Counter
import time


class socket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.codes = {
            1: "HEARTBEAT",
            2: "IDENTIFY",
            3: "PRESENCE",
            4: "VOICE_STATE",
            5: "VOICE_PING",
            6: "RESUME",
            7: "RECONNECT",
            8: "REQUEST_MEMBERS",
            9: "INVALIDATE_SESSION",
            10: "HELLO",
            11: "HEARTBEAT_ACK",
            12: "GUILD_SYNC"
        }

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        self.bot.socket_stats["COMMAND_ERROR"] += 1

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        self.bot.socket_receive += 1
        if msg.get("op") != 0:
            self.bot.socket_stats[self.bot.codes[msg.get("op")]] += 1
        else:
            self.bot.socket_stats[msg.get('t')] += 1

    @commands.command()
    async def socket(self, ctx):
        """
        Status of socket
        """
        current_time = time.time()
        lists = []
        difference = int(current_time - self.bot.start_time) / 60
        lists.append(f"Received {self.bot.socket_receive} {self.bot.socket_receive // difference} per minute")
        for i, (n, v) in enumerate(self.bot.socket_stats.most_common()):
            lists.append(f"{n:<30} {v:<15} {round(v / difference, 3)} /minute")
        paginator = commands.Paginator(max_size=500, prefix="```", suffix="```")
        for i in lists:
            paginator.add_line(i)
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        return await interface.send_to(ctx)


def setup(bot):
    bot.add_cog(socket(bot))
