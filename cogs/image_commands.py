from main import *

#lists and set information

individual_clones = pd.read_csv("resources/individual_clones.csv")
special_clones = pd.read_csv("resources/special_clones.csv")
tragedy = pd.read_csv("resources/tragedy.csv")
clone_types = pd.read_csv("resources/clone_types.csv")
bad_apple_frames = open("resources/bad_apple_frames.txt", "r").read().split("\n")
apple_template = "https://media.discordapp.net/attachments/858094390663839754/{}/image0.gif"


async def generate_clone(ct_number):
  if random.randint(1, 7) == 1:
    clone = special_clones.sample(1, weights = special_clones.Weight).iloc[0]
  else:
    clone = clone_types.sample(1, weights = clone_types.Weight).iloc[0]
  return embed(title = str(clone['Title']).format(ct=ct_number), image = clone.Img)


async def get_clone(ct_number):
  if not ct_number:
    if random.randint(1, 9) == 1:
      clone = individual_clones.sample(1).iloc[0]
      return embed(title = clone.Name, image = clone.Img)
    ct_number = str(random.randint(100000001, 200000000))[1:]
    ct_number = random.choices([f"{ct_number[:4]}/{ct_number[4:]}", 
                                f"{ct_number[:2]}-{ct_number[:4]}", 
                                ct_number[:3], 
                                f"{ct_number[:2]}/{ct_number[2:4]}-{ct_number[4:]}", 
                                ct_number[:4]], weights = tuple([2] * 3 + [1, 30]))[0]

  try:
    clone = individual_clones.loc[individual_clones.Num == ct_number].iloc[0]
    return embed(title = clone.Name, image = clone.Img)
  except:
    pass

  return await generate_clone(ct_number)


