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

from discord.ext import commands, tasks
from discord_slash import cog_ext, SlashContext
from ext.checks import mod_check
from datetime import datetime, timedelta

import traceback
import snowflake
import typing
from io import BytesIO
from contextlib import suppress

from .types import ticketTypes, botTypes
from ext.default import traceback_maker, FutureTime, human_timedelta


class TicketCog(commands.Cog, name="Tickets"):

    def __init__(self, bot):
        self.bot = bot
        self.help_icon = f"{self.bot.settings['emoji']['ticket']}"
        self.generator = snowflake.Generator()
        self.closed = 0xdd2e44
        self.awaiting_response = 0x77ff77
        self.awaiting_fixes = 0xf4dd1a

        self.update_ticket_topic.start()  # start the loop

    def cog_unload(self):
        self.update_ticket_topic.cancel()

    async def snowflake_generate(self):
        """
        Generates a snowflake ID and checks to ensure it is not a duplicate.
        """
        while True:
            generated = self.generator.generate()
            check_db: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({"_id": str(generated)})

            if not check_db:
                return generated

    # noinspection PyTypedDict
    @tasks.loop(hours=1)  # Will go through channels every hour
    async def update_ticket_topic(self):
        guild = self.bot.get_guild(667065302260908032)
        ticket_category = guild.get_channel(int(self.bot.settings["channels"]["ticketCategory"]))

        for text_channel in ticket_category.channels:
            if text_channel.id == int(self.bot.settings["channels"]["ticketLog"]):  # ignore the log channel.
                continue
            else:
                ticket_check: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({
                    "ids.channel": str(text_channel.id)
                })
                if ticket_check:
                    with suppress(KeyError):
                        time = human_timedelta(ticket_check['timeUntil'], source=datetime.utcnow())
                        current_time = datetime.utcnow()
                        total_time = (ticket_check['timeUntil'] - current_time).total_seconds()
                        if total_time <= 0 and 'Time is over' not in text_channel.topic:
                            await text_channel.edit(topic=f"{self.bot.settings['website']['url']}/bots/{ticket_check['ids']['bot']}"
                                                          f"\nTime is over.")
                            return await text_channel.send("They ran out of time.")
                        elif total_time > 0:
                            await text_channel.edit(topic=f"{self.bot.settings['website']['url']}/bots/{ticket_check['ids']['bot']}"
                                                          f"\n⏲ Time remaining to fix the mentioned issues **{time}**")

    @update_ticket_topic.before_loop
    async def before_update_ticket_topic(self):
        await self.bot.wait_until_ready()

    async def open_ticket_command(self, ctx, bot):
        """
        Allows you to open a ticket with the specified bots' developer.
        """
        if isinstance(bot, int):
            bot = str(bot)

        if isinstance(bot, discord.User):
            pass
        elif isinstance(bot, str):
            if bot.isdigit():
                try:
                    bot = await ctx.bot.fetch_user(int(bot))
                except Exception as e:
                    return await \
                        ctx.send(f"{self.bot.settings['formats']['error']} **An error occurred:**\n```py\n{e}```")
            elif not bot.isdigit():
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Unknown bot:** We could not find a "
                                      f"bot with the arguments you provided - Try using an ID so I can fetch it?")

        print(type(bot))
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
            # serverbots = ctx.guild.get_role(int(self.bot.settings['roles']['botpower']))
            
            if owner is None:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Owner Missing:** The bot owner is "
                                      f"not in the server!")

            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                owner: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                mods: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True,
                                                          manage_channels=True, manage_messages=True,
                                                          embed_links=True, attach_files=True)
                # serverbots: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            channel = await category.create_text_channel(name=bot.name.lower(), overwrites=overwrites,
                                                         reason=f"Approval feedback channel - {ctx.author.id}",
                                                         topic=f"{self.bot.settings['website']['url']}/bots/{bot.id}")

            embed = discord.Embed(colour=self.awaiting_response,
                                  description="Hello, whilst reviewing your bot we found some issues, please refer to "
                                              "the message(s) the staff member has sent below. Please do not ping staff members "
                                              "when replying.",
                                  timestamp=datetime.utcnow())

            embed.set_author(name=f"Approval Feedback - {ticket_id} [AWAITING RESPONSE]",
                             icon_url=self.bot.settings["images"]["awaiting_response"])

            embed.set_footer(text=f"{str(bot)} ({bot.id})", icon_url=str(bot.avatar_url))

            message = await channel.send(content=owner.mention, embed=embed,
                                         allowed_mentions=discord.AllowedMentions(users=True))

            await message.pin()
            await ctx.send(f"{self.bot.settings['formats']['success']} **Ticket created:** Successfully created "
                           f"ticket - <#{channel.id}>.")

            embed2 = discord.Embed(color=self.awaiting_response)

            embed2.set_author(name=f"Approval Feedback - {ticket_id} [AWAITING RESPONSE]",
                              icon_url=self.bot.settings["images"]["awaiting_response"])

            embed2.set_footer(text=f"{str(bot)} ({bot.id})", icon_url=str(bot.avatar_url))

            embed2.add_field(name="Channel", value=f"<#{channel.id}>")
            embed2.add_field(name="Developer", value=f"[{str(owner)}]({self.bot.settings['website']['url']}/users/"
                                                     f"{owner.id}) (`{owner.id}`)")

            # testguild = self.bot.get_guild(int(self.bot.settings['guilds']['staff']))
            # fixesrole = testguild.get_role(int(self.bot.settings['roles']['fixesBot']))
            # memberbot = testguild.get_member(bot.id)
            # if memberbot is not None:
            #     await memberbot.add_roles(fixesrole, reason='Bot is Awaiting Fixes.')

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
            return await ctx.send(f"{self.bot.settings['formats']['error']} **An error occurred:**\n```{traceback_maker(e)}```")

    @commands.command(name="open-ticket",
                      aliases=["new-ticket", "nt", "ot", "request-changes", "rc", "create-ticket", "open", "create"],
                      usage="open-ticket <bot>",
                      description="Allows you to open a ticket with the specified bots' developer.")
    @commands.guild_only()
    @mod_check()
    async def open_ticket(self, ctx, *, bot: typing.Union[discord.User, str]):
        await self.open_ticket_command(ctx, bot=bot)

    @cog_ext.cog_slash(name="open-ticket",
                       description="Allows you to open a ticket with the specified bots' developer.",
                       options=[{"name": "bot", "description": "The bot you want to open a ticket for.", "type": 6,
                                 "required": True}],
                       guild_ids=[667065302260908032])
    @mod_check()
    @commands.guild_only()
    async def slash_open_ticket(self, ctx, *, bot: typing.Union[discord.User, str]):
        await self.open_ticket_command(ctx, bot=bot)

    async def awaiting_fixes_command(self, ctx):
        """
        Updates the current ticket channel's status to Awaiting Fixes.
        """
        with suppress(AttributeError):
            await ctx.message.delete()

        status_check: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({
            "ids.channel": str(ctx.channel.id)
        })

        if status_check:
            message = await ctx.channel.fetch_message(int(status_check["ids"]["message"]))

            timeUntil = datetime.utcnow() + timedelta(hours=48)
            embed = message.embeds[0]
            embed.colour = self.awaiting_fixes
            embed.set_author(name=f"Approval Feedback - {status_check['_id']} [AWAITING FIXES]",
                             icon_url=self.bot.settings["images"]["awaiting_fixes"])
            await ctx.channel.edit(topic=ctx.channel.topic + f"\n⏲ Time remaining to fix the mentioned issues **48** hours.")

            await message.edit(embed=embed)

            await ctx.send(f"{self.bot.settings['formats']['ticketStatus']} **Ticket update:** Changed ticket "
                           f"status to `Awaiting Fixes`. Starting the 48 hours timer.")

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
                    "status": 1,
                    "timeUntil": timeUntil
                }
            })

        elif status_check and status_check["status"] == 1:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **No changes:** This ticket is already set "
                                  f"as `Awaiting Fixes`.", delete_after=5)
        else:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid channel:** This is not a valid "
                                  f"ticket channel.")

    @commands.command(name="awaiting-fixes", aliases=["awaiting-changes", "af", "ac", "fixes", "changes"],
                      usage="awaiting-fixes", description="Updates the current ticket channel's status to Awaiting "
                                                          "Fixes.")
    @commands.guild_only()
    @mod_check()
    async def awaiting_fixes(self, ctx):
        await self.awaiting_fixes_command(ctx)

    @cog_ext.cog_slash(name="awaiting-fixes",
                       description="Updates the current ticket channel's status to Awaiting Fixes.",
                       guild_ids=[667065302260908032])
    @mod_check()
    @commands.guild_only()
    async def slash_awaiting_fixes(self, ctx):
        await self.awaiting_fixes_command(ctx)

    async def close_ticket_command(self, ctx, *, reason: str):
        """
        Closes the ticket whose ticket channel you run it in.
        """
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
                for message in await ctx.channel.history(limit=None).flatten():
                    messages.append(f"[{message.created_at}] {message.author} - {message.content}\n")

                messages.reverse()
                file = discord.File(BytesIO(("".join(messages)).encode("utf-8")), filename=f"{message_id['_id']}.txt")

                await ctx.channel.delete(reason=f"Approval feedback closed - Author: {ctx.author.id}, Ticket ID: "
                                                f"{message_id['_id']}")

                log_message = await ctx.guild.get_channel(int(self.bot.settings["channels"]["ticketLog"])) \
                    .fetch_message(message_id["ids"]["log"])

                guild = self.bot.get_guild(int(self.bot.settings["guilds"]["messageLog"]))

                message_history = await ctx.guild.get_channel(int(self.bot.settings["channels"]["messageLog"])) \
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

    @commands.command(name="close-ticket", aliases=["ct", "close"], usage="close-ticket",
                      description="Closes the ticket whose ticket channel you run it in.")
    @commands.guild_only()
    @mod_check()
    async def close_ticket(self, ctx, *, reason: str):
        await self.close_ticket_command(ctx, reason=reason)

    @cog_ext.cog_slash(name="close-ticket",
                       description="Closes the ticket whose ticket channel you run it in.",
                       options=[{"name": "reason", "description": "The reason why you're closing this ticket",
                                 "type": 3, "required": True}],
                       guild_ids=[667065302260908032])
    @commands.guild_only()
    @mod_check()
    async def slash_close_ticket(self, ctx, *, reason: str):
        await self.close_ticket_command(ctx, reason=reason)

    async def set_time_command(self, ctx, *, time: typing.Union[FutureTime, str]):
        with suppress(AttributeError):
            await ctx.message.delete()

        if isinstance(time, FutureTime):
            pass
        elif isinstance(time, str):
            time = FutureTime(time)

        status_check: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({
            "ids.channel": str(ctx.channel.id)
        })

        if status_check:
            message = await ctx.channel.fetch_message(int(status_check["ids"]["message"]))

            await ctx.channel.edit(topic=f"{self.bot.settings['website']['url']}/bots/{status_check['ids']['bot']}"
                                         f"\n⏲ Time remaining to fix the mentioned issues "
                                         f"**{human_timedelta(time.dt, source=ctx.message.created_at if ctx.message else datetime.utcnow())}**")

            await ctx.send(f"{self.bot.settings['formats']['ticketStatus']} **Timer update:** Set timer to expire "
                           f"after {human_timedelta(time.dt, source=ctx.message.created_at if ctx.message else datetime.utcnow())}")

            await ctx.bot.db.tickets.update_one({"ids.channel": str(ctx.channel.id)}, {
                "$set": {
                    "timeUntil": time.dt
                }
            })

        elif status_check and status_check["status"] == 1:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **No changes:** This ticket is already set "
                                  f"as `Awaiting Fixes`.", delete_after=5)
        else:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid channel:** This is not a valid "
                                  f"ticket channel.")

    @commands.command(name='set-time', aliases=['st', 'settime', 'set'],
                      description=".")
    @commands.guild_only()
    @mod_check()
    async def set_time(self, ctx, *, time: FutureTime):
        await self.set_time_command(ctx, time=time)

    @cog_ext.cog_slash(name="set-time",
                       description="Set the time when the developer will be out of time.",
                       options=[{"name": "time", "description": "The time until the ticket will be open",
                                 "type": 3, "required": True}],
                       guild_ids=[667065302260908032])
    @commands.guild_only()
    @mod_check()
    async def slash_set_time(self, ctx, *, time: str):  # Custom aren't supported so doing it in str and then converting to FutureTime.
        await self.set_time_command(ctx, time=time)

    async def add_user_command(self, ctx, *, member: discord.Member):
        with suppress(AttributeError):
            await ctx.message.delete()

        status_check: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({
            "ids.channel": str(ctx.channel.id)
        })

        if not status_check:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid channel:** This is not a valid "
                                  f"ticket channel.")

        if member in ctx.channel.members:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **No changes:** {member} can already see "
                                  "this channel.")
        else:
            overwrite = ctx.channel.overwrites_for(member)
            overwrite.read_messages = True
            await ctx.channel.set_permissions(member, overwrite=overwrite, reason=f'{ctx.author} ({ctx.author.id}) added {member} to ticket')
            await ctx.send(f"{self.bot.settings['formats']['success']} **Member added:** Added {member} to this channel.")

    @commands.command(name='add-user', aliases=['adduser', 'add'],
                      description="Add user to the ticket.")
    @commands.guild_only()
    @mod_check()
    async def add_user(self, ctx, *, member: discord.Member):
        await self.add_user_command(ctx, member=member)

    @cog_ext.cog_slash(name="add-user",
                       description="Add user to the ticket.",
                       options=[{"name": "member", "description": "The member which you want to add", "type": 6, "required": True}],
                       guild_ids=[667065302260908032])
    @commands.guild_only()
    @mod_check()
    async def slash_add_user(self, ctx, *, member: discord.Member):
        await self.add_user_command(ctx, member=member)

    async def remove_user_command(self, ctx, *, member: discord.Member):
        with suppress(AttributeError):
            await ctx.message.delete()

        status_check: ticketTypes.DelTicket = await self.bot.db.tickets.find_one({
            "ids.channel": str(ctx.channel.id)
        })

        ticket_bot: botTypes.DelBot = await self.bot.db.bots.find_one({
            "_id": status_check["ids"]["bot"]
        })

        if not status_check:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid channel:** This is not a valid "
                                  f"ticket channel.")

        if ticket_bot["owner"]["id"] == str(member.id):
            return await ctx.send(f"{self.bot.settings['formats']['error']} **No changes:** That user is the bot developer. You "
                                  f"can't remove them from this ticket channel.")

        if member not in ctx.channel.members:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **No changes:** {member} can't see"
                                  "this channel.")
        else:
            overwrite = ctx.channel.overwrites_for(member)
            overwrite.read_messages = False
            await ctx.channel.set_permissions(member, overwrite=overwrite, reason=f'{ctx.author} ({ctx.author.id}) removed {member} from ticket')
            await ctx.send(f"{self.bot.settings['formats']['success']} **Member removed:** Removed {member} from this channel.")

    @commands.command(name='remove-user', aliases=['removeuser', 'remove'],
                      description="Remove an user from the ticket")
    @commands.guild_only()
    @mod_check()
    async def remove_user(self, ctx, *, member: discord.Member):
        await self.remove_user_command(ctx, member=member)

    @cog_ext.cog_slash(name="remove-user",
                       description="Remove user from the ticket",
                       options=[{"name": "member", "description": "Member you want to remove from the ticket", "type": 6, "required": True}],
                       guild_ids=[667065302260908032])
    @commands.guild_only()
    @mod_check()
    async def slash_remove_user(self, ctx, *, member: discord.Member):
        await self.remove_user_command(ctx, member=member)


def setup(bot):
    bot.add_cog(TicketCog(bot))
