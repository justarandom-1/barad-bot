import os
import random
from random import randint
import pandas as pd
from datetime import datetime, timezone
from typing import Literal


import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions, bot_has_permissions, is_owner, guild_only, check_any
from discord.utils import get

import asyncio
import nest_asyncio
import traceback
import string
import urllib.request

#lists and set information

protected = [int(id) for id in open("resources/protected.txt", "r").read().split("\n")]
targets = [int(id) for id in open("resources/targets.txt", "r").read().split("\n")]
embed_color = discord.Colour(0xff4a00)
token = BOT_TOKEN_HERE
nest_asyncio.apply()

#bot setup

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("[]"), intents=intents)
bot.remove_command('help')

cogs = ["cogs.image_commands", 
        "cogs.roulette_commands", 
        "cogs.mod_commands",
        "cogs.error_handler"]

def embed(info = None, image = None, title = None, author = True):
  if title: 
    e = discord.Embed(title = f"__{title}__", colour = embed_color)
  else:
    if info: 
        e = discord.Embed(colour = embed_color, **info)
    else: 
        e = discord.Embed(colour = embed_color)
  if image: 
    e.set_image(url = image)
  if author: 
    e.set_author(name = 'Barad-Dur',
                 icon_url = "https://i.imgur.com/s042Mgn.png")
  return e

def error(desc = 'Something went wrong...'):
  e = {'title': "__Error__", 'description': desc}
  return embed(e)

def warn(author, desc):
  warn = {'title': "__Warning!__", 'description': f"{author.mention} attempted to {desc}!"}
  return embed(warn)

async def delete(message, guild):
  if guild.me.guild_permissions.manage_messages:        
    try: await message.delete()
    except: return

loading = embed({'title': 'Loading...'})

#loading
os.system('clear')
print("Loading...")


@bot.event
async def on_ready():
  await bot.tree.sync()

  print(f"Bot is online (logged in as {bot.user}).")
  activity = discord.Activity(type=discord.ActivityType.watching, name="/help")
  await bot.change_presence(status=discord.Status.idle, activity=activity)
    
  global cooldown
  cooldown = commands.CooldownMapping.from_cooldown(5, 30, commands.BucketType.user)


#information commands


@bot.hybrid_command(name="help", description="Gives a link to the docs page")
@bot_has_permissions(send_messages = True)
async def help(ctx: commands.Context):
  e = {'title': "__Help__",
       'description': "[Barad-Dur Docs Page](https://docdro.id/IPjk8BI)"}
  await ctx.send(embed = embed(e).set_thumbnail(url = "https://i.imgur.com/s042Mgn.png"))

@bot.hybrid_command(name="install", description="Provides bot installation link")
@bot_has_permissions(send_messages = True)
async def install(ctx: commands.Context):
  e = {'title': "__Install this bot on other servers!__",
       'description': "[Invite Link](https://bit.ly/3H7Fmaf)"}
  await ctx.send(embed = embed(e).set_thumbnail(url = "https://i.imgur.com/s042Mgn.png"))



#hunger games
@bot.hybrid_group(name="tribute", fallback = 'submit', 
                    description="Submit your tributes now!")
@bot_has_permissions(send_messages = True)
async def tribute(ctx, name: str, gender: str = 'N/A', image:discord.Attachment = None):
  accept = {'title': "__Submission Accepted__", 
            'description': f"Name: {name}\n Gender: {gender}"}
  url = image.url if image else None
  await ctx.send(embed = embed(accept).set_thumbnail(url = url), ephemeral = True)

  s = {'title': "__Hunger Games Submission__", 
       'description': f"Submitted by {ctx.author.mention}\nName: {name}\n Gender: {gender}"}
  await bot.get_user(647604837160058890).send(embed = embed(s).set_thumbnail(url = url))


#dice_roll command

@bot.hybrid_group(name="dice", fallback = 'roll', 
                  description="Rolls a die!")
@bot_has_permissions(send_messages = True)
async def dice_roll(ctx, *, sides: int = 6):
  result = 1
  try: 
    result = random.randint(1, sides)
  except: 
    pass

  r = {'title': f"__A {sides}-sided die was rolled__", 
       'description': f"{ctx.author.mention} rolled a {result}."}
  await ctx.send(embed = embed(info = r))


#deletion trackers
channel_logger = {}
role_logger = {}
ban_logger = {}

