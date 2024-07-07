from main import *

#cog:
class roulette_commands(commands.Cog):    

    #set self
    def __init__(self, bot): 
      self.bot = bot   

    @commands.hybrid_group(name="roulette", fallback = 'info', description = "Discord Roulette!")
    @commands.bot_has_permissions(send_messages = True)
    async def roulette(self, ctx):
      await ctx.send('Roulette!')
      return


    @roulette.command(name = 'select_killer', description = "Selects killer for Discord Roulette")
    @commands.guild_only()
    @commands.has_role('Playing')
    @commands.bot_has_permissions(manage_roles = True, send_messages = True)
    async def select_killer(self, ctx, user: discord.Member = None):
      roles = ctx.guild.roles
      playing = get(roles, name="Playing")
      if not user:  
        user = random.choice(list(playing.members))
      else:
        if user not in list(playing.members):
          await ctx.send(embed = error(f"{user.mention} does not have {playing.mention} role!"), ephemeral = True)
          return

      killer = get(roles, name="Killer")      
      await user.add_roles(killer)
        
      e = {'title': "Killer Selected", 
           'description': f'{user.mention} is now the killer.'}
      await ctx.send(embed = embed(e).set_thumbnail(url = 'https://i.imgur.com/WUaFVmO.png'))
      return

    @roulette.command(name = 'register', description = "Registration for Discord Roulette game")
    @commands.guild_only()
    @commands.has_role('Spectator')
    @commands.bot_has_permissions(manage_roles = True, send_messages = True)
    async def register(self, ctx):
      author = ctx.author
      roles = ctx.guild.roles
      playing = get(roles, name="Playing")
      spectator = get(roles, name="Spectator")
        
      await author.remove_roles(spectator)

      if playing not in author.roles: 
        await author.add_roles(playing)
	
      e = {'title': "__Registration Complete__", 
           'description': 'You are now playing in this round of Discord Roulette.'}
      await ctx.send(embed = embed(e))


    @roulette.command(name = 'unregister', description = "Cancels Discord Roulette registration")
    @commands.guild_only()
    @commands.has_role('Playing')
    @commands.bot_has_permissions(manage_roles = True, send_messages = True)
    async def unregister(self, ctx):
      author = ctx.author
      roles = ctx.guild.roles
      playing = get(roles, name="Playing")
      spectator = get(roles, name="Spectator")

      await author.remove_roles(playing)
      if playing not in author.roles: 
        await author.add_roles(spectator)
        
      e = {'title': "__Registration Cancelled__", 
           'description': 'You are no longer playing in this round of Discord Roulette.'}
      await ctx.send(embed = embed(e))


    @roulette.command(name = 'reset', description = "Resets server for a new round of Discord Roulette")
    @commands.guild_only()
    @commands.has_role('Playing')
    @commands.bot_has_permissions(manage_roles = True, send_messages = True)
    async def reset(self, ctx):
      roles = ctx.guild.roles
      dead = get(roles, name="Dead")
      killer = get(roles, name="Killer")
      playing = get(roles, name="Playing")
      spectator = get(roles, name="Spectator")

      for user in list(killer.members): 
        await user.remove_roles(killer)
      for user in list(playing.members):
        await user.remove_roles(playing)
        if spectator not in user.roles: 
          await user.add_roles(spectator)
      if dead in user.roles: 
        await user.remove_roles(dead)
        if spectator not in user.roles: 
          await user.add_roles(spectator)

      e = {'title': "__Game Reset__", 
           'description': 'All players are now spectators.'}
      await ctx.send(embed = embed(e))
  


    @roulette.command(name = 'shoot', description = "Load and shoot for Discord Roulette")
    @commands.guild_only()
    @commands.has_role('Playing')
    @commands.has_role('Killer')
    @commands.bot_has_permissions(manage_roles = True, send_messages = True)
    async def shoot(self, ctx, target:discord.Member, bullets:int=None):
      author = ctx.author
      roles = ctx.guild.roles
      dead = get(roles, name="Dead")
      killer = get(roles, name="Killer")
      playing = get(roles, name="Playing")
      spectator = get(roles, name="Spectator")

      if not bullets or bullets not in range(7):
        await ctx.send(embed=error('Select 1-6 bullets!'), ephemeral = True)
        return
      if playing not in target.roles:
        await ctx.send(embed=error(f"{target.mention} does not have {player.mention} role!"), ephemeral = True)
        return

      shoot_self = target.id == author.id
      bullet = random.randint(1,6)

      if bullet <= bullets:
        await target.remove_roles(playing)
        if killer in target.roles: 
          await target.remove_roles(killer)
        await target.add_roles(dead, spectator)

        if shoot_self:
          new_killer = random.choice(list(playing.members))
          await new_killer.add_roles(killer)
          e = {'title': "__You shot yourself.__", 
          	   'description': f"{new_killer.mention} is now the killer."}
          await ctx.send(embed = embed(e))
        else:  
          e = {'title': f"__{target.display_name} has been shot.__", 
          	   'description': "Select another player to shoot."}
          await ctx.send(embed = embed(e))
        return

      if shoot_self:
        e = {'title': "__You survived.__", 
          	 'description': "Load another bullet to shoot someone else."}
        await ctx.send(embed = embed(e))
      else:
        await target.add_roles(killer)
        await author.remove_roles(killer) 
        
        e = {'title': f"__{target.display_name} was not shot.__", 
          	 'description': "They are now the killer."}
        await ctx.send(embed = embed(e))
        





#add cog

async def setup(bot):
  await bot.add_cog(roulette_commands(bot))  