#cog:
class image_commands(commands.Cog):    

  #set self
  def __init__(self, bot): 
    self.bot = bot  


  @commands.hybrid_command(name="yuh", description = "yuh")
  @commands.bot_has_permissions(send_messages = True)
  async def yuh(self, ctx):
    await ctx.send(embed = embed(image = "https://i.imgur.com/EHPtROp.png"))


  @commands.hybrid_group(name="lucas", fallback = 'yuh', description = "yuh")
  @commands.bot_has_permissions(send_messages = True)
  async def lucas_yuh(self, ctx):
    await ctx.send(embed = embed(image = "https://i.imgur.com/3FwfUqE.png"))


  @commands.hybrid_command(name="we_do_a_little_trolling", 
                           description = "We do quite a considerable amount of mental trickery")
  @commands.bot_has_permissions(send_messages = True)
  async def we_do_a_little_trolling(self, ctx):
    await ctx.send(embed = embed(image = "https://i.imgur.com/UCmx4S0.gif"))


  @commands.hybrid_group(name="bad", fallback = 'apple', description = "Guess what this does... (note: very laggy)")
  @commands.bot_has_permissions(send_messages = True)
  async def bad_apple(self, ctx):
    message = await ctx.send(embed = loading)
    
    frames = [embed(image = apple_template.format(bad_apple_frames[i])) for i in range(22)]
    for i in range(22): await message.edit(embed = frames[i]); await asyncio.sleep(9.9)  

    await delete(message, ctx.guild)

  @commands.hybrid_command(name="tomato", description = "A Glorious Tomato Warrior")
  @commands.bot_has_permissions(send_messages = True)
  async def tomato(self, ctx):
    await ctx.send(embed = embed(title = "A Glorious Tomato Warrior").set_thumbnail(url = "https://i.imgur.com/JuT4Ck4.png")) 

  @commands.hybrid_command(name="potato", description = "A Grand Potato Soldier")
  @commands.bot_has_permissions(send_messages = True)
  async def potato(self, ctx):
    await ctx.send(embed = embed(title = "A Grand Potato Soldier").set_thumbnail(url = "https://i.imgur.com/IZFcYCv.png"))  

  @commands.hybrid_group(name="marauder", fallback = 'megatron',   description = "Am I truly to blame here?")
  @commands.bot_has_permissions(send_messages = True)
  async def marauder_megatron(self, ctx):
    e = {'title': "__It's a shame.__", 
         'description': "I would have at least hoped that my final battle would have been with a worthy opponent."}
    await ctx.send(embed = embed(e, "https://i.imgur.com/iUPQDXt.png"))

  #star wars commands  

  @commands.hybrid_command(name="senate", description = "I am the Senate!")
  @commands.bot_has_permissions(send_messages = True)
  async def senate(self, ctx):
    await ctx.send(embed = embed(title = "I am the senate!",
                                 image = "https://i.imgur.com/WDSHoJU.png"))
    
    def check(message):
      return ("not yet" in message.content.lower() or "not just" in message.content.lower())\
      and message.channel.id == ctx.channel.id
    try: message = await self.bot.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
      return
    else:
      e = {}
      if "not just" in message.content.lower(): 
        e = {'title': "__That I have to revolt.__"}
      await message.reply(embed = embed(e, "https://i.imgur.com/WGKEWAh.gif"))



  @commands.hybrid_group(name="high", fallback = 'ground',  description = "It's over Anakin!")
  @commands.bot_has_permissions(send_messages = True)
  async def high_ground(self, ctx):
    await ctx.send(embed=embed(title = "I have the high ground!",
                               image = "https://i.imgur.com/WHuaLaJ.png"))


  @commands.hybrid_group(name="darth", fallback = 'plagueis',  description = "Uncertainty is the first step toward self-determination.")
  @commands.bot_has_permissions(send_messages = True)
  async def darth(self, ctx):
    await ctx.send(embed = embed(title = 'Did you ever hear the Tragedy of Darth Plagueis the Wise?',
                                             image = "https://i.imgur.com/LbT4Mih.png"))
    for i in range(tragedy.shape[0]):
      index, response, t, desc, img = tuple(tragedy.iloc[i])
      def check(message):
        return response in message.content.lower().translate(str.maketrans('', '', string.punctuation))\
        and message.channel.id == ctx.channel.id
      try: 
        message = await self.bot.wait_for('message', timeout=30.0, check=check)
      except asyncio.TimeoutError:
        return
      else:
        e = {'title': f'__{t}__', "description": desc}
        await message.reply(embed = embed(e, img))
  
  @darth.command(name='maul',  pass_context=True, description = "God Hammer be mind")
  @commands.bot_has_permissions(send_messages = True)
  async def darth_maul(self, ctx):
    e = {'title': "__You have been well trained, my young apprentice.__", 
         'description': "They will be no match for you."}
    await ctx.send(embed = embed(e, "https://i.imgur.com/4apqGir.png"))


  @commands.hybrid_command(name="democracy", description = "I love democracy.")
  @commands.bot_has_permissions(send_messages = True)
  async def democracy(self, ctx):
    e = {'title': "__I love democracy.__", 'description': "I love the republic."}
    await ctx.send(embed = embed(e, "https://i.imgur.com/4FRQnch.png"))

  @commands.hybrid_group(name="hello", fallback = 'there',  description = "General Kenobi!")
  @commands.bot_has_permissions(send_messages = True)
  async def hello_there(self, ctx):
    await ctx.send(embed = embed(title = 'Hello there!', image = "https://i.imgur.com/vM7yx5L.png"))

  @commands.hybrid_group(name="unlimited", fallback = 'power', description = "Get to say with you that part forever!")
  @commands.bot_has_permissions(send_messages = True)
  async def unlimited_power(self, ctx):
    await ctx.send(embed = embed(title = 'Power! Unlimited power!', image = "https://i.imgur.com/5MR6yb3.png"))


  @commands.hybrid_command(name="sheev", description = "The knowledge of the dark of the study hopeless, in the fire of water...")
  @commands.bot_has_permissions(send_messages = True)
  async def sheev(self, ctx):
    await ctx.send(embed = embed().set_image(url="https://i.imgur.com/ALzsuYN.png"))

  @commands.hybrid_group(name="master", fallback = 'windu', description = "Adult, you were caught.")
  @commands.bot_has_permissions(send_messages = True)
  async def master_windu(self, ctx):
    await ctx.send(embed = embed(title = "You're under arrest!", image = "https://i.imgur.com/AT058RA.png"))

  @commands.hybrid_command(name="anakin", description = "We will watch your career with great interest.")
  @commands.bot_has_permissions(send_messages = True)
  async def anakin(self, ctx):
    e = {'title': "__Anakin. I told you it would come to this.__", 
         'description': "I was right! The Jedi are taking over!"}
    await ctx.send(embed = embed(e, "https://i.imgur.com/5o6CohO.png"))


  @commands.hybrid_command(name="yoda", description = "Vanquish Is, you surrendered.")
  @commands.bot_has_permissions(send_messages = True)
  async def yoda(self, ctx):
    e = {'title': "__Master Yoda.__", 
         'description': "You survived."}
    await ctx.send(embed = embed(e, "https://i.imgur.com/onY6vSZ.png"))


  #clone generator commands
  @commands.hybrid_group(name="clone", fallback = 'generate',   description = "Clone generator!")
  @commands.bot_has_permissions(send_messages = True)
  async def clone_generate(self,ctx, *, 
                           ct_number: str = commands.parameter(default = None, 
                                                               description = "Custom Designation")):      
    me = ctx.guild.me
    clones = []
    titles = []

    if ct_number:
      if any([c not in "0123456789-/" for c in ct_number]):
        error = {title: "Error", description: "Invalid CT-number!"}
        await ctx.send(embed = embed(error), ephemeral=True)
        return

    clone = await get_clone(ct_number)
    reply = await ctx.send(embed = clone)

    if not isinstance(ctx.channel, discord.TextChannel) and not me.guild_permissions.add_reactions:
      return

    clones.append(clone)
    titles.append(clone.title)
    index = 0

    await reply.add_reaction("⬅️")
    await reply.add_reaction("➡️")

    while True:
      def check(reaction, user):
        return reaction.message == reply and user.id == ctx.author.id\
        and (str(reaction.emoji) == "➡️" or (index > 0 and str(reaction.emoji) == "⬅️"))
      try: reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
      except asyncio.TimeoutError: 
        try: 
          await reply.remove_reaction("➡️", me)
          await reply.remove_reaction("⬅️", me)
          return
        except:
          return
      else:
        try: 
          await reply.remove_reaction(str(reaction.emoji), user);
        except:
          pass
        if str(reaction.emoji) == "⬅️":
          index -= 1
        else: 
          index += 1
        
        if index == len(clones):
          clone = await get_clone(None)
          while clone.title in titles: clone = await get_clone(None)
          clones.append(clone); titles.append(clone.title)
        
        await reply.edit(embed = clones[index])

#add cog

async def setup(bot):
  await bot.add_cog(image_commands(bot))  