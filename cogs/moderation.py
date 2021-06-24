import discord
import traceback
import typing

from discord.ext import commands
from ext.default import FutureTime
from ext.checks import mod_check
from contextlib import suppress
from ext.checks import *

from discord_slash import cog_ext, SlashContext


class MemberID(commands.Converter):  # For hackban
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument("User needs to be an ID")
        elif argument.isdigit():
            member_id = int(argument, base=10)
            try:
                ban_check = await ctx.guild.fetch_ban(discord.Object(id=member_id))
                if ban_check:
                    raise commands.BadArgument("This user is already banned.") from None
            except discord.NotFound:
                return type('_Hackban', (), {'id': argument, '__str__': lambda s: s.id})()


class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument("This member has not been banned before.") from None

        elif not argument.isdigit():
            ban_list = await ctx.guild.bans()
            entity = discord.utils.find(lambda u: str(u.user.name) == argument, ban_list)
            if entity is None:
                raise commands.BadArgument("This member has not been banned before.")
            return entity


# Credits: https://github.com/dredd-bot/Dredd/blob/master/cogs/moderation.py and @TheMoksej
class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.help_icon = f"{self.bot.settings['emoji']['hammer']}"

    @commands.command(description="Kick someone from the server", usage='kick <members> [reason]')
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason: str = None):
        """
        Kicks member from server.
        You can also provide multiple members to kick.
        """

        if not members:
            raise commands.MissingRequiredArgument(self.kick.params['members'])

        try:
            if len(members) > 10:
                return await ctx.send("You can only kick 10 scumbags at once!")

            if reason and len(reason) > 500:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Reason too long:** reason can only be 500 characters long, "
                                      f"you're over by {len(reason) - 500}.")

            failed = 0
            failed_list = []
            success_list = []
            for member in members:
                if member == ctx.author:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - you can't kick yourself, you can leave though.")
                    continue
                if member.top_role.position >= ctx.author.top_role.position:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - kicking someone higher than you or who has the same role is cringe, so no.")
                    continue
                if member.top_role.position >= ctx.guild.me.top_role.position:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - seems like the person is higher than me or has the same role, also cringe.")
                    continue
                try:
                    await ctx.guild.kick(member, reason=f"Mod: {ctx.author} ({ctx.author.id}) - {reason or 'No reason'}")
                    success_list.append(f"{member} ({member.id})")
                except discord.HTTPException as e:
                    failed += 1
                    failed_list.append(f"{member} - {e}")
                except discord.Forbidden as e:
                    failed += 1
                    failed_list.append(f"{member} - {e}")
            kicked = ""
            notkicked = ""
            if success_list and not failed_list:
                kicked += f"{self.bot.settings['formats']['success']} **Scumbag(s) kicked:** Successfully kicked {len(success_list)} scumbag(s):\n"
                for num, res in enumerate(success_list, start=0):
                    kicked += f"`[{num+1}]` {res}\n"
                await ctx.send(kicked)
            if success_list and failed_list:
                kicked += f"{self.bot.settings['formats']['success']} **Scumbag(s) banned:** Successfully kicked {len(success_list) - failed} scumbag(s):\n"
                notkicked += f"{self.bot.settings['formats']['error']} **Scumbag(s) not kicked:** However I failed to kick the following " \
                             f"{failed_list} scumbag(s)\n"
                for num, res in enumerate(success_list, start=0):
                    kicked += f"`[{num+1}]` {res}\n"
                for num, res in enumerate(failed_list, start=0):
                    notkicked += f"`[{num+1}]` {res}\n"
                await ctx.send(kicked + notkicked)
            if not success_list and failed_list:  
                notmuted += f"**I failed to kick all the scumbags:**\n"
                for num, res in enumerate(failed_list, start=0):
                    notkicked += f"`[{num+1}]` {res}\n"
                await ctx.send(notkicked)
        except Exception as exc:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Error occured:**\n```py\n"
                                  f"{''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}```")

    @commands.command(description="Ban someone from the server", aliases=['tempban', 'massban'],
                      usage='ban <members> [duration] [reason]')
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], duration: typing.Optional[FutureTime], *, reason: str = None):
        """
        Ban members from the server.
        """

        if not members:
            raise commands.MissingRequiredArgument(self.ban.params['members'])

        try:
            total = len(members)
            if total > 10:
                return await ctx.send("You can only ban 10 scumbags at once!")

            if reason and len(reason) > 500:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Reason too long:** reason can only be 500 characters long, "
                                      f"you're over by {len(reason) - 500}.")

            failed = 0
            failed_list = []
            success_list = []
            for member in members:
                if member == ctx.author:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - you can't ban yourself, you can leave though.")
                    continue
                if member.top_role.position >= ctx.author.top_role.position:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - banning someone higher than you or who has the same role is cringe, so no.")
                    continue
                if member.top_role.position >= ctx.guild.me.top_role.position:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - seems like the person is higher than me or has the same role, also cringe.")
                    continue
                try:
                    await ctx.guild.ban(member, reason=f"Mod: {ctx.author} ({ctx.author.id}) - {reason or 'No reason'}", delete_message_days=0)
                    await self.bot.db.bans.insert_one({
                        "_id": str(member.id),
                        "duration": duration.dt if duration else None,
                        "moderator": str(ctx.author.id)
                    })
                    success_list.append(f"{member} ({member.id})")
                except discord.HTTPException as e:
                    failed += 1
                    failed_list.append(f"{member} - {e}")
                    continue
                except discord.Forbidden as e:
                    failed += 1
                    failed_list.append(f"{member} - {e}")
                    continue

            banned = ""
            notbanned = ""
            if success_list and not failed_list:
                banned += f"{self.bot.settings['formats']['success']} **Scumbag(s) banned:** Successfully banned {len(success_list)} scumbag(s):\n"
                for num, res in enumerate(success_list, start=0):
                    banned += f"`[{num+1}]` {res}\n"
                await ctx.send(banned)
            if success_list and failed_list:
                banned += f"{self.bot.settings['formats']['success']} **Scumbag(s) banned:** Successfully banned {len(success_list)} scumbag(s):\n"
                notbanned += f"{self.bot.settings['formats']['error']} **Scumbag(s) not banned:** However I failed to ban the following " \
                             f"{failed} scumbag(s)\n"
                for num, res in enumerate(success_list, start=0):
                    banned += f"`[{num+1}]` {res}\n"
                for num, res in enumerate(failed_list, start=0):
                    notbanned += f"`[{num+1}]` {res}\n"
                await ctx.send(banned + notbanned)
            if not success_list and failed_list:
                notbanned += f"{self.bot.settings['formats']['error']} **Scumbag(s) not banned:** I failed to ban all the scumbags:\n"
                for num, res in enumerate(failed_list, start=0):
                    notbanned += f"`[{num+1}]` {res}\n"
                await ctx.send(notbanned)
                    
        except Exception as exc:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Error occured:**\n```py\n"
                                  f"{''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}```")

    @commands.command(description='Hackban user(s) from the server', aliases=['hack-ban', 'masshackban'],
                      usage='hackban <user(s)> [reason]')
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def hackban(self, ctx, users: commands.Greedy[MemberID], *, reason: commands.clean_content = None):
        """
        Hack-ban a user who's not in the server from the server
        Users must be IDs else it won't work.
        """

        if not users:
            raise commands.MissingRequiredArgument(self.hackban.params['users'])

        if len(users) > 20:
            return await ctx.send("You can only hack-ban 20 users at once.")

        if reason and len(reason) > 500:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Reason too long:** reason can only be 500 characters long, "
                                  f"you're over by {len(reason) - 500}.")

        failed, success, fail_count, suc_count, banned = [], [], 0, 0, []
        await ctx.send("Starting the process, this might take a while.")
        for user in users:
            with suppress(Exception):
                m = await commands.MemberConverter().convert(ctx, str(user))
                if m is not None:
                    failed.append(f"{user} ({user.id}) - This scumbag is in this server, use `ban` command instead.")
                    fail_count += 1
                    continue
            try:
                user = await self.bot.fetch_user(user)
            except Exception:
                failed.append(f"{user} - This scumbag doesn't seem to exist, are you sure the ID is correct?")
                fail_count += 1
                continue
            await ctx.guild.ban(user, reason=f"Mod: {ctx.author} ({ctx.author.id}) - {reason or 'No reason'}", delete_message_days=0)
            success.append(_("{0} ({0.id})").format(user))
            banned.append(user)
            suc_count += 1

        try:
            booted, not_booted = "", ""
            if success and not failed:
                booted += f"{self.bot.settings['formats']['success']} **Scumbag(s) banned:** Successfully hack-banned {suc_count} scumbag(s):\n"
                for num, res in enumerate(success, start=0):
                    booted += f"`[{num+1}]` {res}\n"
                await ctx.send(booted)
                self.bot.dispatch('hackban', ctx.guild, ctx.author, banned, reason)
            if success and failed:
                booted += f"{self.bot.settings['formats']['success']} **Scumbag(s) banned:** Successfully hack-banned {suc_count} scumbag(s):\n"
                not_booted += f"{self.bot.settings['formats']['error']} **Scumbag(s) not banned:** However I failed to hack-ban the following " \
                              f"{failed} scumbag(s)\n"
                for num, res in enumerate(success, start=0):
                    booted += f"`[{num+1}]` {res}\n"
                for num, res in enumerate(failed, start=0):
                    not_booted += f"`[{num+1}]` {res}\n"
                await ctx.send(booted + not_booted)
                self.bot.dispatch('hackban', ctx.guild, ctx.author, banned, reason)
            if not success and failed:
                not_booted += f"{self.bot.settings['formats']['error']} **Scumbag(s) not banned:** I failed to hack-ban all the scumbags:\n"
                for num, res in enumerate(failed, start=0):
                    not_booted += f"`[{num+1}]` {res}\n"
                await ctx.send(not_booted)
        except Exception as e:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Error occured:**\n```py\n"
                                  f"{''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}```")

    @commands.command(name="mute", aliases=["tempmute"], description="Mute member(s) in the server",
                      usage="mute <member(s)> [duration] [reason]")
    @mod_check()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def mute(self, ctx, members: commands.Greedy[discord.Member], duration: typing.Optional[FutureTime], *, reason: str = None):
        """
        Mute member(s) in the server
        """
        if not members:
            raise commands.MissingRequiredArgument(self.mute.params['members'])

        muterole = discord.utils.find(lambda m: m.name.lower() == "public mute", ctx.guild.roles)
        if not muterole:
            return await ctx.channel.send(f"{self.bot.settings['formats']['errors']} **Mute role missing:** The mute role "
                                          f"is either missing in this server or isn't named `public mute`")
        elif muterole and muterole.position > ctx.guild.me.top_role.position:
            return await ctx.channel.send(f"{self.bot.settings['formats']['errors']} **Mute role unaccessible:** The mute role "
                                          f"is higher than me, please lower it down or put my role higher in the role hierarchy!")

        try:
            total = len(members)
            if total > 10:
                return await ctx.send("You can only mute 10 scumbags at once!")

            if reason and len(reason) > 500:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Reason too long:** reason can only be 500 characters long, "
                                      f"you're over by {len(reason) - 500}.")

            failed = 0
            failed_list = []
            success_list = []
            for member in members:
                if member == ctx.author:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - why would you want to mute yourself?")
                    continue
                if member.top_role.position >= ctx.author.top_role.position:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - muting someone higher than you or who has the same role is cringe, so no.")
                    continue
                if member.top_role.position >= ctx.guild.me.top_role.position:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - seems like the person is higher than me or has the same role, also cringe.")
                    continue
                if muterole in member.roles:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - the scumbag is already muted.")
                    continue
                try:
                    await member.add_roles(muterole, reason=f"Mod: {ctx.author} ({ctx.author.id}) - {reason or 'No reason'}")
                    await self.bot.db.mutes.insert_one({
                        "_id": str(member.id),
                        "duration": duration.dt if duration else None,
                        "moderator": str(ctx.author.id)
                    })
                    success_list.append(f"{member} ({member.id})")
                except discord.HTTPException as e:
                    failed += 1
                    failed_list.append(f"{member} - {e}")
                    continue
                except discord.Forbidden as e:
                    failed += 1
                    failed_list.append(f"{member} - {e}")
                    continue

            muted = ""
            notmuted = ""
            if success_list and not failed_list:
                muted += f"{self.bot.settings['formats']['success']} **Scumbag(s) muted:** Successfully muted {len(success_list)} scumbag(s):\n"
                for num, res in enumerate(success_list, start=0):
                    muted += f"`[{num + 1}]` {res}\n"
                await ctx.send(muted)
            if success_list and failed_list:
                muted += f"{self.bot.settings['formats']['success']} **Scumbag(s) muted:** Successfully muted {len(success_list)} scumbag(s):\n"
                notmuted += f"{self.bot.settings['formats']['error']} **Scumbag(s) not muted:** However I failed to unmute the following " \
                            f"{failed} scumbag(s)\n"
                for num, res in enumerate(success_list, start=0):
                    muted += f"`[{num + 1}]` {res}\n"
                for num, res in enumerate(failed_list, start=0):
                    notmuted += f"`[{num + 1}]` {res}\n"
                await ctx.send(muted + notmuted)
            if not success_list and failed_list:
                notmuted += f"{self.bot.settings['formats']['error']} **Scumbag(s) not unmuted:** I failed to unmute all the scumbags:\n"
                for num, res in enumerate(failed_list, start=0):
                    notmuted += f"`[{num + 1}]` {res}\n"
                await ctx.send(notmuted)

        except Exception as exc:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Error occured:**\n```py\n"
                                  f"{''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}```")

    @commands.command(name="unmute", aliases=["untempmute"], description="Mute member(s) in the server",
                      usage="unmute <member(s)> [duration] [reason]")
    @mod_check()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def unmute(self, ctx, members: commands.Greedy[discord.Member], duration: typing.Optional[FutureTime], *, reason: str = None):
        """
        Mute member(s) in the server
        """
        if not members:
            raise commands.MissingRequiredArgument(self.unmute.params['members'])

        muterole = discord.utils.find(lambda m: m.name.lower() == "public mute", ctx.guild.roles)

        if not muterole:
            return await ctx.channel.send(f"{self.bot.settings['formats']['errors']} **Mute role missing:** The mute role "
                                          f"is either missing in this server or isn't named `public mute`")
        elif muterole and muterole.position > ctx.guild.me.top_role.position:
            return await ctx.channel.send(f"{self.bot.settings['formats']['errors']} **Mute role unaccessible:** The mute role "
                                          f"is higher than me, please lower it down or put my role higher in the role hierarchy!")

        try:
            total = len(members)
            if total > 10:
                return await ctx.send("You can only unmute 10 scumbags at once!")

            if reason and len(reason) > 500:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Reason too long:** reason can only be 500 characters long, "
                                      f"you're over by {len(reason) - 500}.")

            failed = 0
            failed_list = []
            success_list = []
            for member in members:
                if member == ctx.author:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - you can't unmute yourself, but wait! How did you run this command?")
                    continue
                if member.top_role.position >= ctx.author.top_role.position:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - unmuting someone higher than you or who has the same role is cringe, so no.")
                    continue
                if member.top_role.position >= ctx.guild.me.top_role.position:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - seems like the person is higher than me or has the same role, also cringe.")
                    continue
                if muterole not in member.roles:
                    failed += 1
                    failed_list.append(f"{member} ({member.id}) - the scumbag is not muted.")
                    continue
                try:
                    await member.add_roles(muterole, reason=f"Mod: {ctx.author} ({ctx.author.id}) - {reason or 'No reason'}")
                    await self.bot.db.mutes.insert_one({
                        "_id": str(member.id),
                        "duration": duration.dt if duration else None,
                        "moderator": str(ctx.author.id)
                    })
                    success_list.append(f"{member} ({member.id})")
                except discord.HTTPException as e:
                    failed += 1
                    failed_list.append(f"{member} - {e}")
                    continue
                except discord.Forbidden as e:
                    failed += 1
                    failed_list.append(f"{member} - {e}")
                    continue

            muted = ""
            notmuted = ""
            if success_list and not failed_list:
                muted += f"{self.bot.settings['formats']['success']} **Scumbag(s) unmuted:** Successfully unmuted {len(success_list)} scumbag(s):\n"
                for num, res in enumerate(success_list, start=0):
                    muted += f"`[{num + 1}]` {res}\n"
                await ctx.send(muted)
            if success_list and failed_list:
                muted += f"{self.bot.settings['formats']['success']} **Scumbag(s) unmuted:** Successfully unmuted {len(success_list)} scumbag(s):\n"
                notmuted += f"{self.bot.settings['formats']['error']} **Scumbag(s) not unmuted:** However I failed to unmute the following " \
                            f"{failed} scumbag(s):\n"
                for num, res in enumerate(success_list, start=0):
                    muted += f"`[{num + 1}]` {res}\n"
                for num, res in enumerate(failed_list, start=0):
                    notmuted += f"`[{num + 1}]` {res}\n"
                await ctx.send(muted + notmuted)
            if not success_list and failed_list:
                notmuted += f"{self.bot.settings['formats']['error']} **Scumbag(s) not unmuted:** I failed to unmute all the scumbags:\n"
                for num, res in enumerate(failed_list, start=0):
                    notmuted += f"`[{num + 1}]` {res}\n"
                await ctx.send(notmuted)

        except Exception as exc:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Error occured:**\n```py\n"
                                  f"{''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}```")

    @commands.command(name="unban", description="Unban user from the server",
                      usage="unban <user> [reason]")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, user: BannedMember, reason: str = None):
        """
        Unban user from the server
        """

        if reason and len(reason) > 500:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Reason too long:** reason can only be 500 characters long, "
                                  f"you're over by {len(reason) - 500}.")

        try:
            await ctx.guild.unban(user.user, reason=f"Mod: {ctx.author} ({ctx.author.id}) - {reason or 'No reason'}")
            await ctx.send(f"{self.bot.settings['formats']['success']} **User unbanned:** Successfully unbanned **{0}** for **{1}**").format(
                user.user, 'No reason provided.' if reason is None else reason
            )
            await default.execute_untemporary(ctx, 1, banned_user.user, ctx.guild)
            self.bot.dispatch('unban', ctx.guild, ctx.author, [banned_user.user], reason)
        except Exception as exc:
            return await ctx.send(f"{self.bot.settings['formats']['error']} **Error occured:**\n```py\n"
                                  f"{''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}```")

    async def common_prefix_command(self, ctx, *, bot: discord.User):
        if not bot.bot:
            return await ctx.send("That's no bot")

        if ctx.guild.id == 667065302260908032:
            role = ctx.guild.get_role(int(settings["roles"]["commonPrefix"]))
            if role not in bot.roles:
                await bot.add_roles(role, reason=f"Mod - {ctx.author} ({ctx.author.id}) gave common prefix to the bot")
                await ctx.send(f"{self.bot.settings['formats']['success']} **Role added:** Added Common Prefix role to {bot}")
            elif role in bot.roles:
                await bot.remove_roles(role, reason=f"Mod - {ctx.author} ({ctx.author.id}) removed common prefix from the bot")
                await ctx.send(f"{self.bot.settings['formats']['success']} **Role removed:** Removed Common Prefix role from {bot}")

    @commands.command(name="common-prefix", aliases=["commonprefix", "common"],
                      description="Add or remove common prefix role to/from a bot.")
    @mod_check()
    @commands.guild_only()
    async def common_prefix(self, ctx, *, bot: discord.Member):
        await self.common_prefix_command(ctx, bot=bot)

    @cog_ext.cog_slash(name="common-prefix",
                       description="Add or remove common prefix role to/from a bot.",
                       options=[{"name": "bot", "description": "The bot to which you want to give the common prefix role or remove.",
                                 "type": 6, "required": True}],
                       guild_ids=[667065302260908032])
    @commands.guild_only()
    @mod_check()
    async def slash_common_prefix(self, ctx, *, bot: discord.Member):
        await self.common_prefix_command(ctx, bot=bot)


def setup(bot):
    bot.add_cog(Moderation(bot))
