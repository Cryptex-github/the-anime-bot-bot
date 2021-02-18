import json
from io import BytesIO

import aiohttp
import discord
import requests
from discord.ext import commands


class Animes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def searchanime(self, ctx, *, search):
        async with aiohttp.ClientSession().get(f"https://crunchy-bot.live/api/anime/details?terms={search}") as resp:
            print(await resp.json())  # uhhh what

    @commands.command()
    async def weebpicture(self, ctx):
        async with aiohttp.ClientSession().get("https://neko.weeb.services/") as resp:
            buffer = BytesIO(await resp.read())
            await ctx.send(file=discord.File(fp=buffer, filename="anime.png"))

    @commands.command()
    async def animememes(self, ctx):
        """
    Anime memes from reddit
    """
        await ctx.trigger_typing()
        async with aiohttp.ClientSession().get("https://meme-api.herokuapp.com/gimme/Animemes") as resp:
            meme = await resp.text()
            meme = json.loads(meme)
            if meme["nsfw"]:
                return True
            else:
                link = meme["postLink"]
                title = meme["title"]
                nsfw = meme["nsfw"]
                image = meme["preview"][-1]
        if nsfw:
            return
        embed = discord.Embed(color=0x2ecc71)
        embed.set_author(name=title, url=link)
        embed.set_image(url=image)
        embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
                         icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["animequotes"], brief=" new new anime quote from the web ")
    async def animequote(self, ctx):
        await ctx.trigger_typing()
        animejson = requests.get("https://animechanapi.xyz/api/quotes/random")
        anime = json.loads(animejson.text)
        animeta = anime["data"]
        animetosend = animeta[0]["quote"] + " By " + animeta[0][
            "character"] + " in " + animeta[0]["anime"]
        embed = discord.Embed(color=0x2ecc71)
        embed.set_author(name="New anime quote from the web")
        embed.add_field(name="quote", value=animetosend)
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Animes(bot))
