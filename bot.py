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
import json
import logging

import colouredlogs
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

from ext.checks import NoMod, NoSomething
from ext.context import EditingContext

colouredlogs.install()

with open("settings.json") as content:
    settings = json.load(content)

logging.basicConfig(level=logging.INFO)
logging.getLogger("discord").setLevel(logging.WARNING)

logging.info("Starting bot")
db = AsyncIOMotorClient(settings["mongo"]["uri"])[settings["mongo"]["db"]]
botExtensions = [
    "cogs.help",
    "cogs.utility",
    "cogs.tickets",
    "jishaku"
]


async def get_prefix(bot, message):
    if not message.guild:
        prefixes = ""
        return prefixes
    else:
        prefixes = settings["prefix"]
        return commands.when_mentioned_or(*prefixes)(bot, message)


if settings["ownership"]["multiple"]:
    bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, owner_ids=settings["ownership"]["owners"],
                       allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))
else:
    bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, owner_id=settings["ownership"]["owner"],
                       allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))

bot.db = db
bot.remove_command("help")
bot.settings = settings
bot.cmd_edits = {}

if __name__ == "__main__":
    for ext in botExtensions:
        try:
            bot.load_extension(ext)
            logging.info(f"{ext} has been loaded")
        except Exception as err:
            logging.exception(f"An error occurred whilst loading {ext}", exc_info=err)


@bot.event
async def on_ready():
    logging.info(f"Connection established! - Logged in as {bot.user} ({bot.user.id})")
    game = discord.Game(name="discordextremelist.xyz", type=discord.ActivityType.watching)
    await bot.change_presence(status=discord.Status.online, activity=game)
    if not hasattr(bot, "uptime"):
        bot.uptime = datetime.datetime.utcnow()


@bot.event
async def on_guild_join(guild):
    logging.info(f"Joined guild - {guild.name} ({guild.id})")


@bot.event
async def on_user_update(_, after):
    if after.bot:
        db_bot = db["bots"].find_one({"_id": str(after.id)})

        if db_bot:
            db["bots"].update_one({"_id": str(after.id)}, {
                "$set": {
                    "name": after.name,
                    "avatar": {
                        "hash": after.avatar,
                        "url": f"https://cdn.discordapp.com/avatars/{after.id}/{after.avatar}"  # ffs stay consistent
                    }
                }
            })
    else:
        user = db["users"].find_one({"_id": str(after.id)})

        if user:
            db["users"].update_one({"_id": str(after.id)}, {
                "$set": {
                    "name": after.name,
                    "discrim": after.discriminator,
                    "fullUsername": f"{after.name}#{after.discriminator}",
                    "avatar": {
                        "hash": after.avatar,
                        "url": f"https://cdn.discordapp.com/avatars/{after.id}/{after.avatar}"  # ffs
                    }
                }
            })


@bot.event
async def on_member_join(member):
    if member.bot:
        db_bot = await db.bots.find_one({"_id": str(member.id)})

        if str(member.guild.id) == settings["guilds"]["main"]:
            if db_bot:
                if db_bot["status"]["premium"]:
                    await member.add_roles(discord.Object(id=int(settings["roles"]["premiumBot"])),
                                           reason="Bot is Premium on the website.")
                else:
                    await member.add_roles(discord.Object(id=int(settings["roles"]["bot"])),
                                           reason="Bot is Approved on the website.")
            else:
                await member.add_roles(discord.Object(id=int(settings["roles"]["unlisted"])),
                                       reason="Bot is not listed on the website.")
        else:
            if db_bot:
                if db_bot["status"]["approved"]:
                    await member.add_roles(discord.Object(id=int(settings["roles"]["unapprovedBot"])),
                                           reason="Bot is not approved on the website.")

    elif str(member.guild.id) == settings["guilds"]["main"]:

        bots = await db.bots.find_one({"owner": {"id": str(member.id)}})

        for discord_bot in bots:
            if discord_bot["status"]["approved"]:
                await member.add_roles(discord.Object(id=int(settings["roles"]["developer"])),
                                       reason="User is a Developer on the website.")
                break


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (discord.Forbidden, commands.CommandNotFound)):
        return

    if isinstance(error, NoMod):
        return await ctx.channel.send(f"{settings['formats']['noPerms']} **Invalid permission(s):** You need "
                                      f"to be a Moderator to execute this command.")

    if isinstance(error, NoSomething):
        return await ctx.channel.send(error.message)

    if isinstance(error, commands.CheckFailure) and error.args:
        return await ctx.channel.send(error)

    if isinstance(error, commands.CommandError) and error.args:
        return await ctx.channel.send(error.args[0])

    logging.exception("something done fucked up", exc_info=error)


@bot.event
async def on_message(msg):
    if not msg.author.bot:
        ctx = await bot.get_context(msg, cls=EditingContext)
        await bot.invoke(ctx)

        ticket = await bot.db.tickets.find_one({
            "ids.channel": str(ctx.channel.id)
        })

        if ticket and ticket["status"] == 0:
            bot_db = await ctx.bot.db.bots.find_one({
                "_id": str(ticket["ids"]["bot"])
            })

            if bot_db and bot_db["owner"]["id"] == str(ctx.author.id):
                message = await ctx.channel.fetch_message(int(ticket["ids"]["message"]))

                embed = message.embeds[0]
                embed.colour = 0x0fb9fc
                embed.set_author(name=f"Approval Feedback - {ticket['_id']} [DEV REPLIED]",
                                 icon_url=ctx.bot.settings["images"]["dev_replied"])

                await message.edit(embed=embed)

                await ctx.send(f"{bot.settings['formats']['ticketStatus']} **Ticket update:** Changed ticket "
                               f"status to `Dev Replied`.")

                ticket = await bot.db.tickets.find_one({
                    "ids.message": str(message.id)
                })

                log_msg = await ctx.guild.get_channel(int(bot.settings["channels"]["ticketLog"])) \
                    .fetch_message(int(ticket["ids"]["log"]))

                embed2 = log_msg.embeds[0]
                embed2.colour = 0x0fb9fc
                embed2.set_author(name=f"Approval Feedback - {ticket['_id']} [DEV REPLIED]",
                                  icon_url=ctx.bot.settings["images"]["dev_replied"])

                await log_msg.edit(embed=embed2)

                await ctx.bot.db.tickets.update_one({"_id": ticket["_id"]}, {
                    "$set": {
                        "status": 3
                    }
                })


@bot.event
async def on_message_edit(old_msg, new_msg):
    if not old_msg.author.bot and new_msg.content != old_msg.content:
        ctx = await bot.get_context(new_msg, cls=EditingContext)
        await bot.invoke(ctx)


bot.run(settings["token"], bot=True, reconnect=True)
