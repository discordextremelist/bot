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

import json

import discord
from discord.ext import commands

from .types import userTypes

with open("settings.json") as content:
    settings = json.load(content)


class BotClass:
    settings = settings


class HelpCommand(commands.HelpCommand):

    def __init__(self, *args, **kwargs):
        self.bot = BotClass
        self.show_hidden = False
        self.verify_checks = True

        self.mod_cogs = ["Tickets", "Notes"]
        self.admin_cogs = ["Admin", "Jishaku"]
        self.jishaku_under_cog = "Admin"
        self.ignore_cogs = ["Events"]

        super().__init__(command_attrs={
            "help": "Shows the help about the bot and/or commands.",
            "brief": "See cog/command help",
            "usage": "[category / command]",
            "name": "help"
        })

    async def embed_colour(self, ctx):
        global colour

        bot_guild_member = await ctx.guild.fetch_member(ctx.bot.user.id)
        if len(str(bot_guild_member.colour.value)) == 1:
            colour = 0xFFFFFA
        else:
            colour = bot_guild_member.colour.value

        return colour

    def get_command_signature(self, command):
        return command.qualified_name

    async def command_callback(self, ctx, *, command=None):
        """|coro|
        The actual implementation of the help command.
        It is not recommended to override this method and instead change
        the behaviour through the methods that actually get dispatched.
        - :meth:`send_bot_help`
        - :meth:`send_cog_help`
        - :meth:`send_group_help`
        - :meth:`send_command_help`
        - :meth:`get_destination`
        - :meth:`command_not_found`
        - :meth:`subcommand_not_found`
        - :meth:`send_error_message`
        - :meth:`on_help_command_error`
        - :meth:`prepare_help_command`
        """

        await self.prepare_help_command(ctx, command)

        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        # Check if it's a cog
        cog = ctx.bot.get_cog(command.title())
        if command.title().lower() != "jishaku":
            if cog is not None:
                return await self.send_cog_help(cog)
        else:
            return await self.send_group_help(ctx.bot.get_command("jishaku"))

        maybe_coro = discord.utils.maybe_coroutine

        # If it's not a cog then it's a command.
        # Since we want to have detailed errors when someone
        # passes an invalid subcommand, we need to walk through
        # the command group chain ourselves.
        keys = command.split(' ')
        cmd = ctx.bot.all_commands.get(keys[0])
        if cmd is None:
            string = await maybe_coro(self.command_not_found, self.remove_mentions(keys[0]))
            return await self.send_error_message(string)

        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)
            except AttributeError:
                string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
                return await self.send_error_message(string)
            else:
                if found is None:
                    string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
                    return await self.send_error_message(string)
                cmd = found

        if isinstance(cmd, commands.Group):
            return await self.send_group_help(cmd)
        else:
            return await self.send_command_help(cmd)

    async def send_bot_help(self, mapping):
        """
        Sends bot help.
        """

        embed = discord.Embed(color=await self.embed_colour(self.context))
        embed.title = f"{self.context.bot.settings['emoji']['home']} Help: Menu"
        embed.description = f"All commands use the prefix `{self.bot.settings['prefix'][0]}` or " \
                            f"`@{str(self.context.bot.user)}`."

        for extension in self.context.bot.cogs.values():
            if extension.qualified_name in self.ignore_cogs:
                continue

            db_user: userTypes.DelUser = await self.context.bot.db.users.find_one({"_id": str(self.context.author.id)})

            if db_user:
                if extension.qualified_name in self.mod_cogs and not db_user["rank"]["mod"]:
                    continue

                if extension.qualified_name in self.admin_cogs and not db_user["rank"]["admin"]:
                    continue
            else:
                if extension.qualified_name in self.mod_cogs or extension.qualified_name in self.admin_cogs:
                    continue

            extension_commands = ""

            for command in set(extension.get_commands()):
                if not command.hidden:
                    mod = False
                    for check in command.checks:
                        if check.__qualname__.startswith("mod_check"):
                            mod = True

                    if mod and db_user:
                        if db_user["rank"]["mod"]:
                            if len(extension_commands) == 0:
                                extension_commands += f"`{command.qualified_name}`"
                            else:
                                extension_commands += f", `{command.qualified_name}`"
                        else:
                            continue
                    elif mod and not db_user:
                        continue
                    else:
                        if len(extension_commands) == 0:
                            extension_commands += f"`{command.qualified_name}`"
                        else:
                            extension_commands += f", `{command.qualified_name}`"
                else:
                    continue

            if extension.qualified_name == self.jishaku_under_cog:
                jsk_extension = self.context.bot.get_cog("Jishaku")
                if not jsk_extension.jsk.hidden:
                    extension_commands += ", `jishaku`"

            embed.add_field(name=f"{extension.help_icon} {extension.qualified_name}", value=extension_commands,
                            inline=False)

        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        """
        Sends help for a specific command.
        """

        db_user: userTypes.DelUser = await self.context.bot.db.users.find_one({"_id": str(self.context.author.id)})

        if db_user:
            if command.cog_name in self.ignore_cogs:
                return await self.send_error_message(self.command_not_found(command.name))

            if command.cog_name in self.mod_cogs and not db_user["rank"]["mod"]:
                return await self.send_error_message(self.command_not_found(command.name))

            if self.context.bot.settings["ownership"]["multiple"]:
                if command.cog_name in self.admin_cogs and self.context.author.id not in \
                        self.bot.settings["ownership"]["owners"]:
                    return await self.send_error_message(self.command_not_found(command.name))
            else:
                if command.cog_name in self.admin_cogs and self.context.author.id != \
                        self.bot.settings["ownership"]["owner"]:
                    return await self.send_error_message(self.command_not_found(command.name))

            if command.hidden:
                return await self.send_error_message(self.command_not_found(command.name))
        else:
            pass

        aliases = '`' + '`, `'.join(command.aliases) + "`"

        if aliases == "``" or aliases == '`':
            aliases = "No aliases were found."

        if command.help:
            description = str(command.help)
        else:
            description = "No description provided."

        command.help_icon = self.bot.settings["emoji"]["info"]
        command.help_name = command.qualified_name

        embed = discord.Embed(description=description, colour=await self.embed_colour(self.context))
        embed.title = f"{command.help_icon} Help: {command.help_name}"
        embed.add_field(name="Usage", value=f"{self.clean_prefix}{command.signature}")
        embed.add_field(name="Aliases", value=aliases)

        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        """
        Sends help for a specific group.
        """

        db_user: userTypes.DelUser = await self.context.bot.db.users.find_one({"_id": str(self.context.author.id)})

        if db_user:
            if group.cog_name in self.ignore_cogs:
                return await self.send_error_message(self.command_not_found(group.name))

            if group.cog_name in self.mod_cogs and not db_user["rank"]["mod"]:
                return await self.context.channel.send(f"{self.bot.settings['formats']['noPerms']} **Invalid "
                                                       f"permission(s):** The specified command requires you to have "
                                                       f"Moderator permissions to access.")

            if self.context.bot.settings["ownership"]["multiple"]:
                if group.cog_name in self.admin_cogs and self.context.author.id not in \
                        self.bot.settings["ownership"]["owners"] and not db_user["rank"]["admin"]:
                    return await self.context.channel.send(f"{self.bot.settings['formats']['noPerms']} **Invalid "
                                                           f"permission(s):** The specified command requires you to "
                                                           f"have Administrator permissions to access.")
            else:
                if group.cog_name in self.admin_cogs and self.context.author.id != \
                        self.bot.settings["ownership"]["owner"] and not db_user["rank"]["admin"]:
                    return await self.context.channel.send(f"{self.bot.settings['formats']['noPerms']} **Invalid "
                                                           f"permission(s):** The specified command requires you to "
                                                           f"have Administrator permissions to access.")

            if group.hidden:
                return await self.send_error_message(self.command_not_found(group.name))
        else:
            pass

        sub_commands = ""

        for group_command in group.commands:
            sub_commands += '`' + group_command.name + f'`, '

        aliases = "`" + '`, `'.join(group_command.root_parent.aliases) + '`'

        if aliases == "``":
            aliases = "No aliases were found."

        if group_command.root_parent == self.context.bot.get_command("jishaku"):
            cmd_signature = "jishaku [subCommand]"
        else:
            cmd_signature = group_command.root_parent

        if group_command.root_parent.help:
            description = str(group_command.root_parent.help)
        else:
            description = "No help provided."

        group.help_icon = self.bot.settings["emoji"]["info"]
        group.help_name = self.get_command_signature(group_command.root_parent)

        if group.cog_name.lower() == "jishaku":
            group.help_icon = self.bot.settings["emoji"]["coder"]
            group.help_name = "Jishaku"

        embed = discord.Embed(description=description, colour=await self.embed_colour(self.context))
        embed.title = f"{group.help_icon} Help: {group.help_name}"
        embed.add_field(name="Usage", value=f"{self.clean_prefix}{cmd_signature}")
        embed.add_field(name="Aliases", value=aliases)
        embed.add_field(name=f"Subcommands ({len(group.commands)})", value=sub_commands[:-2], inline=False)

        await self.context.send(embed=embed)

    async def send_cog_help(self, cog):
        """
        Sends help for a specific cog.
        """

        db_user: userTypes.DelUser = await self.context.bot.db.users.find_one({"_id": str(self.context.author.id)})

        if db_user:
            if cog.qualified_name in self.ignore_cogs:
                return await self.send_error_message(self.command_not_found(cog.qualified_name))

            if cog.qualified_name in self.mod_cogs and not db_user["rank"]["mod"]:
                return await self.context.channel.send(f"{self.bot.settings['formats']['noPerms']} **Invalid "
                                                       f"permission(s):** The specified cog requires you to have "
                                                       f"Moderator permissions to access.")

            if self.context.bot.settings["ownership"]["multiple"]:
                if cog.qualified_name in self.admin_cogs and self.context.author.id not in \
                        self.bot.settings["ownership"]["owners"] and not db_user["rank"]["admin"]:
                    return await self.context.channel.send(f"{self.bot.settings['formats']['noPerms']} **Invalid "
                                                           f"permission(s):** The specified cog requires you to have "
                                                           f"Administrator permissions to access.")
            else:
                if cog.qualified_name in self.admin_cogs and self.context.author.id != \
                        self.bot.settings["ownership"]["owner"] and not db_user["rank"]["admin"]:
                    return await self.context.channel.send(f"{self.bot.settings['formats']['noPerms']} **Invalid "
                                                           f"permission(s):** The specified cog requires you to have "
                                                           f"Administrator permissions to access.")
        else:
            pass

        cog_commands = ""
        for command in cog.get_commands():
            if command.hidden:
                continue
            if command.description is None:
                brief = "No information."
            else:
                brief = command.description

            cog_commands += f"`{command.qualified_name}` - {brief}\n"

        if cog.qualified_name == "Jishaku":
            cog.help_icon = self.bot.settings["emoji"]["coder"]
            cog_commands += f"*For information on the command type:* `{self.bot.settings['prefix'][0]}help jsk`."
        elif cog.qualified_name == self.jishaku_under_cog:
            jsk_extension = self.context.bot.get_cog("Jishaku")
            if not jsk_extension.jsk.hidden:
                cog_commands += "`jishaku` - The Jishaku debug and diagnostic commands."

        embed = discord.Embed(description=cog_commands, colour=await self.embed_colour(self.context))
        embed.title = f"{cog.help_icon} Help: {cog.qualified_name} ({len(cog.get_commands())})"

        await self.context.send(embed=embed)

    def command_not_found(self, string):
        return f"{self.bot.settings['formats']['error']} **Not found:** No command or cog called " \
               f"**\"**{discord.utils.escape_markdown(string, as_needed=False)}**\"** found."


def setup(bot):
    bot.help_command = HelpCommand()
