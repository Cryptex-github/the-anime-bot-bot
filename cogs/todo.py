import discord
from discord.ext import commands
from utils.subclasses import AnimeContext
import datetime
from menus import menus
from jishaku.paginators import PaginatorEmbedInterface, PaginatorInterface


class TodoMenuSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=5)

    async def format_page(self, menu, entries):
        return {
            "embed": discord.Embed(
                color=menu.ctx.bot.color,
                title=f"{menu.ctx.author.name}'s todo list",
                description="\n".join(entries),
            )
        }


class todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def todo(self, ctx):
        pass

    @todo.command()
    async def swap(self, ctx: AnimeContext, task1: int, task2: int):
        todos = await self.bot.db.fetch(
            "SELECT * FROM todos WHERE author_id = $1 ORDER BY created_at",
            ctx.author.id,
        )
        if task1 > len(todos) or task2 > len(todos) or todos is None:
            return await ctx.send("You can't swap tasks you don't have")
        task_1 = todos[task1 - 1]
        task_2 = todos[task2 - 1]
        await self.bot.db.execute(
            "UPDATE todos SET created_at = $1 WHERE created_at = $2",
            task_2["created_at"],
            task_1["created_at"],
        )
        await self.bot.db.execute(
            "UPDATE todos SET created_at = $1 WHERE created_at = $2",
            task_1["created_at"],
            task_2["created_at"],
        )
        return await ctx.send(
            embed=discord.Embed(
                color=self.bot.color,
                title="Swap tasks",
                description=f"Succesfully swapped task {task1} and {task2}",
            )
        )

    @todo.command()
    async def remove(self, ctx: AnimeContext, index: commands.Greedy[int]):
        todos = await self.bot.db.fetch(
            "SELECT * FROM todos WHERE author_id = $1 ORDER BY created_at",
            ctx.author.id,
        )
        if todos is None:
            return await ctx.send("You can't remove tasks you don't have")
        for i in index:
            if i > len(todos):
                return await ctx.send("You can't remove tasks you don't have")
        to_delete = [todos[num - 1]["created_at"] for num in index]
        to_display = [f"{i} - {todos[i-1]['content']}" for i in index]
        await self.bot.db.execute(
            "DELETE FROM todos WHERE author_id = $1 AND created_at = ANY ($2)",
            ctx.author.id,
            tuple(to_delete),
        )
        return await ctx.send(
            embed=discord.Embed(
                color=self.bot.color,
                title=f"Deleted {len(index)} tasks",
                description="\n".join(to_display),
            )
        )

    @todo.command()
    async def list(self, ctx):
        todos = await self.bot.db.fetch(
            "SELECT * FROM todos WHERE author_id = $1 ORDER BY created_at",
            ctx.author.id,
        )
        if not todos:
            return await ctx.send(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f"you have no todos `{ctx.prefix}todo add sometodos` to make one",
                )
            )
        lists = [
            f"[{counter}]({i['jump_url']}). {i['content']}"
            for counter, i in enumerate(todos, start=1)
        ]

        pages = menus.MenuPages(
            source=TodoMenuSource(lists), delete_message_after=True
        )
        await pages.start(ctx)

    @todo.command()
    async def multiadd(self, ctx: AnimeContext, *, contents):
        """
        Add multiple tasks at once split by ,
        Example:
        ovo multiadd taskone,tasktwo,taskthree
        """
        tasks = contents.split(",")
        offset = 1
        for i in tasks:
            await self.bot.db.execute(
                "INSERT INTO todos (author_id, content, created_at, message_id, jump_url) VALUES ($1, $2, $3, $4, $5)",
                ctx.author.id,
                i,
                ctx.message.created_at
                + datetime.timedelta(microseconds=offset),
                ctx.message.id,
                ctx.message.jump_url,
            )
            offset += 1
        todos = await self.bot.db.fetch(
            "SELECT * FROM todos WHERE author_id = $1 AND message_id = $2",
            ctx.author.id,
            ctx.message.id,
        )
        return await ctx.send(
            embed=discord.Embed(
                color=self.bot.color,
                title="Successfully added new todos",
                description="\n".join(tasks),
            )
        )

    @todo.command()
    async def add(self, ctx: AnimeContext, *, content):
        await self.bot.db.execute(
            "INSERT INTO todos (author_id, content, created_at, message_id, jump_url) VALUES ($1, $2, $3, $4, $5)",
            ctx.author.id,
            content,
            ctx.message.created_at,
            ctx.message.id,
            ctx.message.jump_url,
        )
        todos = await self.bot.db.fetch(
            "SELECT * FROM todos WHERE author_id = $1", ctx.author.id
        )
        return await ctx.send(
            embed=discord.Embed(
                color=self.bot.color,
                title="Successfully added new todo",
                description=f"{len(todos)} - {content}",
            )
        )


def setup(bot):
    bot.add_cog(todo(bot))
