import itertools
import ujson
import asyncpg
import config
import os
import subprocess
import sys
import time
from collections import Counter, OrderedDict

import aiohttp
import aiozaneapi
import alexflipnote
import discord
import eight_ball
from discord.ext.commands.cooldowns import MaxConcurrency
import ipc
import mystbin
import psutil
import vacefron
from asyncdagpi import Client
from discord_slash import SlashCommand

from utils.asyncstuff import asyncexe
from utils.utils import utils

alexflipnote_ = str(config.alex_)
ipc_key = str(config.ipc_key)
zane_api = str(config.zane_api)
TOKEN_ACCESS = str(config.TOKEN_ACCESS)
api_token = str(config.api_token)
import re

from discord.ext import commands

from utils.HelpPaginator import CannotPaginate, HelpPaginator

token=re.compile(r"([a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]{27}|mfa\.[a-zA-Z0-9_\-]{84})")
class AnimeContext(commands.Context):
  def __init__(self, *args, **kwargs):
    self.utils = utils
    super().__init__(*args, **kwargs)
  async def remove(self, *args, **kwargs):
    m = await self.send(*args, **kwargs)
    await m.add_reaction("\U0000274c")
    await self.bot.wait_for("reaction_add", check=lambda i,v: i.message.id == m.id and v.id == self.message.author.id and i.emoji == "\U0000274c")
    await m.delete()
  @discord.utils.cached_property
  def replied_reference(self):
      ref = self.message.reference
      if ref and isinstance(ref.resolved, discord.Message):
          return ref.resolved.to_reference()
      return None

  def big_embed(self):
    embed = discord.Embed(color=0x00ff6a, title="a"*256, description="a"*2048)
    embed.add_field(name="a"*256, value="a"*112)
    embed.add_field(name="a"*256, value="a"*1024)
    embed.set_footer(text="a"*2048)
    return embed
  async def ovoly(self, msg):
    ovo = msg.replace("l", "v").replace("L", "v").replace("r", "v").replace("R", "v")
    return f"{ovo} ovo"
  async def get_paste(self, link):
    try:
      return str(await self.bot.mystbin.get(link))
    except:
      return None
  async def paste(self, content):
    return str(await self.bot.mystbin.post(content))
  async def send(self, content=None, **kwargs):
    # if self.invoked_with("jishaku"):
    #   embed = discord.Embed(color=0x2ecc71, description=content)
    #   message = super().send(content=None, embed=embed)
    #   return message
    if self.message.id in self.bot._message_cache:
      if self.message.edited_at:
        msg = self.bot._message_cache[self.message.id]
        await msg.edit(content=content, **kwargs)
        return msg
      else:
        message = await super().send(content, **kwargs)
        self.bot.to_delete_message_cache[self.message.id].append(message.id)
        return message
    else:
      message = await super().send(content, **kwargs)
      self.bot._message_cache[self.message.id] = message
      self.bot.to_delete_message_cache[self.message.id] = [message.id]
      return message
  async def reply(self, content=None, **kwargs):
    if self.message.id in self.bot._message_cache:
      if self.message.edited_at:
        msg = self.bot._message_cache[self.message.id]
        await msg.edit(content=content, **kwargs)
        return msg
      else:
        message = await super().send(content, **kwargs)
        self.bot.to_delete_message_cache[self.message.id].append(message.id)
        return message
    else:
      message = await super().reply(content, **kwargs)
      self.bot._message_cache[self.message.id] = message
      self.bot.to_delete_message_cache[self.message.id] = [message.id]
      return message
class AnimeMessage(discord.Message):
  pass
class GlobalCooldown(commands.CommandOnCooldown):
  pass
class AnimeColor(discord.Color):
    def init(self, args, **kwargs):
        super().init(args, **kwargs)

    @classmethod
    def lighter_green(cls):
        return cls(0x00ff6a)
async def prefix_get(bot, message):
    if message.guild is None:
        return bot.default_prefix
    if bot.prefixes.get(message.guild.id):
        return bot.prefixes.get(message.guild.id)
    if not bot.prefixes.get(message.guild.id):
        await bot.db.execute("INSERT INTO prefix (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO NOTHING", message.guild.id, bot.default_prefix)
        bot.prefixes[message.guild.id] = bot.default_prefix
        return bot.prefixes[message.guild.id]
    return bot.default_prefix
        
    

class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, **kwds):
        self.size_limit = 1000
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __getitem__(self, key):
        return super().__getitem__(key)
  
    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=True)

            
