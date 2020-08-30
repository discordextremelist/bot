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

from .types import userTypes


class HelpCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", hidden=False)
    async def help(self, ctx, *, command: str = None):
        async with ctx.channel.typing():

            if command is not None:
                if not ctx.guild:
                    colour = 0xFFFFFA
                else:
                    botGuildMember = await ctx.guild.fetch_member(self.bot.user.id)
                    if len(str(botGuildMember.colour.value)) == 1:
                        colour = 0xFFFFFA
                    else:
                        colour = botGuildMember.colour.value

                embed = discord.Embed(colour=colour)

                if command in ["jsk", "jishaku"]:
                    jishaku = self.bot.get_command('jishaku')
                    subcommands = ''
                    for command in jishaku.commands:
                        subcommands += f"• {command.name} - `{command.short_doc}`\n"
                    embed.title = f"{self.bot.settings['emoji']['notepad']} Help: jishaku"
                    embed.description = f'{self.bot.settings['emoji']['speech']} **Subcommands:**\n{sucommands}'
                    embed.add_field(name=f"{self.bot.settings['emoji']['notepad']} Aliases", value="jsk")
                    embed.add_field(name=f"{self.bot.settings['emoji']['notepad']} Usage",
                                    value="jishaku <subCommand> <arguments>")
                    embed.add_field(name=f"{self.bot.settings['emoji']['speech']} Information",
                                    value=jishaku.help, inline=False)
                else:
                    cmd = self.bot.get_command(command)

                    if cmd is None:
                        return await ctx.send(f"{self.bot.settings['formats']['error']} **Unknown Command:** The "
                                              f"`{command}` command does not exist.")
                    else:
                        embed.add_field(name=f"{self.bot.settings['emoji']['infoBook']} Help: {cmd.name}",
                                        value=f"Provides general information on the usage of what {cmd.name} does.",
                                        inline=False)
                        embed.add_field(name=f"{self.bot.settings['emoji']['notepad']} Aliases",
                                        value=", ".join(cmd.aliases) or "None")
                        embed.add_field(name=f"{self.bot.settings['emoji']['notepad']} Usage", value=cmd.usage)
                        embed.add_field(name=f"{self.bot.settings['emoji']['speech']} Information",
                                        value=f"```{cmd.help}```", inline=False)
                await ctx.send(embed=embed)
            else:
                if not ctx.guild:
                    colour = 0xFFFFFA
                else:
                    botGuildMember = await ctx.guild.fetch_member(self.bot.user.id)
                    if len(str(botGuildMember.colour.value)) == 1:
                        colour = 0xFFFFFA
                    else:
                        colour = botGuildMember.colour.value

                embed = discord.Embed(colour=colour)
                if not ctx.guild:
                    embed.add_field(name=f"{self.bot.settings['emoji']['home']} Help: Menu",
                                    value=f"Commands in DMs have no prefix, and you can execute them like so: `help`\n"
                                          f"To get command usage and information do `help <command>`\nClick [here]"
                                          f"({self.bot.settings['inviteURL']}) to join cairo's server.")
                else:
                    embed.add_field(name=f"{self.bot.settings['emoji']['home']} Help: Menu",
                                    value=f"All commands use the prefix `{'`, `'.join(self.bot.settings['prefix'])}` "
                                          f"or `@{self.bot.user}`")
                    embed.add_field(name=f"{self.bot.settings['emoji']['toolbox']} Utility Commands (5)",
                                    value="`ping`, `userinfo`, `botinfo`, `showbots`, `token`", inline=False)

                db_user: userTypes.DelUser = await self.bot.db.users.find_one({"_id": str(ctx.author.id)})
                if db_user and db_user["rank"]["mod"]:
                    embed.add_field(name=f"{self.bot.settings['emoji']['hammer']} Moderator Commands (3)",
                                    value="`open-ticket`, `awaiting-fixes`, `close-ticket`", inline=False)

                if self.bot.settings["ownership"]["multiple"]:
                    if ctx.author.id in self.bot.settings["ownership"]["owners"]:
                        embed.add_field(name=f"{self.bot.settings['emoji']['crown']} Admin Commands (2)",
                                        value="`jsk`, `admintoken`", inline=False)
                else:
                    if ctx.author.id == self.bot.settings["ownership"]["owner"]:
                        embed.add_field(name=f"{self.bot.settings['emoji']['crown']} Admin Commands (2)",
                                        value="`jsk`, `admintoken`", inline=False)

                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCog(bot))
