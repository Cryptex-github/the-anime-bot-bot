import discord
from discord.ext import commands
from jishaku.paginators import PaginatorEmbedInterface, PaginatorInterface

class todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(invoke_without_command=True)
    async def todo(self, ctx):
        pass
    @todo.command()
    async def list(self, ctx):
        todos = await self.bot.db.fetch("SELECT * FROM todos WHERE author_id = $1 ORDER BY created_at", ctx.author.id)
        if not todos:
            return await ctx.send(embed=discord.Embed(color=self.bot.color, description=f"you have no todos `{ctx.prefix}todo add sometodos` to make one"))
        paginator = commands.Paginator(prefix="", suffix="", max_size=1000)
        counter = 1
        for i in todos:
            paginator.add_line(f"[{counter}]({i['jump_url']}). {i['content']}")
            counter += 1
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)
    @todo.command()
    async def add(self, ctx, *, content):
        await self.bot.db.execute("INSERT INTO todos (author_id, content, created_at, message_id, jump_url) VALUES ($1, $2, $3, $4, $5)", ctx.author.id, content, ctx.message.created_at, ctx.message.id, ctx.message.jump_url)
        return await ctx.send(embed=discord.Embed(color=self.bot.color, description="Successfully added new todo"))
    

        
def setup(bot):
    bot.add_cog(todo(bot))