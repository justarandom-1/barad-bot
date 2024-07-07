from main import *

class error_handler(commands.Cog):

  def __init__(self, bot): 
    self.bot = bot

  @commands.Cog.listener()
  async def on_command_error(self, ctx: commands.Context, error):
    print(ctx.message.content)
    print(error)
    
    e = {'title': "__Error__",
         'description': error}
    if not ctx.message.content.startswith('[]'):
      try:
        await ctx.send(embed = embed(e), ephemeral = True)
      except Exception as e: 
        print(e)
        
    return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(error_handler(bot))