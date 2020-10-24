import discord
import re

from discord.ext import commands
from datetime import datetime, timezone

INVITE = re.compile(r"(?:https?://)?discord(?:\.com/invite|app\.com/invite|\.gg)/?[a-zA-Z0-9]+/?")


class CooldownByContent(commands.CooldownMapping):
    def _bucket_key(ctx, message):
        return (message.channel.id, message.content)


class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages_cooldown = CooldownByContent.from_cooldown(15, 17.0, commands.BucketType.member)  # checks for same content
        self.user_cooldowns = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)  # checks for member spam
        self.invite_cooldown = commands.CooldownMapping.from_cooldown(5, 10, commands.BucketType.user)  # checks for invites

    # if they send a message
    @commands.Cog.listener('on_message')
    async def on_automod(self, message):

        # cache check goes here Cairo
        # if automod == 0:
        #     return

        if message.guild is None or message.guild.id != 667065302260908032:  # in DM's or not DEL server
            return

        if message.author not in message.guild.members:  # They were banned but messages are still being sent cause discord
            return

        if message.author.guild_permissions.manage_messages:  # Member has MANAGE_MESSAGES permissions
            return

        if not message.guild.me.guild_permissions.manage_roles:
            return

        for coro in self.automodactions.copy():
            if await coro(self, message):
                break

    # if they edit existing message
    @commands.Cog.listener('on_message_edit')
    async def on_automod_edit(self, before, after):
        message = after

        # cache check goes here Cairo
        # if automod == 0:
        #     return

        if message.guild is None:  # in DM's
            return

        if message.author not in message.guild.members:  # They were banned but messages are still being sent cause discord
            return

        if message.author.guild_permissions.manage_messages:  # Member has MANAGE_MESSAGES permissions
            return

        if not message.guild.me.guild_permissions.manage_roles:
            return

        for coro in self.automodactions.copy():
            if await coro(self, message):
                break

    async def anti_spam(self, message):
        current = message.created_at.replace(tzinfo=timezone.utc).timestamp()
        reason = "potential spamming"
        logchannel = message.guild.get_channel()  # put channel id here

        content_bucket = self.messages_cooldown.get_bucket(message)
        if content_bucket.update_rate_limit(current):
            try:
                # ! Check if user is already muted
                muterole = discord.utils.find(lambda r: r.name.lower() == "muted", message.guild.roles)
                if muterole not in message.author.roles:
                    await message.author.add_roles(muterole, reason=reason)
                    await message.channel.send(f"Muted **{message.author}** for {reason}")
                    content_bucket.reset()
                    return await logchannel.send(embed=self.embed(message.author, reason, 1))
            except Exception as e:
                await message.channel.send(f"Failed to mute **{message.author}** - {e}")
                content_bucket.reset()

        user_bucket = self.user_cooldowns.get_bucket(message)
        if user_bucket.update_rate_limit(current):
            try:
                # ! Check if user is already muted
                muterole = discord.utils.find(lambda r: r.name.lower() == "muted", message.guild.roles)
                if muterole not in message.author.roles:
                    await message.author.add_roles(muterole, reason=reason)
                    await message.channel.send(f"Muted **{message.author}** for {reason}")
                    user_bucket.reset()
                    return await logchannel.send(embed=self.embed(message.author, reason, 1))
            except Exception as e:
                await message.channel.send(f"Failed to mute **{message.author}** - {e}")
                user_bucket.reset()

    async def anti_invite(self, message):
        invites = INVITE.findall(message.content)
        reason = 'potential advertising'
        logchannel = message.guild.get_channel()  # put channel id here

        if invites:
            current = message.created_at.replace(tzinfo=timezone.utc).timestamp()
            content_bucket = self.invite_cooldown.get_bucket(message)
            guild_invs = []
            for inv in invites:
                for invs in await message.guild.invites():
                    guild_invs.append(invs.url)
                if inv not in guild_invs:
                    await message.delete()
                    if content_bucket.update_rate_limit(current):
                        # ! Check if user is already muted
                        muterole = discord.utils.find(lambda r: r.name.lower() == "muted", message.guild.roles)
                        if muterole not in message.author.roles:
                            await message.author.add_roles(muterole, reason=reason)
                            await message.channel.send(f"Muted **{message.author}** for {reason}")
                            content_bucket.reset()
                            return await logchannel.send(embed=self.embed(message.author, reason, 1))

    def embed(self, member, reason, action):  # this instead of multiple embeds
        e = discord.Embed(color=0xeb0000, timestamp=datetime.utcnow())
        e.set_author(name="Automod action executed", icon_url=member.avatar_url)
        e.description = (f"{'Muted' if action == 1 else 'Kicked'} **{member} ({member.id})**"
                         f" for **{reason}**")
        e.set_footer(text=f'Member ID: {member.id}')
        return e

    automodactions = [anti_spam, anti_invite]


def setup(bot):
    bot.add_cog(Automod(bot))