class AnimeBot(commands.Bot):
  def __init__(self):
    self.connector = aiohttp.TCPConnector(limit=200)
    intents = discord.Intents.default()
    intents.members=True
    # self.ipc = ipc.Server(self, secret_key=ipc_key)
    self.command_list = []
    super().__init__(command_prefix=prefix_get, 
max_messages=1000,
connector = self.connector,
intents=intents, 
description="""
|_   _| |__   ___     / \   _ __ (_)_ __ ___   ___  | __ )  ___ | |_ 
  | | | '_ \ / _ \   / _ \ | '_ \| | '_ ` _ \ / _ \ |  _ \ / _ \| __|
  | | | | | |  __/  / ___ \| | | | | | | | | |  __/ | |_) | (_) | |_ 
  |_| |_| |_|\___| /_/   \_\_| |_|_|_| |_| |_|\___| |____/ \___/ \__|
""",
chunk_guilds_at_startup=False, 
case_insensitive=True, allowed_mentions=discord.AllowedMentions.none())
  def add_command(self, command):
    super().add_command(command)
    command.cooldown_after_parsing = True
    if not getattr(command._buckets, "_cooldown", None):
      command._buckets = commands.CooldownMapping.from_cooldown(1, 3, commands.BucketType.user)
    if command._max_concurrency is None:
      command._max_concurrency = MaxConcurrency(1, per=commands.BucketType.user, wait=False)
  async def create_cache(self):
    await self.wait_until_ready()
    for i in self.guilds:
      await self.db.execute("INSERT INTO prefix (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO NOTHING", i.id, self.default_prefix)
    prefixes = await self.db.fetch("SELECT * FROM prefix")
    for i in prefixes:
        self.prefixes[i["guild_id"]] = i["prefix"]
    emojioptions = await self.db.fetch("SELECT * FROM emojioptions")
    if emojioptions:
      for i in emojioptions:
        self.emojioptions[i["user_id"]] = i["enabled"]
    commandsusage = await self.db.fetch("SELECT * FROM commandsusage")
    for i in commandsusage:
      self.commandsusages[i["command"]] = i["usages"]
      self.command_counter += i["usages"]
    socket = await self.db.fetch("SELECT * FROM socket")
    for i in socket:
      self.socket_stats[i["name"]] = i["count"]
      self.socket_receive += i["count"]

        
  async def chunk_(self, ctx):
    if ctx.guild and not ctx.guild.chunked:
      await ctx.guild.chunk()

  async def before_invoke_(self, ctx):
    try:
      if ctx.message.author.id in [590323594744168494, 711057339360477184]:
        await ctx.command._max_concurrency.release()
    except:
      pass
    await ctx.trigger_typing() if not ctx.command.qualified_name.startswith("jishaku") else ...
    ctx.bot.loop.create_task(self.chunk_(ctx))
  def run(self, *args, **kwargs):
    # self.ipc.start()
    self.default_prefix = ['ovo ']
    self.prefixes = {}
    db = self.loop.run_until_complete(asyncpg.create_pool('postgres://postgres1:postgres@localhost:5432/cryptex'))
    self.db = db
    self.emojioptions = {}
    self.loop.create_task(self.create_cache())
    self.url_regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", re.IGNORECASE)
    self.before_invoke(self.before_invoke_)
    self.bad_word_cache = {} 
    self.logging_cache = {}
    self.logging_webhook_cache = []
    self.utils = utils
    self.deleted_message_cache = LimitedSizeDict()
    self.concurrency = []
    self.color = 0x00ff6a
    self.psutil_process = psutil.Process()
    self.to_delete_message_cache = {}
    self._message_cache = {} 
    self.prefixes = {}
    self.socket_receive = 0
    self.start_time = time.time()
    self.socket_stats = Counter()
    self.command_counter = 0
    self.commandsusages = Counter()
    self.session = aiohttp.ClientSession(headers={"User-Agent": f"python-requests/2.25.1 The Anime Bot/1.1.0 Python/{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]} aiohttp/{aiohttp.__version__}"}, connector=self.connector, json_serialize=ujson.dumps)
    self.mystbin = mystbin.Client(session=self.session)
    self.vacefron_api=vacefron.Client(session=self.session, loop=self.loop)
    self.dag = Client(api_token, session=self.session, loop=self.loop)
    self.alex=alexflipnote.Client(alexflipnote_, session=self.session, loop=self.loop)
    self.ball = eight_ball.ball()
    self.zaneapi = aiozaneapi.Client(zane_api)
    for command in self.commands:
      self.command_list.append(str(command))
      self.command_list.extend([alias for alias in command.aliases])
      if isinstance(command, commands.Group):
          for subcommand in command.commands:
              self.command_list.append(str(subcommand))
              self.command_list.extend([f"{command} {subcommand_alias}" for subcommand_alias in subcommand.aliases])
              if isinstance(subcommand, commands.Group):
                  for subcommand2 in subcommand.commands:
                      self.command_list.append(str(subcommand2))
                      self.command_list.extend([f"{subcommand} {subcommand2_alias}" for subcommand2_alias in subcommand2.aliases])
                      if isinstance(subcommand2, commands.Group):
                          for subcommand3 in subcommand2.commands:
                              self.command_list.append(str(subcommand3))
                              self.command_list.extend([f"{subcommand2} {subcommand3_alias}" for subcommand3_alias in subcommand3.aliases])
    super().run(*args, **kwargs)
  async def close(self):
    await self.session.close()
    await super().close()
  def get_message(self, message_id):
    return self._connection._get_message(message_id)

  async def get_context(self, message, *, cls=None):
    return await super().get_context(message, cls=self.context)
  async def is_ratelimited(self):
    result = await self.is_ws_ratelimited()
    return result

  
