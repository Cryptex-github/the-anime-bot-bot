from discord.ext import commands
from jishaku.paginators import PaginatorInterface


class CommandsUsage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.bot.command_counter += 1
        self.bot.commandsusages[ctx.command.qualified_name] += 1

    @commands.command()
    async def commandsusage(self, ctx):
        lists = [f"Total {self.bot.command_counter} commands invoked"]
        for i, (n, v) in enumerate(self.bot.commandsusages.most_common()):
            lists.append(f"{n:<30} {v:<15}")
        if len(str(lists)) > 1800:
            paginator = commands.Paginator(max_size=1800, prefix="```", suffix="```")
            for i in lists:
                paginator.add_line(i)
            interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
            return await interface.send_to(ctx)
        else:
            lists = "\n".join(lists)
            await ctx.send(f"```\n{lists}\n```")


def setup(bot):
    bot.add_cog(CommandsUsage(bot))
