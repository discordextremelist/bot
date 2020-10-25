import discord
import re

from discord.ext import commands
from datetime import datetime, timezone

# this regex is probably trash but at least it works
INVITE = re.compile(r"(?:https?://)?discord(?:\.com/invite|app\.com/invite|\.gg)/(?:discord(?:\-api|\-developers|\-testers)|[a-zA-Z0-9])+/?")


class CooldownByContent(commands.CooldownMapping):
    def _bucket_key(ctx, message):
        return (message.channel.id, message.content)


class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # cooldown goes the same as commands.cooldown
        # (messages, seconds, user/member/channel whatever)
        self.messages_cooldown = CooldownByContent.from_cooldown(15, 17.0, commands.BucketType.member)  # checks for same content
        self.user_cooldowns = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)  # checks for member spam
        self.invite_cooldown = commands.CooldownMapping.from_cooldown(5, 60.0, commands.BucketType.user)  # checks for invites

    # if they send a message
    @commands.Cog.listener('on_message')
    async def on_automod(self, message):

        # cache check goes here
        # if automod == 0:
        #     return

        if message.guild is None or message.guild.id != 568567800910839811:  # in DM's or not DEL server
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

        # cache check goes here
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
                # Check if user is already muted
                muterole = discord.utils.find(lambda r: r.name.lower() == "muted", message.guild.roles)
                if muterole not in message.author.roles:
                    await message.author.add_roles(muterole, reason=reason)
                    await message.channel.send(f"Muted **{message.author}** for potential spamming")
                    content_bucket.reset()
                    return await logchannel.send(embed=self.embed(message.author, reason, 1))
            except Exception as e:
                await message.channel.send(f"Failed to mute **{message.author}** - {e}")
                content_bucket.reset()

        user_bucket = self.user_cooldowns.get_bucket(message)
        if user_bucket.update_rate_limit(current):
            try:
                # Check if user is already muted
                muterole = discord.utils.find(lambda r: r.name.lower() == "muted", message.guild.roles)
                if muterole not in message.author.roles:
                    await message.author.add_roles(muterole, reason=reason)
                    await message.channel.send(f"Muted **{message.author}** for potential spamming")
                    user_bucket.reset()
                    return await logchannel.send(embed=self.embed(message.author, reason, 1))
            except Exception as e:
                await message.channel.send(f"Failed to mute **{message.author}** - {e}")
                user_bucket.reset()

    async def anti_invite(self, message):
        invites = INVITE.findall(message.content)
        reason = 'potential advertising'
        logchannel = message.guild.get_channel()  # put channel id here

        # this include all the library support server
        # discord-api, discord-testers and discord-developers
        # if you want to add more, just copy that server id
        # and paste it in this list. That'll make it whitelisted
        # to save up resources you can paste DEL's server id
        # in here as well, and remove lines 142-143
        whitelisted_guilds = [197038439483310086, 336642139381301249, 81384788765712384, 613425648685547541, 493130730549805057,
                              222078108977594368, 125227483518861312, 208023865127862272, 151037561152733184, 379378609942560770,
                              530557949098065930, 486311607400529931, 223909216866402304]

        if invites:
            current = message.created_at.replace(tzinfo=timezone.utc).timestamp()
            content_bucket = self.invite_cooldown.get_bucket(message)
            guild_invs = []
            # this will work as long as they won't provide
            # all the whitelisted invites. However if they will
            # it'll take ~10-30 seconds for loop to find non-whitelisted invite
            # If they'll spam messages too fast anti spam will mute them.
            for inv in invites:
                try:
                    check_whitelist = await self.bot.fetch_invite(inv)
                    if check_whitelist.guild.id in whitelisted_guilds:
                        # if the original message is "discord.gg/invite" and not "https://discord.gg/invite"
                        # this whitelisting will not work on "https://discord.com/invite/randominv"
                        # as `check_whitelist.url` will provide "https://discord.gg/randominv" url
                        if "https://" not in inv:
                            guild_invs.append(check_whitelist.url[8:])
                        else:
                            guild_invs.append(check_whitelist.url)
                except Exception as e:
                    print(e)
                    pass
                for invs in await message.guild.invites():
                    guild_invs.append(invs.url)

                if inv not in guild_invs:
                    await message.delete()
                    if content_bucket.update_rate_limit(current):
                        # Check if user is already muted
                        muterole = discord.utils.find(lambda r: r.name.lower() == "muted", message.guild.roles)
                        if muterole not in message.author.roles:
                            await message.author.add_roles(muterole, reason=reason)
                            await message.channel.send(f"Muted **{message.author}** for potential advertising")
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

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def toggleautomod(self, ctx):
        check = None  # get value from cache

        if check == 0:
            # update cache
            await ctx.send("Toggled automod `on`")
        elif check != 0:
            # update cache
            await ctx.send("Toggled automod `off`")


def setup(bot):
    bot.add_cog(Automod(bot))
