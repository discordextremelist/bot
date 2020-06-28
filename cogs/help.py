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

class HelpCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", hidden=False)
    async def help(self, ctx, *, command: str = None):
        async with ctx.channel.typing():
            if command != None:
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
                    embed.add_field(name=f"{self.bot.settings['emoji']['infoBook']} Help: jishaku", value=f"Provides general information on the usage of what jishaku does.", inline=False)
                    embed.add_field(name=f"{self.bot.settings['emoji']['notepad']} Aliases", value="jsk")
                    embed.add_field(name=f"{self.bot.settings['emoji']['notepad']} Usage", value="jishaku <subCommand> <arguments>")
                    embed.add_field(name=f"{self.bot.settings['emoji']['speech']} Information", value=f"```The Jishaku debug and diagnostic commands.\n\nThis command on its own gives a status brief.\nAll other functionality is within its subcommands.```", inline=False)
                    embed.add_field(name=f"{self.bot.settings['emoji']['speech']} Sub-Commands", value="```py\ncancel \"Cancels a task with the given index.\"\ncat = \"Read out a file, using syntax highlighting if detected.\"\ncurl \"Download and display a text file from the internet.\"\ndebug \"Run a command timing execution and catching exceptions.\"\ngit \"Shortcut for \'jsk sh git\'. Invokes the system shell.\"\nhide \"Hides Jishaku from the help command.\"\nin \"Run a command as if it were run in a different channel.\"\nload \"Loads or reloads the given extension names.\"\npy \"Direct evaluation of Python code.\"\npy_inspect \"Evaluation of Python code with inspect information.\"```", inline=False)
                    embed.add_field(name="\u200B", value="```py\nrepeat \"Runs a command multiple times in a row.\"\nretain \"Turn variable retention for REPL on or off.\"\nshell \"Executes statements in the system shell.\"\nshow \"Shows Jishaku in the help command.\"\nshutdown \"Logs this bot out.\"\nsource \"Displays the source code for a command.\"\nsu \"Run a command as someone else.\"\nsudo \"Run a command bypassing all checks and cooldowns.\"\ntasks \"Shows the currently running jishaku tasks.\"\nunload \"Unloads the given extension names.\"\nvoice \"Voice-related commands.\"```", inline=False)
                else:
                    cmd = self.bot.get_command(command)

                    if cmd == None:
                        return await ctx.send(f"{self.bot.settings['formats']['error']} **Unknown Command:** The `{command}` command does not exist.")
                    else:
                        embed.add_field(name=f"{self.bot.settings['emoji']['infoBook']} Help: {cmd.name}", value=f"Provides general information on the usage of what {cmd.name} does.", inline=False)
                        embed.add_field(name=f"{self.bot.settings['emoji']['notepad']} Aliases", value=", ".join(cmd.aliases) or "None")
                        embed.add_field(name=f"{self.bot.settings['emoji']['notepad']} Usage", value=cmd.usage)
                        embed.add_field(name=f"{self.bot.settings['emoji']['speech']} Information", value=f"```{cmd.help}```", inline=False)
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
                    embed.add_field(name=f"{self.bot.settings['emoji']['home']} Help: Menu", value=f"Commands in DMs have no prefix, and you can execute them like so: `help`\nTo get command usage and information do `help <command>`\nClick [here]({self.bot.settings['inviteURL']}) to join cairo's server.")
                else:
                    embed.add_field(name=f"{self.bot.settings['emoji']['home']} Help: Menu", value=f"All commands use the prefix `{'`, `'.join(self.bot.settings['prefix'])}` or `@{self.bot.user}`")
                    embed.add_field(name=f"{self.bot.settings['emoji']['toolbox']} Utility Commands (4)", value="`ping`, `userinfo`, `botinfo`, `token`", inline=False)

                if self.bot.settings["ownership"]["multiple"]:
                    if ctx.author.id in self.bot.settings["ownership"]["owners"]:
                        embed.add_field(name=f"{self.bot.settings['emoji']['crown']} Admin Commands (1)", value="`jsk`, `admintoken`", inline=False)
                else:
                    if ctx.author.id == self.bot.settings["ownership"]["owner"]:
                        embed.add_field(name=f"{self.bot.settings['emoji']['crown']} Admin Commands (1)", value="`jsk`, `admintoken`", inline=False)

                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(HelpCog(bot))
