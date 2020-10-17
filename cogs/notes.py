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
import time

import discord
from discord.ext import commands
from ext.checks import mod_check, NoSomething

import traceback
import typing
from io import BytesIO


def check_s_end(string):
    if string.endswith("s"):
        return True
    else:
        return False


class BotNotesCog(commands.Cog):

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

    async def check_bot(self, ctx, bot: typing.Union[discord.User, str]):
        if isinstance(bot, discord.User):
            pass
        elif isinstance(bot, str):
            if bot.isdigit():
                try:
                    bot = await ctx.bot.fetch_user(bot)
                except Exception as e:
                    return await ctx.send(
                        f"{self.bot.settings['formats']['error']} **An error occurred:**\n```py\n{e}```")
            elif not bot.isdigit():
                return await ctx.send(
                    f"{self.bot.settings['formats']['error']} **Unknown bot:** We could not find a bot with the "
                    f"arguments you provided - Try using an ID so I can fetch it?")

        if not bot.bot:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Invalid bot:** {bot} is not a bot.")

        return bot

    @commands.command(name="add-note", aliases=["addnote", "insertnote"], usage="add-note <bot> <note>")
    @commands.guild_only()
    @mod_check()
    async def add_note(self, ctx, bot: typing.Union[discord.User, str], *, note: str):

        bot = await self.check_bot(ctx, bot)

        bot_db = await ctx.bot.db.bots.find_one({
            "_id": str(bot.id)
        })

        if not bot_db:
            raise NoSomething(bot)

        notes_db = bot_db["reviewNotes"]

        notes_db.append({
            "note": note,
            "author": str(ctx.author.id),
            "date": time.time() * 1000
        })

        await ctx.bot.db.bots.update_one({"_id": str(bot_db["_id"])}, {
            "$set": {
                "reviewNotes": notes_db
            }
        })

        return await ctx.send(f"{self.bot.settings['formats']['success']} **Success:** I have successfully added your "
                              f"note to {bot_db['name']}.")

    @commands.command(name="remove-note", aliases=["removenote", "delnote", "del-note", "delete-note", "deletenote"],
                      usage="remove-note <bot> <note>")
    @commands.guild_only()
    @mod_check()
    async def remove_note(self, ctx, bot: typing.Union[discord.User, str], *, note: int):

        bot = await self.check_bot(ctx, bot)

        bot_db = await ctx.bot.db.bots.find_one({
            "_id": str(bot.id)
        })

        if not bot_db:
            raise NoSomething(bot)

        notes_db = bot_db["reviewNotes"]

        if note > len(notes_db) or note < 1:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Doesn't exist:** The note you're trying "
                                  f"to delete doesn't exist.")

        del notes_db[(note - 1)]

        await ctx.bot.db.bots.update_one({"_id": str(bot_db["_id"])}, {
            "$set": {
                "reviewNotes": notes_db
            }
        })

        return await ctx.send(
            f"{self.bot.settings['formats']['success']} **Success:** I have successfully removed note #{note} "
            f"from {bot_db['name']}.")

    @commands.command(name="notes", usage="notes <bot>")
    @commands.guild_only()
    @mod_check()
    async def notes(self, ctx, *, bot: typing.Union[discord.User, str]):

        bot = await self.check_bot(ctx, bot)

        bot_db = await ctx.bot.db.bots.find_one({
            "_id": str(bot.id)
        })

        if not bot_db:
            raise NoSomething(bot)

        if not bot_db["reviewNotes"]:
            return await ctx.send(f"{self.bot.settings['formats']['info']} **No notes:** This bot does not have "
                                  f"any notes.")

        if check_s_end(bot_db["name"]):
            title = f"{bot_db['name']}' Notes"
        else:
            title = f"{bot_db['name']}'s Notes"

        embed = discord.Embed(title=title, colour=await self.embed_colour(ctx))
        embed.set_thumbnail(url=bot_db["avatar"]["url"])
        pos = 1

        for note in bot_db["reviewNotes"]:
            try:
                user = str(await self.bot.fetch_user(note["author"]))
            except discord.NotFound:
                user = str(note["author"])

            date = datetime.datetime.utcfromtimestamp(note["date"] / 1000).strftime(f"%I:%M%p - %a, %d %b %Y (GMT)")
            embed.add_field(name=f"Note #{pos}", value=f"-> **{discord.utils.escape_markdown(user, as_needed=False)} "
                                                       f"- {date}**\n" + note["note"], inline=False)
            pos += 1

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BotNotesCog(bot))
