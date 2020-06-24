import discord
from discord.ext import commands
from discord.ext.commands import converter

def sig(command):
    if command.usage is not None:
        return command.usage

    params = command.clean_params
    if not params:
        return ''

    result = []
    for name, param in params.items():
        greedy = isinstance(param.annotation, converter._Greedy)

        if param.default is not param.empty:
            # We don't want None or '' to trigger the [name=value] case and instead it should
            # do [name] since [name=None] or [name=] are not exactly useful for the user.
            should_print = param.default if isinstance(param.default, str) else param.default is not None
            if should_print:
                result.append('[%s]' % name)
                continue
            else:
                result.append('[%s]' % name)

        elif param.kind == param.VAR_POSITIONAL:
            result.append('[%s...]' % name)
        elif greedy:
            result.append('[%s]...' % name)
        elif command._is_typing_optional(param.annotation):
            result.append('[%s]' % name)
        else:
            result.append('<%s>' % name)

    return ' '.join(result)

class Help(commands.HelpCommand):
    def common_command_formatting(self, page_or_embed, command, issub=False):
        title = self.get_command_signature(command)
        if command.description:
            desc = f'{command.description}\n\n{command.help}'
        else:
            desc = command.help or 'No help found...'

        if issub:
            page_or_embed.add_field(name=title, value=desc)
        else:
            page_or_embed.title = title
            page_or_embed.description = desc

    def command_not_found(self, string):
        return f"Nope, no {string} command found here"

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {sig(command)}'

    async def send_command_help(self, command):
        if command.hidden:
            return await self.context.send(self.command_not_found(command.qualified_name))

        embed = discord.Embed(colour=discord.Colour.teal())
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        if group.hidden:
            return await self.context.send(self.command_not_found(group.qualified_name))

        subcommands = list(group.commands)
        embed = discord.Embed(colour=discord.Colour.teal())
        self.common_command_formatting(embed, group)
        for cmd in subcommands:
            self.common_command_formatting(embed, cmd, issub=True)

    async def send_cog_help(self, cog: commands.Cog):
        embed = discord.Embed(colour=discord.Colour.teal())
        subs = cog.get_commands()

        embed.title = f'{cog.qualified_name} Commands'
        desc = ""

        for command in subs:
            desc += "**" + self.get_command_signature(command) + "**\n"
            desc += command.short_doc
            desc += "\n\n"

        embed.description = desc
        await self.context.send(embed=embed)

def setup(bot):
    bot.help_command = Help()
