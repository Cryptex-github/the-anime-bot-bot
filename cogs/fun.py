import discord
from discord.ext import commands
import typing
import async_timeout
from io import BytesIO
import aiohttp
import os
from PIL import Image
import textwrap
from PIL import ImageFont
from PIL import ImageDraw

talk_token = os.getenv("talk_token")
rapid_api_key = os.getenv("rapid_api_key")
tenor_API_key = os.getenv("tenor_API_key")
from utils.asyncstuff import asyncexe
from bottom import to_bottom
from bottom import from_bottom
import asyncio
import time
import gtts
import json
import re
from menus import menus
from utils.paginator import AnimePages
from cryptography.fernet import Fernet
import random
from asyncdagpi import Client
from utils.embed import EmbedBase


class gifs():
    async def tenor(self, search):
        tenor_ = []
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                    f"https://api.tenor.com/v1/search?q={search}&key={tenor_API_key}&limit=50&contentfilter=low") as resp:
                text = await resp.text()
                text = json.loads(text)
                for i in text["results"]:
                    for x in i["media"]:
                        tenor_.append(x["gif"]["url"])
        return random.choice(tenor_)

    async def hug(self):
        self.gifs = []
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                    f"https://api.tenor.com/v1/search?q=animehug&key={tenor_API_key}&limit=50&contentfilter=low") as resp:
                text = await resp.text()
                text = json.loads(text)
                for i in text["results"]:
                    for x in i["media"]:
                        self.gifs.append(x["gif"]["url"])
        return random.choice(self.gifs)


class UrbanDictionaryPageSource(menus.ListPageSource):
    BRACKETED = re.compile(r'(\[(.+?)\])')

    def __init__(self, data):
        super().__init__(entries=data, per_page=1)

    def cleanup_definition(self, definition, *, regex=BRACKETED):
        def repl(m):
            word = m.group(2)
            return f'[{word}](http://{word.replace(" ", "-")}.urbanup.com)'

        ret = regex.sub(repl, definition)
        if len(ret) >= 2048:
            return ret[0:2000] + ' [...]'
        return ret

    def format_page(self, menu, entry):
        maximum = self.get_max_pages()
        title = f'{entry["word"]}: {menu.current_page + 1} / {maximum}' if maximum else entry['word']
        embed = discord.Embed(title=title, colour=0x00ff6a, url=entry['permalink'])
        embed.set_footer(text=f'By {entry["author"]}')
        embed.description = self.cleanup_definition(
            f"**Definition:**\n {entry['definition']}\n**Example:**\n{entry['example']}")

        try:
            up, down = entry['thumbs_up'], entry['thumbs_down']
        except KeyError:
            pass
        else:
            embed.add_field(name='Votes', value=f"Thumbs Up {up} Thumbs Down {down}", inline=False)

        try:
            date = discord.utils.parse_time(entry['written_on'][0:-1])
        except (ValueError, KeyError):
            pass
        else:
            embed.timestamp = date

        return embed


class functions(commands.Cog):
    async def get_quote(self):
        self.quotes = []
        async with aiohttp.ClientSession().get("https://type.fit/api/quotes") as resp:
            for i in json.loads(await resp.text()):
                self.quotes.append(i["text"])
        return random.choice(self.quotes)

    async def getmeme():
        async with aiohttp.ClientSession().get("https://meme-api.herokuapp.com/gimme") as resp:
            meme = await resp.text()
            meme = json.loads(meme)
            if meme["nsfw"] == True:
                return True
            else:
                link = meme["postLink"]
                title = meme["title"]
                nsfw = meme["nsfw"]
                image = meme["preview"][-1]
                return link, title, nsfw, image

    async def in_lb(user):
        with open("sushi.json", "r") as f:
            users = json.load(f)
            if str(user.id) in users:
                return True
            else:
                users[str(user.id)] = None
                with open("sushi.json", "w") as f:
                    json.dump(users, f)
                return False

    async def get_lb(user):
        with open("sushi.json", "r") as f:
            users = json.load(f)
            return users[str(user.id)]

    async def update_lb(user, score):
        with open("sushi.json", "r") as f:
            users = json.load(f)
        users[str(user.id)] = int(score)
        with open("sushi.json", "w") as f:
            json.dump(users, f)
            return True