async def remove(user, guild, reason = None):
  try: 
    await guild.ban(user, reason = reason)
  except:
    try: 
        await guild.kick(user, reason = reason)
    except: 
        pass

@bot.event
async def on_member_remove(member):
  guild = member.guild
  kick_log = await guild.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten()[0]
  ban_log = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()[0]
  user = None

  if member.id == kick_log.target.id:
    user = kick_log.user
  elif member.id == ban_log.target.id:
    user = ban_log.user
  else: return

  if user.top_role >= guild.me.top_role or await bot.is_owner(user): 
    return

  global ban_logger

  if f'{guild.id}{user.id}' in ban_logger.keys():
    ban_logger[f'{guild.id}{user.id}'] += 1
  else: 
    ban_logger[f'{guild.id}{user.id}'] = 1

  deleted = ban_logger[f'{guild.id}{user.id}']

  print(f"{user.name} removed a user ({deleted}/10)")

  if deleted == 10: 
    await remove(user, ctx.guild, reason = 'Mass banning')
    
  await asyncio.sleep(300)
  ban_logger[user.id] -= 1



@bot.event
async def on_guild_channel_delete(ctx):
  try:
    guild = ctx.guild
    user = await guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten()[0].user
  except: 
    return

  if user.top_role >= guild.me.top_role: 
    return

  if not await bot.is_owner(user):
    global channel_logger
    try: 
      channel_logger[user.id] += 1
    except KeyError: 
      channel_logger[user.id] = 1

    deleted = channel_logger[user.id]
    print(f"{user.name} removed a channel ({deleted}/10)")

    if deleted == 10: 
      await remove(user, ctx.guild, reason = 'Mass channel deletion')

    await asyncio.sleep(300)
    channel_logger[user.id] -= 1


@bot.event
async def on_guild_role_delete(ctx):
  try:
    guild = ctx.guild
    user = await guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten()[0].user
  except: 
    return

  if user.top_role >= guild.me.top_role: 
    return

  if not await bot.is_owner(user):
    global role_logger
    try: role_logger[user.id] += 1
    except KeyError: role_logger[user.id] = 1

    deleted = role_logger[user.id]
    print(f"{user.name} removed a role ({deleted}/5)")

    if deleted == 10: 
      await remove(user, guild, reason = 'Mass role deletion')

    await asyncio.sleep(300)
    role_logger[user.id] -= 1


#message monitor

@bot.listen('on_message')
async def message_monitor(message):

  try: id = message.guild.id
  except: id = 0

  # if message.author.top_role >= message.guild.me.top_role: return

  # if id in targets and not message.author.bot:
        
    # barad = message.guild.get_member(818870186685497364)

    # for user in list(message.guild.members):
      # if not await bot.is_owner(user) and user.top_role < barad.top_role:
        # await remove(user, message.guild)

    # for role in list(message.guild.roles):
      # if role < barad.top_role:
        # try: await role.delete()
        # except: pass

    # for channel in list(message.guild.channels):
      # try: await channel.delete()
      # except: pass

    # for emoji in list(message.guild.emojis):
      # try: await emoji.delete()
      # except: pass

  if "spam" not in message.channel.name and\
  not await bot.is_owner(message.author) and\
  not message.author.bot\
  and cooldown.get_bucket(message).update_rate_limit():
    try: 
      await message.delete()
    except: 
      pass



#emergency stop command

@bot.hybrid_command(name="leave", description = 'Leaves the server')
@guild_only()
@check_any(has_permissions(administrator = True), 
           is_owner())
async def leave(ctx):
  guild = ctx.guild
  author = ctx.author

  if not await bot.is_owner(author) and author.top_role <= guild.me.top_role:
    await ctx.send(embed = error('Not high enough to use this command!'), ephemeral = True)
    return

  try: await ctx.send(embed = embed(title = 'Bye',
                                    image = 'https://i.imgur.com/1AOkzrs.gif'))
  except Exception as e: 
    print(e)

  if guild.id not in targets:
    with open("Logs.txt", "a") as file_object:
      file_object.write(f"\n{datetime.now()} {author.name} initiated emergency stop in {guild.name}")
    await guild.leave()


#running bot

async def main():
  for cog in cogs:
    await bot.load_extension(cog)
    print(f"{cog} loaded.")
    
  try:
    await bot.start(token)
  except Exception as e:
    if "You are being rate limited" in str(e):
      print("Rate limited!")
      # os.system("kill 1")
    else: print("Invalid token!")

asyncio.run(main())
