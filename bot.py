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
import pymongo 
import json

from colorama import Fore, init
from discord.ext import commands, tasks

init()
colouredlogs.install()

with open("settings.json") as content:
    settings = json.load(content)

logging.basicConfig(level=logging.INFO)

fr = Fore.RESET
logging.info("Starting bot")
MongoClient = pymongo.MongoClient(settings["mongo"]["uri"])
db = MongoClient[settings["mongo"]["db"]]
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
        bot = db["bots"].find_one({"id": str(member.id)})
        
        if bot:
            db["bots"].update_one({"id": str(before.id)}, {
                "$set": {
                    "name": after.name,
                    "avatar": {
                        "hash": after.avatar,
                        "url": f"https://cdn.discordapp.com/avatars/{before.id}/{after.avatar}"
                    }
                }
            })
    else:
        user = db["users"].find_one({"id": str(member.id)})
        
        if user:
            db["users"].update_one({"id": str(before.id)}, {
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
        bot = db["bots"].find_one({"id": str(member.id)})

        if str(member.guild.id) == settings["guilds"]["main"]:
            if bot:
                if bot["status"]["verified"]:
                    await member.add_roles(discord.Object(id=int(settings["roles"]["verifiedBot"])), reason="Bot is Verified on the website.")
                else:
                    await member.add_roles(discord.Object(id=int(settings["roles"]["bot"])), reason="Bot is Approved on the website.")
            else:
                await member.add_roles(discord.Object(id=int(settings["roles"]["unlisted"])), reason="Bot is not listed on the website.")
        else:
            if bot:
                if bot["status"]["approved"]:
                    await member.add_roles(discord.Object(id=int(settings["roles"]["unapprovedBot"])), reason="Bot is not approved on the website.")

    elif str(member.guild.id) == settings["guilds"]["main"]:
        user = db["users"].find_one({"id": str(member.id)})

        if user["rank"]["verified"]:
            await member.add_roles(discord.Object(id=int(settings["roles"]["verifiedDeveloper"])), reason="User is a Verified Developer on the website.")
            await member.add_roles(discord.Object(id=int(settings["roles"]["developer"])), reason="User is a Verified Developer on the website.")
        else:
            bots = db["bots"].find({"owner": {"id": str(member.id)}})
            botCount = 0

            for bot in bots:
                if bot["status"]["approved"]:
                    botCount += 1

            if botCount >= 1:
                await member.add_roles(discord.Object(id=int(settings["roles"]["developer"])), reason="User is a Verified Developer on the website.")



bot.run(settings["token"], bot=True, reconnect=True)
