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


class WebModeration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="approve", aliases=["approvebot"], usage="approve <@mention/#id>",
                      help="Allows you to approve the bot on the website.", hidden=False)
    async def approve_bot(self, ctx, *, bot: discord.User = None):
        async with ctx.channel.typing():
            db_user = await self.bot.db.users.find_one({"_id": str(ctx.author.id)})

            if db_user is None:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Permission error:** You need to be a Website Moderator "
                    f"to use this command.")
            elif not db_user["rank"]["mod"]:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Permission error:** You need to be a Website Moderator "
                    f"to use this command.")

            if bot is None:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Invalid argument:** You need to mention or provide an "
                    f"ID of a bot.")

            db_bot = await self.bot.db.bots.find_one({"_id": str(bot.id)})

            if db_bot:
                if db_bot["status"]["approved"]:
                    return await ctx.send(
                        f"{self.bot.settings['formats']['error']} **Already approved:** You cannot approve a bot that "
                        f"is already approved!")
                else:
                    await self.bot.db.bots.update_one({"_id": str(bot.id)}, {
                        "$set": {
                            "status.approved": True
                        }
                    })

                    db_user.staffTracking.handledBots.allTime.total += 1
                    db_user.staffTracking.handledBots.allTime.approved += 1
                    db_user.staffTracking.handledBots.thisWeek.total += 1
                    db_user.staffTracking.handledBots.thisWeek.approved += 1

                    await self.bot.db.users.update_one({"_id": str(ctx.author.id)}, {
                        "$set": {
                            "staffTracking.handledBots.allTime.total": db_user.staffTracking.handledBots.allTime.total,
                            "staffTracking.handledBots.allTime.approved": db_user.staffTracking.handledBots.allTime.approved,
                            "staffTracking.handledBots.thisWeek.total": db_user.staffTracking.handledBots.thisWeek.total,
                            "staffTracking.handledBots.thisWeek.approved": db_user.staffTracking.handledBots.thisWeek.approved
                        }
                    })

                    return await ctx.send(
                        f"{self.bot.settings['formats']['error']} **Success:** {db_bot.name} has been approved "
                        f"successfully!")

            else:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Invalid bot:** I could not find the bot you specified "
                    f"in my database.")


def setup(bot):
    bot.add_cog(WebModeration(bot))
