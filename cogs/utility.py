# Discord Extreme List - Discord's unbiased list.

# Copyright (C) 2020 Cairo Mitchell-Acason

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from time import monotonic
import datetime

import discord
from discord.ext import commands

from ext.checks import *


class UtilityCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def embed_colour(self, ctx):
        global colour

        bot_guild_member = await ctx.guild.fetch_member(self.bot.user.id)
        if len(str(bot_guild_member.colour.value)) == 1:
            colour = 0xFFFFFA
        else:
            colour = bot_guild_member.colour.value

        return colour

    @commands.command(name="ping", aliases=["latency", "pingpong", "pong"], usage="ping")
    async def ping(self, ctx):
        """
        Allows you to get the bot's current ping.
        """
        before = monotonic()
        await ctx.trigger_typing()
        ping = (monotonic() - before) * 1000
        await ctx.send(f"{self.bot.settings['emoji']['ping']} | **Pong! My ping is:** `{int(ping)}ms`")

    @commands.command(name="userinfo", aliases=["ui", "profile"], usage="userinfo <user>")
    async def user_info(self, ctx, *, user: discord.User = None):
        """
        Allows you to get your own or another user's DEL profile information.
        """
        async with ctx.channel.typing():
            if user is None:
                user = ctx.author

            db_user = await self.bot.db.users.find_one({"_id": str(user.id)})
            if not db_user:
                raise NoSomething(user)

            embed = discord.Embed(colour=await self.embed_colour(ctx))

            embed.add_field(name=f"{self.bot.settings['emoji']['shadows']} Username", value=db_user["fullUsername"])
            embed.add_field(name=f"{self.bot.settings['emoji']['id']} ID", value=db_user["_id"])
            embed.add_field(name=f"{self.bot.settings['emoji']['url']} Profile URL",
                            value=f"{self.bot.settings['website']['url']}/users/{db_user['_id']}", inline=False)
            embed.set_thumbnail(url=f"{db_user['avatar']['url']}")

            await ctx.send(embed=embed)

    @commands.command(name="botinfo", aliases=["bi"], usage="botinfo <bot>")
    async def robot_info(self, ctx, *, bot: str):
        """
        Allows you to get information of a bot.
        """
        if not bot.isdigit():
            return await ctx.send("You provided wrong id.")

        async with ctx.channel.typing():

            db_bot = await self.bot.db.bots.find_one({"_id": str(bot.id)})

            if not db_bot:
                raise NoSomething(bot)

            bot_owner = await self.bot.db.users.find_one({"_id": db_bot["owner"]["id"]})

            embed = discord.Embed(colour=await self.embed_colour(ctx))

            embed.add_field(name=f"{self.bot.settings['emoji']['shadows']} Bot Name", value=db_bot["name"])
            embed.add_field(name=f"{self.bot.settings['emoji']['id']} ID", value=db_bot["_id"])
            embed.add_field(name=f"{self.bot.settings['emoji']['crown']} Developer",
                            value=f"[{bot_owner['fullUsername']}]({self.bot.settings['website']['url']}/users/{bot_owner['_id']})")
            embed.add_field(name=f"{self.bot.settings['emoji']['infoBook']} Library", value=db_bot["library"])
            embed.add_field(name=f"{self.bot.settings['emoji']['speech']} Prefix", value=db_bot["prefix"])
            embed.add_field(name=f"{self.bot.settings['emoji']['shield']} Server Count",
                            value=db_bot["serverCount"])
            embed.add_field(name=f"{self.bot.settings['emoji']['url']} Listing URL",
                            value=f"{self.bot.settings['website']['url']}/bots/{db_bot['_id']}", inline=False)
            embed.set_thumbnail(url=f"{db_bot['avatar']['url']}")

            await ctx.send(embed=embed)

    @commands.command(name="token", aliases=["delapitoken", "apikey", "apitoken"], usage="token <bot>")
    async def token(self, ctx, *, bot: discord.User):
        """
        Allows you to get the DELAPI token of the specified bot (provided you own it).
        """
        async with ctx.channel.typing():
            db_bot = await self.bot.db.bots.find_one({"_id": str(bot.id)})

            if not db_bot:
                raise NoSomething(bot)

            if db_bot["owner"]["id"] == str(ctx.author.id):
                embed = discord.Embed(colour=await self.embed_colour(ctx))

                embed.add_field(name=f"{self.bot.settings['emoji']['shadows']} Bot Name", value=db_bot["name"])
                embed.add_field(name=f"{self.bot.settings['emoji']['id']} ID", value=db_bot["_id"])
                embed.add_field(name=f"{self.bot.settings['emoji']['cog']} Token", value=f"```{db_bot['token']}```",
                                inline=False)
                embed.set_thumbnail(url=f"{db_bot['avatar']['url']}.png")

                try:
                    await ctx.author.send(embed=embed)
                    await ctx.send(
                        f"{self.bot.settings['formats']['success']} {bot}'s token has been dm'ed to you")
                except:
                    await ctx.send("Your dms appear to be closed")
            else:
                await ctx.send(
                    f"{self.bot.settings['formats']['noPerms']} **Invalid permission(s):** You need to be the "
                    f"owner of the specified bot to access it's token.")

    @commands.command(name="admintoken", usage="admintoken")
    @commands.is_owner()
    async def admin_token(self, ctx):
        """
        Allows you to get your temporary DELADMIN access token (admins only).
        """
        async with ctx.channel.typing():
            db_user = await self.bot.db.users.find_one({"_id": str(ctx.author.id)})

            if not db_user:
                raise NoSomething(ctx.author)

            token = await self.bot.db.adminTokens.find_one({"_id": str(ctx.author.id)})

            if token:
                embed = discord.Embed(colour=await self.embed_colour(ctx))

                embed.add_field(name=f"{self.bot.settings['emoji']['clock']} Valid From",
                                value=datetime.datetime.utcfromtimestamp(token["lastUpdate"] / 1000).strftime(
                                    f"%I:%M%p - %a, %d %b %Y (GMT)"))
                embed.add_field(name=f"{self.bot.settings['emoji']['timer']} Valid Until",
                                value=datetime.datetime.utcfromtimestamp(token["validUntil"] / 1000).strftime(
                                    f"%I:%M%p - %a, %d %b %Y (GMT)"))
                embed.add_field(name=f"{self.bot.settings['emoji']['cog']} Token", value=f"```{token['token']}```",
                                inline=False)
                embed.set_thumbnail(url=ctx.author.avatar_url)

                try:
                    await ctx.author.send(embed=embed)
                    await ctx.send(
                        f"{self.bot.settings['formats']['success']} Your current admin token has been dmed to you.")
                except:
                    await ctx.send("Your dms appear to be closed")
            else:
                await ctx.send(
                    f"{self.bot.settings['formats']['noPerms']} **Invalid permission(s):** You need to be a "
                    f"DEL admin to obtain one of these.")

    @commands.command(name="cssreset", aliases=["resetcss", "ohshitohfuck"])
    async def css_reset(self, ctx):
        """
        Allows you to reset your custom css if you've broken something
        """
        async with ctx.channel.typing():
            db_user = await self.bot.db.users.find_one({"_id": str(ctx.author.id)})

            if not db_user:
                raise NoSomething(ctx.author)

            if db_user:
                await self.bot.db.users.update_one({"_id": str(ctx.author.id)}, {
                    "$set": {
                        "profile.css": ""
                    }
                })

                return await ctx.send(
                    f"{self.bot.settings['formats']['success']} **Success:** Your custom css was reset.")
            else:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Unknown account:** You need to have authenticated on "
                    f"our website before to use this command.")


def setup(bot):
    bot.add_cog(UtilityCog(bot))
