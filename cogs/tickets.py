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
from ext.checks import mod_check

import traceback
import snowflake
import typing
from io import BytesIO

from .types import ticketTypes


class TicketCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.generator = snowflake.Generator()
        self.closed = 0xdd2e44
        self.awaiting_response = 0x77ff77
        self.awaiting_fixes = 0xf4dd1a

    async def snowflake_generate(self):
        """
        Generates a snowflake ID and checks to ensure it is not a duplicate.
        """
        while True:
            generated = self.generator.generate()
            check_db: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({"_id": str(generated)})

            if not check_db:
                return generated

    @commands.command(name="open-ticket", aliases=["new-ticket", "nt", "ot", "request-changes", "rc", "create-ticket",
                                                   "open", "create"])
    @commands.guild_only()
    @mod_check()
    async def open_ticket(self, ctx, bot: typing.Union[discord.User, str]):
        
        if isinstance(bot, discord.User):
            pass
        elif isinstance(bot, str):
            if bot.isdigit():
                try:
                    bot = await ctx.bot.fetch_user(bot)
                except Exception as e:
                    return await ctx.send(f"{self.bot.settings['formats']['error']} **An error occurred:**\n```py\n{e}```")
            elif not bot.isdigit():
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Unknown bot:** We could not find a bot with the arguments you provided - Try using an ID so I can fetch it?")
                                           
        if not bot.bot:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid bot:** {bot} is not a bot.")

        for channel in ctx.guild.channels:
            if channel.name == bot.name.lower():
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Duplicated channel:** there is "
                                      f"already a channel for this bot.")

        try:
            bot_db = await ctx.bot.db.bots.find_one({
                "_id": str(bot.id)
            })

            ticket_id = await self.snowflake_generate()

            category = ctx.guild.get_channel(int(self.bot.settings["channels"]["ticketCategory"]))

            owner = ctx.guild.get_member(int(bot_db["owner"]["id"]))
            mods = ctx.guild.get_role(int(self.bot.settings["roles"]["mod"]))
            serverbots = ctx.guild.get_role(int(self.bot.settings['roles']['botpower']))
            
            if owner is None:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Owner Missing:** The bot owner is not in the server!")

            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                owner: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                mods: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                serverbots: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            channel = await category.create_text_channel(name=bot.name.lower(), overwrites=overwrites,
                                                         reason=f"Approval feedback channel - {ctx.author.id}",
                                                         topic=f"{self.bot.settings['website']['url']}/bots/{bot.id}")

            embed = discord.Embed(colour=self.awaiting_response,
                                  description="Hello, whilst reviewing your bot we found some issues, please refer to "
                                              "the message(s) the staff member has sent below.")

            embed.set_author(name=f"Approval Feedback - {ticket_id} [AWAITING RESPONSE]",
                             icon_url=self.bot.settings["images"]["awaiting_response"])

            embed.set_footer(text=f"{str(bot)} ({bot.id})", icon_url=str(bot.avatar_url))

            message = await channel.send(content=owner.mention, embed=embed,
                                         allowed_mentions=discord.AllowedMentions(users=True))

            await message.pin()
            await ctx.send(f"{self.bot.settings['formats']['success']} **Ticket created:** Successfully created "
                           f"ticket - <#{channel.id}>")

            embed2 = discord.Embed(color=self.awaiting_response)

            embed2.set_author(name=f"Approval Feedback - {ticket_id} [AWAITING RESPONSE]",
                              icon_url=self.bot.settings["images"]["awaiting_response"])

            embed2.set_footer(text=f"{str(bot)} ({bot.id})", icon_url=str(bot.avatar_url))

            embed2.add_field(name="Channel", value=f"<#{channel.id}>")
            embed2.add_field(name="Developer", value=f"[{str(owner)}]({self.bot.settings['website']['url']}/users/"
                                                     f"{owner.id}) (`{owner.id}`)")

            testguild = self.bot.get_guild(int(self.bot.settings['guilds']['staff']))
            fixesrole = testguild.get_role(int(self.bot.settings['roles']['fixesBot']))
            memberbot = testguild.get_member(bot.id)
            if memberbot is not None:
                await memberbot.add_roles(fixesrole, reason='Bot is Awaiting Fixes.')

            log_channel = ctx.guild.get_channel(int(self.bot.settings["channels"]["ticketLog"]))
            log_msg = await log_channel.send(embed=embed2)

            await self.bot.db.tickets.insert_one({
                "_id": str(ticket_id),
                "ids": {
                    "channel": str(channel.id),
                    "message": str(message.id),
                    "log": str(log_msg.id),
                    "bot": str(bot.id)
                },
                "status": 0,
                "closureReason": None
            })
        except Exception as e:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **An error occurred:**\n```{e}```")

    @commands.command(name="awaiting-fixes", aliases=["awaiting-changes", "af", "ac", "fixes", "changes"])
    @commands.guild_only()
    @mod_check()
    async def awaiting_fixes(self, ctx):
        await ctx.message.delete()

        status_check: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({
            "ids.channel": str(ctx.channel.id)
        })

        if status_check:
            message = await ctx.channel.fetch_message(int(status_check["ids"]["message"]))

            embed = message.embeds[0]
            embed.colour = self.awaiting_fixes
            embed.set_author(name=f"Approval Feedback - {status_check['_id']} [AWAITING FIXES]",
                             icon_url=self.bot.settings["images"]["awaiting_fixes"])

            await message.edit(embed=embed)

            await ctx.send(f"{self.bot.settings['formats']['ticketStatus']} **Ticket update:** Changed ticket "
                           f"status to `Awaiting Fixes`.")

            ticket: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({
                "ids.message": str(message.id)
            })

            log_msg = await ctx.guild.get_channel(int(self.bot.settings["channels"]["ticketLog"])) \
                .fetch_message(int(ticket["ids"]["log"]))

            embed2 = log_msg.embeds[0]
            embed2.colour = self.awaiting_fixes
            embed2.set_author(name=f"Approval Feedback - {status_check['_id']} [AWAITING FIXES]",
                              icon_url=self.bot.settings["images"]["awaiting_fixes"])

            await log_msg.edit(embed=embed2)

            await ctx.bot.db.tickets.update_one({"ids.channel": str(ctx.channel.id)}, {
                "$set": {
                    "status": 1
                }
            })

        elif status_check and status_check["status"] == 1:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **No changes:** This ticket is already set "
                                  f"as `Awaiting Fixes`.", delete_after=5)
        else:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid channel:** This is not a valid "
                                  f"ticket channel.")

    @commands.command(name="close-ticket", aliases=["ct", "close"])
    @commands.guild_only()
    @mod_check()
    async def close_ticket(self, ctx, *, reason: str):

        try:
            message_id: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({
                "ids.channel": str(ctx.channel.id)
            })

            if len(reason) > 500:
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Invalid length:** The reason you provided is too "
                    f"long. (`{len(reason) / 500}`)")

            if message_id:
                channel_name = ctx.channel.name

                messages = []
                for message in await ctx.channel.history().flatten():
                    messages.append(f"[{message.created_at}] {message.author} - {message.content}\n")

                messages.reverse()
                file = discord.File(BytesIO(("".join(messages)).encode("utf-8")), filename=f"{message_id['_id']}.txt")

                await ctx.channel.delete(reason=f"Approval feedback closed - Author: {ctx.author.id}, Ticket ID: "
                                                f"{message_id['_id']}")

                log_message = await ctx.guild.get_channel(int(self.bot.settings["channels"]["ticketLog"])) \
                    .fetch_message(message_id["ids"]["log"])

                guild = self.bot.get_guild(int(self.bot.settings["guilds"]["messageLog"]))

                message_history = await guild.get_channel(int(self.bot.settings["channels"]["messageLog"])) \
                    .send(content=log_message.jump_url, file=file)

                embed = log_message.embeds[0]
                embed.colour = self.closed
                embed.remove_field(0)
                embed.insert_field_at(0, name="Channel", value=f"[#{channel_name}](https://txt.discord.website/?txt="
                                                               f"{self.bot.settings['channels']['messageLog']}"
                                                               f"/{message_history.attachments[0].id}/"
                                                               f"{message_id['_id']})")

                embed.set_author(name=f"Approval Feedback - {message_id['_id']} [CLOSED]",
                                 icon_url=self.bot.settings["images"]["closed"])

                await log_message.edit(embed=embed)
                await ctx.bot.db.tickets.update_one({"_id": str(message_id['_id'])}, {
                    "$set": {
                        "status": 2,
                        "closureReason": reason,
                        "ids.history": str(message_history.id)
                    }
                })
            else:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid channel:** This is not a "
                                      f"valid ticket channel.")
        except Exception as e:
            tb = traceback.format_exception(type(e), e, e.__traceback__)
            print("".join(tb))
            await ctx.author.send(f"Error occured! {e}")


def setup(bot):
    bot.add_cog(TicketCog(bot))
