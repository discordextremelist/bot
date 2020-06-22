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

from ext.checks import mod_check, NoSomething


class WebModeration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="approve", aliases=["approvebot"])
    @mod_check()
    async def approve_bot(self, ctx, bot: discord.User):
        """
        Allows you to approve the bot on the website.
        """
        async with ctx.channel.typing():
            db_user = await self.bot.db.users.find_one({"_id": str(ctx.author.id)})

            if bot is None or not bot.bot:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Invalid argument:** You need to mention or provide an "
                    f"ID of a bot.")

            db_bot = await self.bot.db.bots.find_one({"_id": str(bot.id)})
            if not db_bot:
                raise NoSomething(bot)

            if db_bot["status"]["approved"]:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Already approved:** You cannot approve a bot that "
                    f"is already approved!")

            await self.bot.db.bots.update_one({"_id": str(bot.id)}, {
                "$set": {
                    "status.approved": True
                }
            })

            await self.bot.db.users.update_one({"_id": str(ctx.author.id)}, {
                "$set": {
                    "staffTracking.handledBots.allTime.total": db_user.staffTracking.handledBots.allTime.total+1,
                    "staffTracking.handledBots.allTime.approved": db_user.staffTracking.handledBots.allTime.approved+1,
                    "staffTracking.handledBots.thisWeek.total": db_user.staffTracking.handledBots.thisWeek.total+1,
                    "staffTracking.handledBots.thisWeek.approved": db_user.staffTracking.handledBots.thisWeek.approved+1
                }
            })

            await ctx.send(
                f"{self.bot.settings['formats']['error']} **Success:** {db_bot.name} has been approved "
                f"successfully!")

            site = ctx.bot.settings['website']['url']
            await ctx.bot.get_channel(603800402013585408).send(
                f"<:check:587490138129563649> {ctx.author} ({ctx.author.id}) approved bot {bot} ({bot.id})\n{site}/bots/{bot.id}")

    @commands.command(name="deny", aliases=["denybot"])
    @mod_check()
    async def approve_bot(self, ctx, bot: discord.User, *, reason):
        """
        Allows you to decline a bot on the website.
        """
        async with ctx.channel.typing():
            db_user = await self.bot.db.users.find_one({"_id": str(ctx.author.id)})

            if bot is None or not bot.bot:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Invalid argument:** You need to mention or provide an "
                    f"ID of a bot.")

            db_bot = await self.bot.db.bots.find_one({"_id": str(bot.id)})
            if not db_bot:
                raise NoSomething(bot)

            if db_bot["status"]["approved"]:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Already approved:** You cannot decline a bot that "
                    f"is already approved!")

            await self.bot.db.bots.update_one({"_id": str(bot.id)}, {
                "$set": {
                    "status.approved": True
                }
            })

            await self.bot.db.users.update_one({"_id": str(ctx.author.id)}, {
                "$set": {
                    "staffTracking.handledBots.allTime.total": db_user.staffTracking.handledBots.allTime.total + 1,
                    "staffTracking.handledBots.allTime.declined": db_user.staffTracking.handledBots.allTime.declined + 1,
                    "staffTracking.handledBots.thisWeek.total": db_user.staffTracking.handledBots.thisWeek.total + 1,
                    "staffTracking.handledBots.thisWeek.declined": db_user.staffTracking.handledBots.thisWeek.declined + 1
                }
            })

            await ctx.send(
                f"{self.bot.settings['formats']['error']} **Success:** {db_bot.name} has been declined "
                f"successfully!")
            await ctx.bot.get_channel(603800402013585408).send(f"<:cross:587490138129432596> {ctx.author} ({ctx.author.id}) declined bot {bot} ({bot.id})\n[ Reason ] `{reason}`")



def setup(bot):
    bot.add_cog(WebModeration(bot))
