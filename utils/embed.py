import discord
from datetime import datetime


class EmbedBase:
    async def embed(self, ctx):
        embed = discord.Embed(color=0x2ecc71, timestamp=datetime.utcnow())
        embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
                         icon_url=ctx.author.avatar_url)
        return embed
