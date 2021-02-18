import re
import asyncio

import discord
import lavalink
from discord.ext import commands

url_rx = re.compile(r'https?://(?:www\.)?.+')


class Music(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
    if not hasattr(bot, 'lavalink'):
      bot.lavalink = lavalink.Client(787927476177076234)
      bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'eu', 'default-node')
      bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')
    lavalink.add_event_hook(self.track_hook)
  def cog_unload(self):
    self.bot.lavalink._event_hooks.clear()
  
  async def cog_before_invoke(self, ctx):
    guild_check = ctx.guild is not None
    if guild_check:
      await self.ensure_voice(ctx)
    return guild_check
  async def cog_command_error(self, ctx, error):
    if isinstance(error, commands.CommandInvokeError):
      await ctx.send(error.original)
  async def ensure_voice(self, ctx):
    player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    should_connect = ctx.command.name in ('play',)
    if not ctx.author.voice or not ctx.author.voice.channel:
      raise commands.CommandInvokeError('Join a voicechannel first.')
    if not player.is_connected:
      if not should_connect:
        raise commands.CommandInvokeError('Not connected.')
      permissions = ctx.author.voice.channel.permissions_for(ctx.me)

      if not permissions.connect or not permissions.speak:  
        raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

      player.store('channel', ctx.channel.id)
      await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
    else:
      if int(player.channel_id) != ctx.author.voice.channel.id:
        raise commands.CommandInvokeError('You need to be in my voicechannel.')
  
  async def track_hook(self, event):
    if isinstance(event, lavalink.Events.QueueEndEvent):
      await asyncio.sleep(30)
      guild_id = int(event.player.guild_id)
      await self.connect_to(guild_id, None)
  async def connect_to(self, guild_id: int, channel_id: str):
    ws = self.bot._connection._get_websocket(guild_id)
    await ws.voice_state(str(guild_id), channel_id)
  @commands.command(aliases=['p'])
  async def play(self, ctx, *, query: str):
    player = self.bot.lavalink.player_manager.get(ctx.guild.id)
    query = query.strip('<>')
    if not url_rx.match(query):
      query = f'ytsearch:{query}'
    results = await player.node.get_tracks(query)
    if not results or not results['tracks']:
      return await ctx.send('Nothing found!')
    embed = discord.Embed(color=0x00ff6a)
    if results['loadType'] == 'PLAYLIST_LOADED':
      tracks = results['tracks']
      for track in tracks:
        player.add(requester=ctx.author.id, track=track)
      embed.title = 'Playlist Enqueued!'
      embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
    else:
      track = results['tracks'][0]
      embed.title = 'Track Enqueued'
      embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
      track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
      player.add(requester=ctx.author.id, track=track)
    await ctx.send(embed=embed)
    if not player.is_playing:
      await player.play()
  @commands.command(aliases=['dc'])
  async def disconnect(self, ctx):
    player = self.bot.lavalink.player_manager.get(ctx.guild.id)
    if not player.is_connected:
      return await ctx.send('Not connected.')
    if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
      return await ctx.send('You\'re not in my voicechannel!')
    player.queue.clear()
    await player.stop()
    await self.connect_to(ctx.guild.id, None)
    await ctx.send('Disconnected.')

def setup(bot):
    bot.add_cog(Music(bot))
