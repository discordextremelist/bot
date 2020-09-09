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

def setup(bot):
    bot.help_command = HelpCommand()

class HelpCommand(commands.HelpCommand):
    def __init__(self, *args, **kwargs):
        self.show_hidden = False
        super().__init__(command_attrs={
	    		'help': 'Shows help about bot and/or commands',
                'brief': 'See cog/command help',
                'usage': '[category / command]',
                'cooldown': commands.Cooldown(1, 3, commands.BucketType.user),
                'name': 'help'})
        self.verify_checks = True
        

        self.admin_cogs = [] # Do you even have admin cog? If not then I cannot change this
        self.mog_cogs = ['TicketCog']
        self.ignore_cogs = ["Events"] # Add cogs here that you don't want to be displayed in the help menu
    
    def get_command_signature(self, command):
        return f"{self.bot.settings['emoji']['infoBook']} Help: {command.qualified_name}"

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
        bot = ctx.bot

        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        # Check if it's a cog
        cog = ctx.bot.get_cog(command.title())
        if cog is not None:
            return await self.send_cog_help(cog)

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
        """ See bot help """

        emb = discord.Embed(color=self.context.author.colour)
        emb.description = 'All commands use the prefix `del,` or `@Delly#7185`'

        exts = ""
        for extension in self.context.bot.cogs.values():
            if extension.qualified_name in self.ignore_cogs:
                continue
            if extension.qualified_name == "Jishaku":
                continue
            db_user: userTypes.DelUser = await self.context.bot.db.users.find_one({"_id": str(self.context.author.id)})
            if db_user:
                if extension.qualified_name in self.mod_cogs and not db_user["rank"]["mod"]:
                    continue
            else:
                if extension.qualified_name in self.mod_cogs:
                    continue
            c = f"`" + f"`, `".join([c.qualified_name for c in set(extension.get_commands()) if not c.hidden]) + '`'
            exts += f"{extension.help_icon} **{extension.qualified_name}**\n{c}"

        emb.description += f'\n{exts}'
        emb.title = f"{self.context.bot.settings['emoji']['home']} Help Menu"
        await self.context.send(embed=emb)

    async def send_command_help(self, command):
        db_user: userTypes.DelUser = await self.context.bot.db.users.find_one({"_id": str(self.context.author.id)})
        if db_user:
            if command.cog_name in self.ignore_cogs:
                return await self.send_error_message(self.command_not_found(command.name))
            if command.cog_name in self.mod_cogs and not db_user["rank"]["mod"]: 
                return await self.send_error_message(self.command_not_found(command.name))  
            if self.context.bot.settings["ownership"]["multiple"]:
                if command.cog_name in self.admin_cogs and not self.context.author.id in self.bot.settings["ownership"]["owners"]:
                    return await self.send_error_message(self.command_not_found(command.name))
            else:
                if command.cog_name in self.admin_cogs and self.context.author.id != self.bot.settings["ownership"]["owner"]:
                    return await self.send_error_message(self.command_not_found(command.name))
            if command.hidden == True:
                return await self.send_error_message(self.command_not_found(command.name))
        else:
            pass

        aliases = '`' + '`, `'.join(command.aliases) + "`"
        if aliases == "``" or aliases == '`':
            aliases = "No aliases were found" 
        if command.help:
            desc = f"{command.help}"
        else:
            desc = "No help provided..."
        emb = discord.Embed(escription=desc, colour=self.context.author.colour)
        emb.title = self.get_command_signature(command)
        emb.add_field(name="Usage:\n", value=f"{self.clean_prefix}{command.qualified_name} {command.signature}")
        emb.add_field(name="Aliases:\n", value=aliases)
        await self.context.send(embed=emb)
        
    async def send_group_help(self, group):          
        db_user: userTypes.DelUser = await self.context.bot.db.users.find_one({"_id": str(self.context.author.id)})
        if db_user:
            if group.cog_name in self.ignore_cogs:
                return await self.send_error_message(self.command_not_found(group.name))
            if group.cog_name in self.mod_cogs and not db_user["rank"]["mod"]: 
                return await self.send_error_message(self.command_not_found(group.name)) 
            if self.context.bot.settings["ownership"]["multiple"]:
                if group.cog_name in self.admin_cogs and not self.context.author.id in self.bot.settings["ownership"]["owners"]:
                    return await self.send_error_message(self.command_not_found(group.name))
            else:
                if group.cog_name in self.admin_cogs and self.context.author.id != self.bot.settings["ownership"]["owner"]:
                    return await self.send_error_message(self.command_not_found(group.name))
            if command.hidden == True:
                return await self.send_error_message(self.command_not_found(group.name))
        else:
            pass
        
        sub_cmd_list = ""
        for group_command in group.commands:
            sub_cmd_list += '' + group_command.name + f', '
        aliases = "`" + '`, `'.join(group_command.root_parent.aliases) + "`"     
        if aliases == "``":
            aliases = "No aliases were found"
        if group_command.root_parent == self.context.bot.get_command('jishaku'):
            cmdsignature = 'jishaku [subCommand]'  
        else:  
            cmdsignature = group_command.root_parent

        if group_command.root_parent.help:
            desc = f"{group_command.root_parent.help}"
        else:
            desc = "No help provided..."

        emb = discord.Embed(description=f"**Information:**\n{desc}", colour=self.context.author.colour)
        emb.title = self.get_command_signature(group_command.root_parent)
        emb.add_field(name="Usage:\n", value=f"{self.clean_prefix}{cmdsignature}")
        emb.add_field(name="Aliases:\n", value=aliases)
        emb.add_field(name=f"Subcommands: ({len(group.commands)})", value=sub_cmd_list[:-2], inline=False)
        
        await self.context.send(embed=emb)

    async def send_cog_help(self, cog):
        db_user: userTypes.DelUser = await self.context.bot.db.users.find_one({"_id": str(self.context.author.id)})
        if db_user:
            if cog.qualified_name in self.ignore_cogs:
                return await self.send_error_message(self.command_not_found(cog.qualified_name.lower()))
            if cog.qualified_name in self.mod_cogs and not db_user["rank"]["mod"]: 
                return await self.send_error_message(self.command_not_found(cog.qualified_name.lower())) 
            if self.context.bot.settings["ownership"]["multiple"]:
                if cog.qualified_name in self.admin_cogs and not self.context.author.id in self.bot.settings["ownership"]["owners"]:
                    return await self.send_error_message(self.command_not_found(cog.qualified_name.lower()))
            else:
                if cog.qualified_name in self.admin_cogs and self.context.author.id != self.bot.settings["ownership"]["owner"]:
                    return await self.send_error_message(self.command_not_found(cog.qualified_name.lower()))
        else:
            pass

        commands = ""
        for cmd in cog.get_commands():
            if cmd.hidden:
                continue
            if cmd.short_doc is None:
                brief = 'No info'
            else:
                brief = cmd.short_doc
            commands += f"`{cmd.qualified_name}` - {brief}\n"
        
        e = discord.Embed(title=f"{cog.help_icon} Help: {cog.qualified_name} ({len(cog.get_commands())})")
        e.description=commands
        await self.context.send(embed=e)

    def command_not_found(self, string):
        return 'No command called "{}" found.'.format(string)