class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.talk_channels = []

    @staticmethod
    async def reddit_(text):
        async with aiohttp.ClientSession().get(f"https://meme-api.herokuapp.com/gimme/{text}") as resp:
            meme = await resp.text()
            meme = json.loads(meme)
            if meme["nsfw"] == True:
                return True
            else:
                link = meme["postLink"]
                title = meme["title"]
                nsfw = meme["nsfw"]
                image = meme["preview"][-1]
                return link, title, nsfw, image

    @staticmethod
    def bottoms(mode, text):
        if mode == "to_bottom":
            return to_bottom(text)
        else:
            return from_bottom(text)

    @commands.command()
    async def http(self, ctx, *, code: str = "404"):
        async with aiohttp.ClientSession().get(f"https://http.cat/{code}") as resp:
            buffer = await resp.read()
        await ctx.send(file=discord.File(BytesIO(buffer), filename=f"{code}.png"))

    @commands.command()
    async def robtea(self, ctx):
        embed = discord.Embed(description="Click it in 10 seconds to get your tea in perfect tempature", color=0x00ff6a)
        message = await ctx.send(embed=embed)
        await message.add_reaction("\U0001f375")
        start = time.time()

        def check(payload):
            return payload.message_id == message.id and payload.emoji.name == "\U0001f375" and payload.user_id == ctx.author.id

        payload = await self.bot.wait_for("raw_reaction_add", check=check)
        end = time.time()
        embed = discord.Embed(description=f"You robbed the tea in {round(end - start, 3)} seconds", color=0x00ff6a)
        await message.edit(embed=embed)

    @commands.command(aliases=["balls"])
    async def ball(self, ctx, *, question):
        await ctx.send(self.bot.ball.response(question))

    # @commands.command()
    async def spamclick(self, ctx):
        counter = 0
        embed = discord.Embed(color=0x00ff6a,
                              description="Rules:\nafter the countdown end you will spam click the reaction as fast as you can")
        message = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        embed = discord.Embed(color=0x00ff6a, description="3")
        await message.edit(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(color=0x00ff6a, description="2")
        await message.edit(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(color=0x00ff6a, description="1")
        await message.edit(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(color=0x00ff6a, description="NOW")
        await message.edit(embed=embed)
        await message.add_reaction("<:stab:744345955637395586>")

        def check(payload):
            return payload.emoji.id == 744345955637395586 and payload.message_id == message.id

        async with async_timeout.timeout(10):
            while True:
                tasks = [
                    asyncio.ensure_future(self.bot.wait_for('raw_reaction_add', check=check)),
                    asyncio.ensure_future(self.bot.wait_for('raw_reaction_remove', check=check))
                ]
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                counter += 1
                for task in pending:
                    task.cancel()
        await ctx.send(f"You clicked {counter} times")

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    async def latest(self, ctx, user: discord.Member = None):
        async with ctx.typing():
            user1 = user
            if user1 == None:
                user1 = ctx.author
            async for message in ctx.channel.history(limit=10000):
                if message.author.id == user1.id:
                    msg = message
                    break
            embed = discord.Embed(color=0x00ff6a, timestamp=msg.created_at)
            embed.set_author(name=msg.author, icon_url=str(msg.author.avatar_url))
            embed.set_footer(text=f"id: {msg.id} Created at: ")
            if msg.embeds:
                content = "Embed"
            elif msg.attachments:
                content = "Attachment"
            else:
                content = msg.content
            embed.add_field(name="Content", value=content, inline=False)
            embed.add_field(name="Jump link", value=f"[url]({msg.jump_url})", inline=False)
            await ctx.send(embed=embed)
            if msg.attachments:
                await ctx.send(msg.attachments[0].url)
            if msg.embeds:
                await ctx.send(embed=msg.embeds[0])

    @commands.command(aliases=["rm"])
    @commands.max_concurrency(1, commands.BucketType.user)
    async def randommessage(self, ctx, limit=300):
        if limit > 10000:
            limit = 10000
        if limit <= 0:
            limit = 300
        async with ctx.typing():
            async for message in ctx.channel.history(limit=limit):
                # if user:
                #   lists = []
                #   counter = 0
                #   if message.author.id == user.id:
                #     lists.append(message)
                #     counter += 1
                #   if counter == 10:
                #     msg = random.choice(lists)
                #     break
                # else:
                if random.randint(0, 100) == 1:
                    msg = message
                    break
            # if user != None:
            #   lists = []
            #   for i in msg:
            #     if i.author.id == user.id:
            #       lists.append(i)
            # else:
            #   lists = msg
            # if lists == []:
            #   return await ctx.send(f"Can not find message that is send by {user}")
            # msg = random.choice(lists)
            embed = discord.Embed(color=0x00ff6a, timestamp=msg.created_at)
            embed.set_author(name=msg.author, icon_url=str(msg.author.avatar_url))
            embed.set_footer(text=f"id: {msg.id} Created at: ")
            if msg.embeds:
                content = "Embed"
            elif msg.attachments:
                content = "Attachment"
            else:
                content = msg.content
            embed.add_field(name="Content", value=content, inline=False)
            embed.add_field(name="Jump link", value=f"[url]({msg.jump_url})", inline=False)
            await ctx.send(embed=embed)
            if msg.attachments:
                await ctx.send(msg.attachments[0].url)
            if msg.embeds:
                await ctx.send(embed=msg.embeds[0])

    @commands.command()
    async def reddit(self, ctx, *, text):
        await ctx.trigger_typing()
        link, title, nsfw, image = await self.reddit_(text)
        if nsfw:
            return
        embed = discord.Embed(color=0x00ff6a)
        embed.set_author(name=title, url=link)
        embed.set_image(url=image)
        embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
                         icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command()
    async def bottomdecode(self, ctx, *, text):
        bottoms = await self.bot.loop.run_in_executor(None, self.bottoms, "from_bottom", text)
        if len(bottoms) > 500:
            return await ctx.send(str(await self.bot.mystbin.post(bottoms)))
        await ctx.send(bottoms)

    @commands.command()
    async def bottomencode(self, ctx, *, text):
        bottoms = await self.bot.loop.run_in_executor(None, self.bottoms, "to_bottom", text)
        if len(bottoms) > 500:
            return await ctx.send(str(await self.bot.mystbin.post(bottoms)))
        await ctx.send(bottoms)

    @staticmethod
    def render_emoji(text):
        text_ = text.replace("0", "\U00002b1b").replace("1", "\U00002b1c").replace("2", "\U0001f7e6").replace("3",
                                                                                                              "\U0001f7eb").replace(
            "4", "\U0001f7e9").replace("5", "\U0001f7e7").replace("6", "\U0001f7ea").replace("7", "\U0001f7e5").replace(
            "8", "\U0001f7e8").replace("9", "")
        return text_

    @commands.command(aliases=["grid", "toemoji"])
    async def renderemoji(self, ctx, *, codes):
        codes_ = await self.bot.loop.run_in_executor(None, self.render_emoji, codes)
        await ctx.reply(codes_)

    @commands.command()
    async def urban(self, ctx, *, search: str):
        if not ctx.channel.nsfw:
            lists = ["dick", "pussy", "horny", "porn", "cum", "cunt", "cock", "penis", "hole", "fuck", "shit", "bitch"]
            if any(i in search for i in lists):
                return await ctx.send("Can not search nsfw words in non nsfw channel")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"http://api.urbandictionary.com/v0/define?term={search}") as resp:
                if resp.status != 200:
                    return await ctx.send(f'An error occurred: {resp.status} {resp.reason}')
                js = await resp.json()
                data = js.get('list', [])
                if not data:
                    return await ctx.send('No results found, sorry.')

            pages = AnimePages(UrbanDictionaryPageSource(data))
            try:
                await pages.start(ctx)
            except menus.MenuError as e:
                await ctx.send(e)

    @commands.command(aliases=["chat"])
    @commands.max_concurrency(1, commands.cooldowns.BucketType.channel, wait=False)
    async def talk(self, ctx):
        """
        Chat with the bot you might stop by saying `end`
        """
        # for i in self.talk_channels:
        #   if i == ctx.message.channel.id:
        #     embed = discord.Embed(color=0x00ff6a, description="A chat session has already been established in this channel")
        #     return await ctx.reply(embed=embed)
        self.talk_channels.append(ctx.message.channel.id)
        embed = discord.Embed(color=0x00ff6a, description="A chat session has been established")
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and (3 <= len(m.content) <= 60)

        talking = True
        while talking:
            chats = ["Hii", "helooo"]
            try:
                message = await self.bot.wait_for("message", timeout=60, check=check)
                chats.append(message.content)
                if message.content == "end":
                    self.talk_channels.remove(ctx.message.channel.id)
                    embed = discord.Embed(color=0x00ff6a, description="Ended")
                    await ctx.reply(embed=embed)
                    talking = False
                    return False
                payload = {"text": message.content, "context": [chats[-2], chats[-1]]}
                async with ctx.channel.typing(), aiohttp.ClientSession().post("https://public-api.travitia.xyz/talk",
                                                                              json=payload, headers={
                            "authorization": talk_token}) as res:
                    await message.reply((await res.json())["response"])
            except asyncio.TimeoutError:
                self.talk_channels.remove(ctx.message.channel.id)
                embed = discord.Embed(color=0x00ff6a, description="Ended")
                await message.reply(embed=embed)
                talking = False
                return False

    @talk.error
    async def talk_error(self, ctx, error):
        if isinstance(error, commands.errors.MaxConcurrencyReached):
            embed = discord.Embed(color=0x00ff6a,
                                  description="A chat session has already been established in this channel")
            return await ctx.reply(embed=embed)

    @commands.command()
    async def sob(self, ctx, level: int = 1):
        if level > 70:
            embed = discord.Embed(color=0x00ff6a, description=f"The level must be 70 or lower then 70")
            return await ctx.send(embed=embed)
        emojis2 = []
        for i in range(level):
            emojis2.append("<:rooSob:744345453923139714>")
        emojis = " ".join(emojis2)
        embed = discord.Embed(color=0x00ff6a, description=f"{emojis}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["tr", "typerace"])
    async def typeracer(self, ctx):
        quote = await functions.get_quote(self)
        font = ImageFont.truetype("lexiereadable-bold.ttf", 16)
        img = Image.new("RGB", (400, 100), color="black")
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), '\n'.join(textwrap.wrap(quote, 46)), font=font)
        buffer = BytesIO()
        img.save(buffer, "png")
        file = discord.File(buffer, filename="quote.png")
        embed = await EmbedBase.embed(self, ctx)
        embed.set_image(url="attachment://quote.png")
        message = await ctx.reply(file=file, embed=embed)

        def check(m):
            return m.channel == ctx.message.channel and m.content == quote

        start = time.perf_counter()
        msg = await self.bot.wait_for("message", check=check)
        end = time.perf_counter()
        final_ = end - start
        final_ = round(final_)
        embed = await EmbedBase.embed(self, ctx)
        embed.set_author(name=f"{msg.author} got it in {final_} seconds")
        embed2 = await EmbedBase.embed(self, ctx)
        embed2.set_author(name=f"{msg.author} got it in {final_} seconds")
        embed2.set_image(url="attachment://quote.png")
        await message.edit(embed=embed2)
        await ctx.send(embed=embed)

    @commands.command()
    async def tenor(self, ctx, *, search):
        gif = await gifs.tenor(self, search)
        embed = await EmbedBase.embed(self, ctx)
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

    @commands.command(aliases=["sw", "speedwatch"])
    async def speedwatcher(self, ctx, member: discord.Member = None):
        member1 = member
        if member1 == None:
            member1 = ctx.author
        variable = random.randint(1, 2)
        variable2 = random.randint(0, 10)
        random.seed(member1.id)
        speed_ = random.random()
        speed = round(speed_ * 100)
        if variable == 1:
            speed = speed + variable2
        else:
            speed = speed - variable2
        if speed < 0:
            bar_ = "\u2800"
        elif speed <= 10:
            bar_ = "<:angery:747680299311300639>"
        elif speed <= 20:
            bar_ = "<:angery:747680299311300639><:angery:747680299311300639>"
        elif speed <= 30:
            bar_ = "<:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639>"
        elif speed <= 40:
            bar_ = "<:angery:747680299311300639> <:angery:747680299311300639> <:angery:747680299311300639> <:angery:747680299311300639>"
        elif speed <= 50:
            bar_ = "<:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639>"
        elif speed <= 60:
            bar_ = "<:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639>"
        elif speed <= 70:
            bar_ = "<:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639>"
        elif speed <= 80:
            bar_ = "<:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639>"
        elif speed <= 90:
            bar_ = "<:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639>"
        elif speed >= 100:
            bar_ = "<:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639><:angery:747680299311300639>"

        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name=f"{member1} is", value=f"`{speed}%` anime speedwatcher\n{bar_}")
        await ctx.send(embed=embed)

    @commands.command()
    async def hug(self, ctx, member: discord.Member = None):
        gif = await gifs.hug(self)
        member1 = member
        if member1 == None:
            member1 = "themself"
        embed = await EmbedBase.embed(self, ctx)
        embed.set_author(name=f"{ctx.author} just hugged {member1}")
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

    @commands.command()
    async def tts(self, ctx, *, text="enter something "):
        async with ctx.typing():
            t = gtts.gTTS(text=f"{text}")
            t.save("audio.mp3")
            await ctx.reply(file=discord.File("audio.mp3"))
            await asyncio.sleep(1)
            os.remove("audio.mp3")

    @commands.command()
    async def sushi(self, ctx):
        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name="Get the sushi", value="3")
        message = await ctx.send(embed=embed)
        await asyncio.sleep(1)
        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name="Get the sushi", value="2")
        await message.edit(embed=embed)
        await asyncio.sleep(1)
        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name="Get the sushi", value="1")
        await message.edit(embed=embed)
        await asyncio.sleep(1)
        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name="Get the sushi", value="**NOW**")
        await message.edit(embed=embed)
        await message.add_reaction("\U0001f363")
        start = time.perf_counter()

        def check(reaction, user):
            return reaction.message.id == message.id and user != self.bot.user and str(reaction.emoji) == "\U0001f363"

        reaction, user = await self.bot.wait_for('reaction_add', check=check)
        end = time.perf_counter()
        users = await reaction.users().flatten()
        for i in users:
            if i.bot == True:
                users.remove(i)
        lists = []
        for i in users:
            lists.append(str(i.name))
        # await functions.in_lb(user)
        # score = await functions.get_lb(user)
        final = end - start
        # final = int(final)
        # if final == None or final == "null":
        #   await functions.update_lb(user, final)
        #   embed = await EmbedBase.embed(self, ctx)
        #   embed.add_field(name="Get the sushi", value=f"**{user} got it in {round(final * 1000)} ms new person record**")
        #   await message.edit(embed=embed)
        #   return
        # if final < score:
        #   await functions.update_lb(user, final)
        #   embed = await EmbedBase.embed(self, ctx)
        #   embed.add_field(name="Get the sushi", value=f"**{user} got it in {round(final * 1000)} ms new person record**")
        #   await message.edit(embed=embed)
        #   return

        embed = await EmbedBase.embed(self, ctx)
        embed.add_field(name="Get the sushi", value=f"**{user.mention} got it in {round(final * 1000)} ms **",
                        inline=False)
        embed.add_field(name="participant", value="\n".join(lists), inline=False)
        await message.edit(embed=embed)

        def check(payload):
            return payload.message_id == message.id

        while True:
            payload = await self.bot.wait_for("raw_reaction_add", check=check)
            msg = await self.bot.get_message(payload.message_id)
            if not msg:
                break
            reactions = msg.reactions[0]
            users = await reactions.users().flatten()
            print(users)
            for i in users:
                if i.bot == True:
                    users.remove(i)
            lists = []
            for i in users:
                lists.append(str(i.name))
            embed = await EmbedBase.embed(self, ctx)
            embed.add_field(name="Get the sushi", value=f"**{user.mention} got it in {round(final * 1000)} ms **",
                            inline=False)
            embed.add_field(name="participant", value="\n".join(lists), inline=False)
            await message.edit(embed=embed)

    @commands.command()
    async def meme(self, ctx):
        await ctx.trigger_typing()
        link, title, nsfw, image = await functions.getmeme()
        if nsfw == True:
            return
        embed = discord.Embed(color=0x00ff6a)
        embed.set_author(name=title, url=link)
        embed.set_image(url=image)
        embed.set_footer(text=f"requested by {ctx.author} response time : {round(self.bot.latency * 1000)} ms",
                         icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command()
    async def decode(self, ctx, *, text):
        await ctx.trigger_typing()
        text1 = text
        key = os.getenv("key")
        f = Fernet(key)
        try:
            if text1.startswith("https://mystb.in/"):
                text1 = str(await self.bot.mystbin.get(text))
            new = bytes(text1, "utf-8")
            decrypted = f.decrypt(new)
            decrypted = str(decrypted, 'utf-8')
            await ctx.reply(decrypted)
        except:
            await ctx.send("You provided a invalid link")

    @commands.command()
    async def encode(self, ctx, *, text: str):
        await ctx.trigger_typing()
        key = os.getenv("key")
        f = Fernet(key)
        newtext = bytes(text, "utf-8")
        new_token = f.encrypt(newtext)
        new_token = str(new_token, 'utf-8')
        if len(new_token) > 0:
            paste = await self.bot.mystbin.post(new_token)
            new_token = str(paste)
        await ctx.reply(new_token)

    @commands.command()
    async def ovoly(self, ctx, *, text):
        ovo = text.replace("l", "v").replace("L", "v").replace("r", "v").replace(
            "R", "v")
        await ctx.reply(f"{ovo} ovo")

    @commands.command()
    async def roast(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.trigger_typing()
        async with aiohttp.ClientSession().get("https://evilinsult.com/generate_insult.php") as resp:
            response = await resp.text()
        async with aiohttp.ClientSession().get("https://insult.mattbas.org/api/insult") as resp:
            response3 = await resp.text()
        response2 = await self.bot.dag.roast()
        choice = random.randint(1, 3)
        if choice == 1:
            response = response
        elif choice == 2:
            response == response2
        else:
            response == response3
        text = f"{member.mention}, {response}"
        await ctx.send(text)


def setup(bot):
    bot.add_cog(fun(bot))
