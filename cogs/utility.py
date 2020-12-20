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

import discord
from discord.ext import commands
from ext.checks import *

import datetime
from time import monotonic
from .types import globalTypes, botTypes, userTypes


class UtilityCog(commands.Cog, name="Utility"):

    def __init__(self, bot):
        self.bot = bot
        self.help_icon = f"{self.bot.settings['emoji']['toolbox']}"

    async def embed_colour(self, ctx):
        global colour

        bot_guild_member = await ctx.guild.fetch_member(self.bot.user.id)
        if len(str(bot_guild_member.colour.value)) == 1:
            colour = 0xFFFFFA
        else:
            colour = bot_guild_member.colour.value

        return colour

    @commands.command(name="ping", aliases=["latency", "pingpong", "pong"], usage="ping",
                      description="Allows you to get the bots' current ping.")
    async def ping(self, ctx):
        """
        Allows you to get the bots' current ping.
        """
        before = monotonic()
        await ctx.trigger_typing()
        ping = (monotonic() - before) * 1000
        await ctx.send(f"{self.bot.settings['emoji']['ping']} | **Pong! My ping is:** `{int(ping)}ms`")

    # noinspection DuplicatedCode
    @commands.command(name="userinfo", aliases=["ui", "profile"], usage="userinfo <user>",
                      description="Allows you to get your own or another user's DEL profile information.")
    @commands.guild_only()
    async def user_info(self, ctx, *, user: discord.User = None):
        """
        Allows you to get your own or another user's DEL profile information.
        """
        if user is None:
            user = ctx.author

        db_user: userTypes.DelUser = await self.bot.db.users.find_one({"_id": str(user.id)})
        if not db_user:
            raise NoSomething(user)

        embed = discord.Embed(colour=await self.embed_colour(ctx))

        acknowledgements = []
        badges = []

        if db_user["rank"]["admin"]:
            acknowledgements.append("Website Administrator")
            badges.append(self.bot.settings["emoji"]["crown"])

        if db_user["rank"]["assistant"]:
            acknowledgements.append("Website Assistant")
            badges.append(self.bot.settings["emoji"]["assistant"])

        if db_user["rank"]["mod"]:
            acknowledgements.append("Website Moderator")
            badges.append(self.bot.settings["emoji"]["hammer"])

        if db_user["rank"]["premium"]:
            acknowledgements.append("Donator")
            badges.append(self.bot.settings["emoji"]["heart"])

        if db_user["rank"]["tester"]:
            acknowledgements.append("Tester")
            badges.append(self.bot.settings["emoji"]["tube"])

        if db_user["rank"]["translator"]:
            acknowledgements.append("Translator")
            badges.append(self.bot.settings["emoji"]["url"])

        if db_user["rank"]["covid"]:
            acknowledgements.append("COVID-19 Donator")
            badges.append(self.bot.settings["emoji"]["shield"])

        embed.add_field(name=f"{self.bot.settings['emoji']['shadows']} Username", value=f"{db_user['fullUsername']}"
                                                                                        f" {' '.join(badges)}")
        embed.add_field(name=f"{self.bot.settings['emoji']['id']} ID", value=db_user["_id"])

        if acknowledgements != []:
            embed.add_field(name=f"{self.bot.settings['emoji']['crown']} Acknowledgements",
                            value="\n".join(acknowledgements), inline=False)

        embed.add_field(name=f"{self.bot.settings['emoji']['url']} Profile URL",
                        value=f"{self.bot.settings['website']['url']}/users/{db_user['_id']}", inline=False)
        embed.set_thumbnail(url=f"{db_user['avatar']['url']}")

        await ctx.send(embed=embed)

    # noinspection DuplicatedCode
    @commands.command(name="botinfo", aliases=["bi"], usage="botinfo <bot>",
                      description="Allows you to get information of a bot.")
    @commands.guild_only()
    async def robot_info(self, ctx, *, bot: discord.User):
        """
        Allows you to get information of a bot.
        """
        if not bot.bot:
            return await ctx.send("That's no bot")

        db_bot: botTypes.DelBot = await self.bot.db.bots.find_one({"_id": str(bot.id)})

        if not db_bot:
            raise NoSomething(bot)

        bot_owner: userTypes.DelUser = await self.bot.db.users.find_one({"_id": db_bot["owner"]["id"]})

        embed = discord.Embed(colour=await self.embed_colour(ctx))

        embed.add_field(name=f"{self.bot.settings['emoji']['shadows']} Bot Name", value=db_bot["name"])
        embed.add_field(name=f"{self.bot.settings['emoji']['id']} ID", value=db_bot["_id"])
        embed.add_field(name=f"{self.bot.settings['emoji']['crown']} Developer",
                        value=f"[{bot_owner['fullUsername']}]({self.bot.settings['website']['url']}/users/{bot_owner['_id']})")
        embed.add_field(name=f"{self.bot.settings['emoji']['infoBook']} Library", value=db_bot["library"])
        embed.add_field(name=f"{self.bot.settings['emoji']['speech']} Prefix", value=db_bot["prefix"])
        embed.add_field(name=f"{self.bot.settings['emoji']['shield']} Server Count",
                        value=str(db_bot["serverCount"]))
        embed.add_field(name=f"{self.bot.settings['emoji']['url']} Listing URL",
                        value=f"{self.bot.settings['website']['url']}/bots/{db_bot['_id']}", inline=False)
        embed.set_thumbnail(url=f"{db_bot['avatar']['url']}")

        await ctx.send(embed=embed)

    @commands.command(name="token", aliases=["delapitoken", "apikey", "apitoken"], usage="token <bot>",
                      description="Allows you to get the DELAPI token of the specified bot (provided you own it).")
    @commands.guild_only()
    async def token(self, ctx, *, bot: discord.User):
        """
        Allows you to get the DELAPI token of the specified bot (provided you own it).
        """
        db_bot: botTypes.DelBot = await self.bot.db.bots.find_one({"_id": str(bot.id)})

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

    @commands.command(name="cssreset", aliases=["resetcss", "ohshitohfuck"],
                      description="Allows you to reset your 'Custom CSS' if you've broken something.")
    @commands.guild_only()
    async def css_reset(self, ctx):
        """
        Allows you to reset your 'Custom CSS' if you've broken something.
        """
        db_user: userTypes.DelUser = await self.bot.db.users.find_one({"_id": str(ctx.author.id)})

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

    @commands.command(name="showbots", aliases=["bl", "hasbots", "hasbot", "bots"], usage="showbots <user>",
                      description="Allows you to view the bots a specified user has.")
    @commands.guild_only()
    async def show_bots(self, ctx, *, user: discord.User = None):
        """
        Allows you to view the bots a specified user has.
        """
        user = user or ctx.author

        db_bots = self.bot.db.bots.find({"owner": {"id": str(user.id)}})

        if user.bot:
            return await ctx.send(
                f"{self.bot.settings['formats']['error']} **Bots can't own bots:** Bots can't make bots... "
                f"AI robots please don't kill me...")

        formatted_bots = []
        async for db_bot in db_bots:
            db_bot: botTypes.DelBot
            formatted_bots.append(
                f"• [{db_bot['name']}]({self.bot.settings['website']['url']}/bots/{db_bot['_id']}) "
                f"(`{db_bot['_id']}`)")

        if not formatted_bots:
            return await ctx.send(
                f"{self.bot.settings['formats']['error']} **No bots:** This user has no bots listed.")

        embed = discord.Embed(colour=await self.embed_colour(ctx))
        embed.add_field(name=f"{self.bot.settings['emoji']['robot']} {str(user)}'s Bot(s)",
                        value="\n".join(formatted_bots), inline=False)
        embed.set_thumbnail(url=f"{user.avatar_url}")

        await ctx.send(embed=embed)

    @commands.command(name="subscribe", aliases=["unsubscribe", "unsub", "sub"], usage="subscribe",
                      description="Allows you to subscribe or unsubscribe from @Subscribers pings.")
    @commands.guild_only()
    async def subscribe(self, ctx):
        """
        Allows you to subscribe or unsubscribe from @Subscribers pings.
        """
        guild = self.bot.get_guild(int(self.bot.settings["guilds"]["main"]))
        subscribe_role = guild.get_role(int(self.bot.settings["roles"]["subscribers"]))

        if subscribe_role not in ctx.author.roles:
            await ctx.author.add_roles(subscribe_role, reason="User has subscribed.")
            await ctx.send(
                f"{self.bot.settings['formats']['success']} You have been subscribed to news pings.")
        else:
            await ctx.author.remove_roles(subscribe_role, reason="User has un-subscribed.")
            await ctx.send(
                f"{self.bot.settings['formats']['success']} You have un-subscribed from news pings.")


def setup(bot):
    bot.add_cog(UtilityCog(bot))
