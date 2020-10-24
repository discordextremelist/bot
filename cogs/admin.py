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

import datetime

import discord
from discord.ext import commands

from ext.checks import NoSomething
from .types import userTypes, globalTypes


class AdminCog(commands.Cog, name="Admin"):

    def __init__(self, bot):
        self.bot = bot
        self.help_icon = f"{self.bot.settings['emoji']['coder']}"

    @commands.command(name="admintoken", usage="admintoken",
                      description="Allows you to get your temporary DELADMIN access token.")
    async def admin_token(self, ctx):
        """
        Allows you to get your temporary DELADMIN access token.
        """
        async with ctx.channel.typing():
            db_user: userTypes.DelUser = await self.bot.db.users.find_one({"_id": str(ctx.author.id)})

            if not db_user:
                raise NoSomething(ctx.author)

            token: globalTypes.DelAdminToken = await self.bot.db.adminTokens.find_one({"_id": str(ctx.author.id)})

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


def setup(bot):
    bot.add_cog(AdminCog(bot))