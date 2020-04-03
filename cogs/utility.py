import discord
from discord.ext import commands

class UtilityCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", aliases=["latency", "pingpong", "pong"], usage="ping", help="Allows you to get the bot's current ping.", hidden=False)
    async def ping(self, ctx):
        async with ctx.channel.typing():
            before = monotonic()
            msg = await ctx.send(f"{self.bot.settings['emoji']['ping']} | **Pong! My ping is :thinking:**")
            ping = (monotonic() - before) * 1000
            await msg.edit(content=f"{self.bot.settings['emoji']['ping']} | **Pong! My ping is:** `{int(ping)}ms`")

    @commands.command(name="userinfo", aliases=["ui", "profile"], usage="userinfo [@mention/#id]", help="Allows you to get your own or another user's DEL profile information.", hidden=False)
    async def userinfo(self, ctx, *, user: discord.User = None):
        async with ctx.channel.typing():

            async def embedColour():
                global colour

                botGuildMember = await ctx.guild.fetch_member(self.bot.user.id)
                if len(str(botGuildMember.colour.value)) == 1:
                    colour = 0xFFFFFA
                else:
                    colour = botGuildMember.colour.value

                return colour

            if user == None:
                user = ctx.author

            dbUser = self.bot.db["users"].find_one({"id": str(user.id)})

            if dbUser:
                embed = discord.Embed(colour=await embedColour())

                embed.add_field(name=f"{self.bot.settings['emoji']['shadows']} Username", value=dbUser["fullUsername"])
                embed.add_field(name=f"{self.bot.settings['emoji']['id']} ID", value=dbUser["id"])
                embed.add_field(name=f"{self.bot.settings['emoji']['url']} Profile URL", value=f"{self.bot.settings['website']['url']}/users/{dbUser['id']}", inline=False)
                embed.set_thumbnail(url=f"{dbUser['avatar']['url']}.png")

                await ctx.send(embed=embed)
            else:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid user:** I could not find the user you specified in my database.")

    @commands.command(name="botinfo", aliases=["bi"], usage="botinfo <@mention/#id>", help="Allows you to get information of a bot.", hidden=False)
    async def botinfo(self, ctx, *, bot: discord.User = None):
        async with ctx.channel.typing():

            async def embedColour():
                global colour

                botGuildMember = await ctx.guild.fetch_member(self.bot.user.id)
                if len(str(botGuildMember.colour.value)) == 1:
                    colour = 0xFFFFFA
                else:
                    colour = botGuildMember.colour.value

                return colour

            if bot == None:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid argument:** You need to mention or provide an ID of a bot.")

            dbBot = self.bot.db["bots"].find_one({"id": str(bot.id)})

            if dbBot:
                botOwner = self.bot.db["users"].find_one({"id": dbBot["owner"]["id"]})

                embed = discord.Embed(colour=await embedColour())

                embed.add_field(name=f"{self.bot.settings['emoji']['shadows']} Bot Name", value=dbBot["name"])
                embed.add_field(name=f"{self.bot.settings['emoji']['id']} ID", value=dbBot["id"])
                embed.add_field(name=f"{self.bot.settings['emoji']['crown']} Developer", value=f"[{botOwner['fullUsername']}]({self.bot.settings['website']['url']}/users/{botOwner['id']})")
                embed.add_field(name=f"{self.bot.settings['emoji']['infoBook']} Library", value=dbBot["library"])
                embed.add_field(name=f"{self.bot.settings['emoji']['speech']} Prefix", value=dbBot["prefix"])
                embed.add_field(name=f"{self.bot.settings['emoji']['shield']} Server Count", value=dbBot["serverCount"])
                embed.add_field(name=f"{self.bot.settings['emoji']['url']} Library", value=f"{self.bot.settings['website']['url']}/bots/{dbBot['id']}", inline=False)
                embed.set_thumbnail(url=f"{dbBot['avatar']['url']}.png")

                await ctx.send(embed=embed)
            else:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid bot:** I could not find the bot you specified in my database.")


    @commands.command(name="token", aliases=["delapitoken", "apikey", "apitoken"], usage="token [@mention/#id]", help="Allows you to get the DELAPI token of the specified bot (provided you own it).", hidden=False)
    async def token(self, ctx, *, bot: discord.User = None):
        async with ctx.channel.typing():

            async def embedColour():
                global colour

                botGuildMember = await ctx.guild.fetch_member(self.bot.user.id)
                if len(str(botGuildMember.colour.value)) == 1:
                    colour = 0xFFFFFA
                else:
                    colour = botGuildMember.colour.value

                return colour

            if bot == None:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid argument:** You need to mention or provide an ID of a bot.")

            dbBot = self.bot.db["bots"].find_one({"id": str(bot.id)})

            if dbBot:
                if dbBot["owner"]["id"] == str(ctx.author.id):
                    embed = discord.Embed(colour=await embedColour())

                    embed.add_field(name=f"{self.bot.settings['emoji']['shadows']} Bot Name", value=dbBot["name"])
                    embed.add_field(name=f"{self.bot.settings['emoji']['id']} ID", value=dbBot["id"])
                    embed.add_field(name=f"{self.bot.settings['emoji']['cog']} Token", value=f"```{dbBot['token']}```", inline=False)
                    embed.set_thumbnail(url=f"{dbBot['avatar']['url']}.png")

                    await ctx.author.send(embed=embed)
                    await ctx.send(f"{self.bot.settings['formats']['success']} **Success:** The specified bot's DELAPI token has been sent to you via DM.")
                else:
                    await ctx.send(f"{self.bot.settings['formats']['noPerms']} **Invalid permission(s):** You need to be the owner of the specified bot to access it's token.")
            else:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid bot:** I could not find the bot you specified in my database.")

def setup(bot):
    bot.add_cog(UtilityCog(bot))

