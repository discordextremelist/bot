import discord
import json
from discord.ext import commands

with open("settings.json") as content:
    settings = json.load(content)


class NoMod(commands.CheckFailure):
    pass


class NoSomething(commands.CommandError):
    def __init__(self, account: discord.User):
        self.user = account
        if account.bot:
            fmt = f"**Invalid bot:** I could not find {account} in my " \
                  "database."
        else:
            fmt = f"**Invalid user:** I could not find {account} in my " \
                  "database."

        self.message = fmt
        super().__init__(fmt)


def mod_check():
    async def predicate(ctx):
        db_user = await ctx.bot.db.users.find_one({"_id": str(ctx.author.id)})
        if db_user is None or not db_user['rank']['mod']:
            raise NoMod()

        return True

    return commands.check(predicate)
