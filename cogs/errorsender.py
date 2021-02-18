import discord
from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
import aiohttp


class ErrorSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if not ctx.guild:
            server = "DM "
        else:
            server = "Server"
        if not ctx.guild:
            name = ctx.author
        else:
            name = ctx.guild.name
        fields = [
            ["Error", error],
            ["Author", ctx.author],
            [server, name],
            ["Message", ctx.message.content]
        ]
        embed = discord.Embed(color=0xFF0000, title="An error occured")
        [embed.add_field(name=f"**{n}**", value=f"```py\n{v}```", inline=False) for n, v in fields]
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(wha, adapter=AsyncWebhookAdapter(session))
            await webhook.send(embed=embed)
            return


def setup(bot):
    bot.add_cog(ErrorSender(bot))
