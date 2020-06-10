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

import colouredlogs, logging
import datetime
import discord
from motor.motor_asyncio import AsyncIOMotorClient
import json

from discord.ext import commands, tasks
from ext.context import EditingContext

colouredlogs.install()

with open("settings.json") as content:
    settings = json.load(content)

logging.basicConfig(level=logging.INFO)

logging.info("Starting bot")
db = AsyncIOMotorClient(settings["mongo"]["uri"])[settings["mongo"]["db"]]
botExtensions = [
    "cogs.help",
    "cogs.utility",
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
    bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, owner_ids=settings["ownership"]["owners"])
else:
    bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, owner_id=settings["ownership"]["owner"])

bot.remove_command("help")
bot.db = db
bot.settings = settings
bot.cmd_edits = {}

if __name__ == "__main__":
    for ext in botExtensions:
        try:
            bot.load_extension(ext)
            logging.info(f"{ext} has been loaded")
        except Exception as err:
            logging.error(f"An error occurred whilst loading {ext}: {err}")


@bot.event
async def on_ready():
    logging.info(f"Connection established! - Logged in as {bot.user} ({bot.user.id})")
    if not hasattr(bot, "uptime"):
        bot.uptime = datetime.datetime.utcnow()


@bot.event
async def on_guild_join(guild):
    logging.info(f"Joined guild - {guild.name} ({guild.id})")


@bot.event
async def on_user_update(before, after):
    if before.bot:
        db_bot = db["bots"].find_one({"_id": str(before.id)})

        if db_bot:
            db["bots"].update_one({"_id": str(before.id)}, {
                "$set": {
                    "name": after.name,
                    "avatar": {
                        "hash": after.avatar,
                        "url": f"https://cdn.discordapp.com/avatars/{before.id}/{after.avatar}"
                    }
                }
            })
    else:
        user = db["users"].find_one({"_id": str(before.id)})

        if user:
            db["users"].update_one({"_id": str(before.id)}, {
                "$set": {
                    "name": after.name,
                    "discrim": after.discriminator,
                    "fullUsername": f"{after.name}#{after.discriminator}",
                    "avatar": {
                        "hash": after.avatar,
                        "url": f"https://cdn.discordapp.com/avatars/{before.id}/{after.avatar}"
                    }
                }
            })


@bot.event
async def on_member_join(member):
    if member.bot:
        db_bot = db["bots"].find_one({"_id": str(member.id)})

        if str(member.guild.id) == settings["guilds"]["main"]:
            if db_bot:
                if db_bot["status"]["verified"]:
                    await member.add_roles(discord.Object(id=int(settings["roles"]["verifiedBot"])),
                                           reason="Bot is Verified on the website.")
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

        bots = db["bots"].find({"owner": {"_id": str(member.id)}})
        bot_count = 0

        for discord_bot in bots:
            if discord_bot["status"]["approved"]:
                bot_count += 1

        if bot_count >= 1:
            await member.add_roles(discord.Object(id=int(settings["roles"]["developer"])),
                                   reason="User is a Developer on the website.")


@bot.event
async def on_command_error(ctx, error):
    if error in (discord.Forbidden, commands.BotMissingPermissions, commands.CommandNotFound, commands.CheckFailure):
        pass


@bot.event
async def on_message(msg):
    if not msg.author.bot:
        ctx = await bot.get_context(msg, cls=EditingContext)
        await bot.invoke(ctx)


@bot.event
async def on_message_edit(old_msg, new_msg):
    if not old_msg.author.bot and new_msg.content is not old_msg.content:
        ctx = await bot.get_context(new_msg, cls=EditingContext)
        await bot.invoke(ctx)


bot.run(settings["token"], bot=True, reconnect=True)
