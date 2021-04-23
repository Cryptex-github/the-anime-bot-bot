import discord
from discord.ext import commands
import random
from utils.subclasses import AnimeContext
import humanize
import ratelimiter
import datetime


class logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ratelimiter = ratelimiter.RateLimiter(max_calls=5, period=20)
        self.events = [
            "channel_create",
            "channel_update",
            "channel_delete",
            "role_create",
            "role_update",
            "role_delete",
            "guild_update",
            "emojis_update",
            "member_update",
            "member_ban",
            "member_unban",
            "invite_change",
            "member_join",
            "member_leave",
            "voice_channel_change",
            "message_delete",
            "message_edit",
        ]
        self.bot.loop.create_task(self.make_cache())

    async def make_cache(self):
        await self.bot.wait_until_ready()
        logs = await self.bot.db.fetch("SELECT * FROM logging")
        if logs:
            for i in logs:
                self.bot.logging_cache[i["guild_id"]] = dict(i.items())

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def logging(self, ctx):
        """
        View the status of logging
        """
        logging_settings = self.bot.logging_cache.get(ctx.guild.id)
        if not logging_settings:
            return await ctx.send(
                f"You have not enable logging run {ctx.prefix}logging setup to enable it"
            )
        settings = [
            f"{i} - {str(v).replace(logging_settings['webhook'], 'secrect webhook')}"
            for i, v in logging_settings.items()
        ]
        settings = "\n".join(settings)
        await ctx.send(
            embed=discord.Embed(color=self.bot.color, description=settings)
        )

    @logging.command()
    @commands.has_permissions(manage_guild=True)
    async def setup(
        self, ctx: AnimeContext, channel: discord.TextChannel, nowebhook=False
    ):
        """
        Setup logging:
        Usage:
        ovo logging setup #logging
        or if you don't want the bot to send message with webhook:
        ovo logging setup #logging True
        note that normal message will be slower then webhooks
        """
        if ctx.guild.id in self.bot.logging_cache.keys():
            return await ctx.send(
                f"Logging is already on use {ctx.prefix}logging off to turn it off"
            )
        if nowebhook:
            logging = await self.bot.db.fetchrow(
                "INSERT INTO logging (guild_id, channel_id, webhook, channel_create, channel_update, channel_delete, role_create, role_update, role_delete, guild_update, emojis_update, member_update, member_ban, member_unban, invite_change, member_join, member_leave, voice_channel_change, message_delete, message_edit) VALUES ($1, $2, $3, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4) RETURNING *;",
                ctx.guild.id,
                channel.id,
                "nowebhook",
                True,
            )
            self.bot.logging_cache[ctx.guild.id] = dict(logging.items())
            return await ctx.send(
                f"Success, logging is enabled in this server, logging channel is {channel.mention} and no webhook is enabled"
            )

        try:
            webhook = None
            webhooks = await channel.webhooks()
            for i in webhooks:
                if i.name == "The Anime Bot logging":
                    webhook = i
                    break
            if not webhook:
                webhook = await channel.create_webhook(
                    name="The Anime Bot logging",
                    avatar=await self.bot.user.avatar_url_as(
                        format="png"
                    ).read(),
                    reason="The Anime Bot logging",
                )
        except discord.HTTPException:
            if await channel.webhooks():
                webhook = random.choice(await channel.webhooks())
            else:
                return await ctx.send(
                    "Unable to create webhook in this channel maybe try a different channel?"
                )
        except discord.Forbidden:
            return await ctx.send(
                "I do not have permission to create webhook in that channel, please make sure I have `manage_webhook` permission"
            )
        logging = await self.bot.db.fetchrow(
            "INSERT INTO logging (guild_id, channel_id, webhook, channel_create, channel_update, channel_delete, role_create, role_update, role_delete, guild_update, emojis_update, member_update, member_ban, member_unban, invite_change, member_join, member_leave, voice_channel_change, message_delete, message_edit) VALUES ($1, $2, $3, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4, $4) RETURNING *;",
            ctx.guild.id,
            channel.id,
            webhook.url,
            True,
        )
        self.bot.logging_cache[ctx.guild.id] = dict(logging.items())
        await ctx.send(
            f"Success, logging is enabled in this server, logging channel is {channel.mention}"
        )

    @logging.command()
    @commands.has_permissions(manage_guild=True)
    async def off(self, ctx):
        if ctx.guild.id not in self.bot.logging_cache.keys():
            return await ctx.send("logging is already off")
        self.bot.logging_cache.pop(ctx.guild.id)
        await self.bot.db.execute(
            "DELETE FROM logging WHERE guild_id = $1", ctx.guild.id
        )
        await ctx.send("Success logging have been turn off")

    @logging.command()
    @commands.has_permissions(manage_guild=True)
    async def toggle(self, ctx: AnimeContext, event: str):
        """
        Toggle a certain event
        Usage:
        ovo logging toggle message_edit
        """
        if ctx.guild.id not in self.bot.logging_cache.keys():
            return await ctx.send("Logging is not enabled")
        if self.bot.logging_cache[ctx.guild.id].get(event) is None:
            events = "\n".join(self.events)
            return await ctx.send(
                f"That not a valid event a list of valid events \n{events}"
            )
        if self.bot.logging_cache[ctx.guild.id][event]:
            self.bot.logging_cache[ctx.guild.id][event] = False
            await self.bot.db.execute(
                f"UPDATE logging SET {event} = $1 WHERE guild_id = $2",
                False,
                ctx.guild.id,
            )
            return await ctx.send(f"{event} has been turn off")
        else:
            self.bot.logging_cache[ctx.guild.id][event] = True
            await self.bot.db.execute(
                f"UPDATE logging SET {event} = $1 WHERE guild_id = $2",
                True,
                ctx.guild.id,
            )
            return await ctx.send(f"{event} has been turn on")

    async def send_message(self, channel_id, embed):
        async with self.ratelimiter:
            channel = self.bot.get_channel(channel_id)
            await channel.send("logging no webhook mode ON", embed=embed)

    async def send_webhook(self, guild_id, embed, event):
        if guild_id not in self.bot.logging_cache.keys():
            return
        if self.bot.logging_cache[guild_id][event] == False:
            return
        webhook_url = self.bot.logging_cache[guild_id]["webhook"]
        channel_id = self.bot.logging_cache[guild_id]["channel_id"]
        if webhook_url == "nowebhook":
            return await self.send_message(channel_id, embed)
        webhook = discord.Webhook.from_url(
            webhook_url, adapter=discord.AsyncWebhookAdapter(self.bot.session)
        )
        async with self.ratelimiter:
            try:
                message = await webhook.send(
                    embed=embed,
                    username="The Anime Bot logging",
                    avatar_url=str(self.bot.user.avatar_url_as(format="png")),
                )
            except discord.NotFound:
                channel = self.bot.get_channel(channel_id)
                webhooks = await channel.webhooks()
                if not webhooks:
                    webhook = await channel.create_webhook(
                        name="The Anime Bot logging",
                        avatar=await self.bot.user.avatar_url_as(
                            format="png"
                        ).read(),
                        reason="The Anime Bot logging",
                    )
                    message = await webhook.send(
                        embed=embed,
                        username="The Anime Bot logging",
                        avatar_url=str(
                            self.bot.user.avatar_url_as(format="png")
                        ),
                    )
                    await self.bot.db.execute(
                        "UPDATE logging SET webhook = $1, WHERE guild_id = $2",
                        webhook.url,
                        channel.guild.id,
                    )
                webhook = random.choice(webhooks)
                message = await webhook.send(
                    embed=embed,
                    username="The Anime Bot logging",
                    avatar_url=str(self.bot.user.avatar_url_as(format="png")),
                )

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if channel.guild.id not in self.bot.logging_cache.keys():
            return
        embed = discord.Embed(
            color=self.bot.color,
            title="New channel created",
            description=f"**channel name:** {channel.name}\n**Category:** {channel.category}",
            timestamp=channel.created_at,
        )
        embed.set_footer(text=f"Channel ID: {channel.id}")
        await self.send_webhook(channel.guild.id, embed, "channel_create")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if after.guild.id not in self.bot.logging_cache.keys():
            return
        embed = discord.Embed(
            color=self.bot.color,
            title="Channel Updated",
            timestamp=after.created_at,
        )
        embed.set_footer(text=f"Channel ID: {after.id}")
        return await self.send_webhook(after.guild.id, embed, "channel_update")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if channel.guild.id not in self.bot.logging_cache.keys():
            return
        embed = discord.Embed(
            color=self.bot.color,
            title="Channel Deleted",
            description=f"**channel name:** {channel.name}\n**Category:** {channel.category}",
            timestamp=channel.created_at,
        )
        embed.set_footer(text=f"Channel ID: {channel.id}")
        await self.send_webhook(channel.guild.id, embed, "channel_delete")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if role.guild.id not in self.bot.logging_cache.keys():
            return
        embed = discord.Embed(
            color=self.bot.color,
            title="Role Created",
            description=f"**Role name:** {role.name}\n**Color:** {str(channel.color)}",
            timestamp=channel.created_at,
        )
        embed.set_footer(text=f"Role ID: {role.id}")
        await self.send_webhook(role.guild.id, embed, "role_delete")

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.color != after.color:
            embed = discord.Embed(
                color=self.bot.color,
                title="Role Updated",
                description=f"**Role name:** {after.name}\n**Old Color:** {str(before.color)}\n**New Color:** {str(after.color)}",
                timestamp=datetime.datetime.utcnow(),
            )
            await self.send_webhook(after.guild.id, embed, "role_update")
        if before.name != after.name:
            embed = discord.Embed(
                color=self.bot.color,
                title="Role Updated",
                description=f"**Old Role Name:** {before.name}\n**New Role Name:** {after.name}",
                timestamp=datetime.datetime.utcnow(),
            )
            await self.send_webhook(after.guild.id, embed, "role_update")
        if before.permissions != after.permissions:
            changed_permission = [
                (i, v)
                for i, v in dict(after.permissions).items()
                if dict(before.permissions)[i] != v
            ]
            to_display = []
            for i, v in changed_permission:
                to_display.append(
                    f"Added permission {i}"
                ) if v else to_display.append(f"Removed permission {i}")
            to_display = "\n".join(to_display)
            embed = discord.Embed(
                color=self.bot.color,
                title="Role Updated",
                description=f"**New Permissions:** {to_display}",
                timestamp=datetime.datetime.utcnow(),
            )
            await self.send_webhook(after.guild.id, embed, "role_update")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if role.guild.id not in self.bot.logging_cache.keys():
            return
        embed = discord.Embed(
            color=self.bot.color,
            title="Role Deleted",
            description=f"**Role name:** {role.name}\n**Color:** {str(channel.color)}",
            timestamp=channel.created_at,
        )
        embed.set_footer(text=f"Channel ID: {channel.id}")
        await self.send_webhook(role.guild.id, embed, "role_delete")

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if before.afk_channel != after.afk_channel:
            embed = discord.Embed(
                color=self.bot.color,
                title="Guild Updated",
                description=f"**Old Afk channel:** {before.afk_channel.mention}*\n*New Afk channel:** {after.afk_channel.mention}",
                timestamp=datetime.datetime.utcnow(),
            )
            return await self.send_webhook(after.id, embed, "guild_update")
        if before.afk_timeout != after.afk_timeout:
            embed = discord.Embed(
                color=self.bot.color,
                title="Guild Updated",
                description=f"**Old Afk timeout:** {before.afk_timeout}*\n*New Afk timeout:** {after.afk_timeout}",
                timestamp=datetime.datetime.utcnow(),
            )
            return await self.send_webhook(after.id, embed, "guild_update")
        if before.name != after.name:
            embed = discord.Embed(
                color=self.bot.color,
                title="Guild Updated",
                description=f"**Old Name:** {before.name}*\n*New name:** {after.name}",
                timestamp=datetime.datetime.utcnow(),
            )
            return await self.send_webhook(
                after.guild.id, embed, "guild_update"
            )
        embed = discord.Embed(
            color=self.bot.color,
            title="Guild Updated",
            description=f"Something updated but I can't trace what updated",
            timestamp=datetime.datetime.utcnow(),
        )
        await self.send_webhook(after.id, embed, "guild_update")

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        if len(before) < len(after):
            new_emojis = [str(i) for i in after if i not in before]
            embed = discord.Embed(
                color=self.bot.color,
                title="New Emojis Added",
                description=f"{', '.join(new_emojis)}",
                timestamp=datetime.datetime.utcnow(),
            )
        else:
            removed_emojis = [str(i) for i in before if i not in after]
            embed = discord.Embed(
                color=self.bot.color,
                title="Emojis Removed",
                description=f"{', '.join(removed_emojis)}",
                timestamp=datetime.datetime.utcnow(),
            )

        await self.send_webhook(guild.id, embed, "emojis_update")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = discord.Embed(
                color=self.bot.color,
                title="Nickname Changed",
                description=f"Before Nickname: {before.nick}\nAfter Nickname: {after.nick}",
                timestamp=datetime.datetime.utcnow(),
            )
            embed.set_footer(text=f"User ID: {after.id}")
            await self.send_webhook(after.guild.id, embed, "member_update")
        if before.roles != after.roles:
            if len(before.roles) < len(after.roles):
                roles = set(before.roles)
                new_roles = [i.mention for i in after.roles if i not in roles]
                embed = discord.Embed(
                    color=self.bot.color,
                    title="Role Added",
                    description=f"Member: {after.mention}\nRoles: {', '.join(new_roles)}",
                    timestamp=datetime.datetime.utcnow(),
                )
            else:
                roles = set(after.roles)
                removed_roles = [
                    i.mention for i in before.roles if i not in roles
                ]
                embed = discord.Embed(
                    color=self.bot.color,
                    title="Role Removed",
                    description=f"Member: {after.mention}\nRoles: {', '.join(removed_roles)}",
                    timestamp=datetime.datetime.utcnow(),
                )

            embed.set_footer(text=f"User ID: {after.id}")
            return await self.send_webhook(
                after.guild.id, embed, "member_update"
            )

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            color=self.bot.color,
            title="Member Banned",
            description=f"User: {str(user)} {user.mention} ({user.id})",
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_footer(text=f"User ID: {user.id}")
        await self.send_webhook(guild.id, embed, "member_ban")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(
            color=self.bot.color,
            title="Member Unbanned",
            description=f"User: {str(user)} {user.mention} ({user.id})",
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_footer(text=f"User ID: {user.id}")
        await self.send_webhook(guild.id, embed, "member_unban")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        embed = discord.Embed(
            color=self.bot.color,
            title="Invite Created",
            description=f"Invite ID: {invite.id}\nInvite URL: {invite.url}",
            timestamp=invite.created_at,
        )
        embed.set_footer(text=f"User ID: {invite.inviter.id}")
        await self.send_webhook(invite.guild.id, embed, "invite_change")

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        embed = discord.Embed(
            color=self.bot.color,
            title="Invite Deleted",
            description=f"Invite ID: {invite.id}\nInvite URL: {invite.url}",
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_footer(text=f"User ID: {invite.inviter.id}")
        await self.send_webhook(invite.guild.id, embed, "invite_change")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            color=self.bot.color,
            title="Member joined",
            description=f"{member.mention} just joined. We now have {member.guild.member_count} members. Account Created at: {humanize.precisedelta(member.created_at)} ago",
            timestamp=datetime.datetime.now(),
        )
        embed.set_footer(text=f"ID: {member.id}")
        await self.send_webhook(member.guild.id, embed, "member_join")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            color=self.bot.color,
            title="Member left",
            description=f"{member.mention} just left. We now have {member.guild.member_count} members. Account Created at: {humanize.precisedelta(member.created_at)} ago",
            timestamp=datetime.datetime.now(),
        )
        embed.set_footer(text=f"ID: {member.id}")
        await self.send_webhook(member.guild.id, embed, "member_leave")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not before.channel:
            embed = discord.Embed(
                color=self.bot.color,
                title="Joined voice channel",
                description=f"{member.display_name} joined voice channel {after.channel.mention}",
            )
            embed.set_footer(text=f"User ID: {member.id}")
            return await self.send_webhook(
                member.guild.id, embed, "voice_channel_change"
            )
        if not after.channel:
            embed = discord.Embed(
                color=self.bot.color,
                title="Left voice channel",
                description=f"{member.display_name} left voice channel {before.channel.mention}",
            )
            embed.set_footer(text=f"User ID: {member.id}")
            return await self.send_webhook(
                member.guild.id, embed, "voice_channel_change"
            )
        if before.channel != after.channel:
            embed = discord.Embed(
                color=self.bot.color,
                title="Changed voice channel",
                description=f"{member.display_name} changed voice channel from {before.channel.mention} to {after.channel.mention}",
            )
            embed.set_footer(text=f"User ID: {member.id}")
            return await self.send_webhook(
                member.guild.id, embed, "voice_channel_change"
            )

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        ...
        # if payload.cached_message:
        #     return
        # if not payload.data.get("guild_id"):
        #     return
        # embed = discord.Embed(color=self.bot.color, title="Message Edited", description=f"The message is too old I can't find the content", timestamp=datetime.datetime.utcnow())
        # embed.set_footer(text=f"Message ID: {payload.message_id}")
        # await self.send_webhook(payload.data.get("guild_id"), embed, "message_edit")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.embeds:
            return
        before_content = (
            before.content
            or "message don't have content could be a attachment or embed"
        )
        after_content = (
            after.content
            or "message don't have content could be a attachment or embed"
        )
        embed = discord.Embed(
            color=self.bot.color,
            title="Message Edited",
            timestamp=datetime.datetime.utcnow(),
        )
        embed.add_field(name="Before", value=f"**Content:** {before_content}")
        embed.add_field(name="After", value=f"**Content:** {after_content}")
        embed.set_author(
            name=str(after.author),
            icon_url=str(after.author.avatar_url_as(static_format="png")),
        )
        embed.set_footer(text=f"User ID: {after.id} Message ID: {after.id}")
        await self.send_webhook(after.guild.id, embed, "message_edit")

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        ids = "\n".join(str(i) for i in payload.message_ids)
        embed = discord.Embed(
            color=self.bot.color,
            title="Bulk messages deleted",
            description=f"Message Ids: \n{ids}",
        )
        await self.send_webhook(payload.guild_id, embed, "message_delete")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if not payload.guild_id:
            return
        message = payload.cached_message
        if message:
            if message.webhook_id:
                return
            if message.content == "logging no webhook mode ON":
                return
            content = (
                message.content
                or "message don't have content could be a attachment or embed"
            )
            embed = discord.Embed(
                color=self.bot.color,
                title="Message Deleted",
                description=f"**Content:** {content}",
                timestamp=datetime.datetime.utcnow(),
            )
            embed.set_author(
                name=str(message.author),
                icon_url=str(
                    message.author.avatar_url_as(static_format="png")
                ),
            )
            embed.set_footer(
                text=f"User ID: {message.author.id} Message ID: {message.id}"
            )
            await self.send_webhook(message.guild.id, embed, "message_delete")
        else:
            embed = discord.Embed(
                color=self.bot.color,
                title="Message Deleted",
                description=f"The message is too old I can't find the content",
                timestamp=datetime.datetime.utcnow(),
            )
            await self.send_webhook(payload.guild_id, embed, "message_delete")


def setup(bot):
    bot.add_cog(logging(bot))
