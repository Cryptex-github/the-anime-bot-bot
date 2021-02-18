import asyncio
import discord
from menus import menus


class AnimePages(menus.MenuPages):
    def __init__(self, source):
        super().__init__(source=source, check_embeds=True)

    async def finalize(self, timed_out):
        try:
            if timed_out:
                await self.message.clear_reactions()
            else:
                await self.message.delete()
        except discord.HTTPException:
            pass

    # @menus.button('\N{INFORMATION SOURCE}\ufe0f', position=menus.Last(3))
    # async def show_help(self, payload):
    #       """shows this message"""
    #       embed = discord.Embed(title='Paginator help', description='Hello! Welcome to the help page.')
    #       messages = []
    #       for (emoji, button) in self.buttons.items():
    #           messages.append(f'{emoji}: {button.action.__doc__}')

    #       embed.add_field(name='What are these reactions for?', value='\n'.join(messages), inline=False)
    #       embed.set_footer(text=f'We were on page {self.current_page + 1} before this message.')
    #       await self.message.edit(content=None, embed=embed)

    #       async def go_back_to_current_page():
    #           await asyncio.sleep(30.0)
    #           await self.show_page(self.current_page)

    #       self.bot.loop.create_task(go_back_to_current_page())

    @menus.button('\N{INPUT SYMBOL FOR NUMBERS}', position=menus.Last(1.5))
    async def numbered_page(self, payload):
        """lets you type a page number to go to"""
        channel = self.message.channel
        author_id = payload.user_id
        to_delete = [await channel.send("What page you want to teleport to")]

        def message_check(m):
            return m.author.id == author_id and \
                   channel == m.channel and \
                   m.content.isdigit()

        try:
            msg = await self.bot.wait_for('message', check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(await channel.send('Took too long.'))
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            await self.show_checked_page(page - 1)

        try:
            await channel.delete_messages(to_delete)
        except Exception:
            pass
