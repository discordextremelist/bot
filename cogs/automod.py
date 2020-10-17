import discord

from discord.ext import commands

class CooldownByContent(commands.CooldownMapping):
    def _bucket_key(ctx, message):
        return (message.channel.id, message.content)
      
class Automod(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.messages_cooldown = CooldownByContent.from_cooldown(15, 17.0, commands.BucketType.member)
    
def setup(bot):
  bot.add_cog(Automod(bot))
