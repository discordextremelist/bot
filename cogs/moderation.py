import discord

from discord.ext import commands

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Kick someone from the server")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason: str = None):
        """
        Kicks member from server.
        You can also provide multiple members to kick.
        """
        if not members:
            return await ctx.send(f"{emotes.red_mark} | You're missing an argument - **members**")
            
        error = '\n'
        try:
            total = len(members)
            if total > 10:
                return await ctx.send("You can kick only 10 members at once!") 

            failed = 0
            failed_list = []
            success_list = []
            for member in members:
                if member == ctx.author:
                    failed += 1
                    failed_list.append(f"{member.mention} ({member.id}) - you are the member?")
                    continue
                if member.top_role.position >= ctx.author.top_role.position:
                    failed += 1
                    failed_list.append(f"{member.mention} ({member.id}) - member is above you in role hierarchy or has the same role.")
                    continue
                if member.top_role.position >= ctx.guild.me.top_role.position:
                    failed += 1
                    failed_list.append(f"{member.mention} ({member.id}) - member is above me in role hierarchy or has the same role.")
                    continue
                try:
                    await ctx.guild.kick(member, reason=f"Mod: {ctx.author} - {reason or 'No reason'}")
                    success_list.append(f"{member.mention} ({member.id})")
                except discord.HTTPException as e:
                    print(e)
                    failed += 1
                    failed_list.append(f"{member.mention} - {e}")
                except discord.Forbidden as e:
                    print(e)
                    failed += 1
                    failed_list.append(f"{member.mention} - {e}")
            muted = ""
            notmuted = ""
            if success_list and not failed_list:
                muted += "**I've successfully kicked {0} member(s):**\n".format(total)
                for num, res in enumerate(success_list, start=0):
                    muted += f"`[{num+1}]` {res}\n"
                await ctx.send(muted)
            if success_list and failed_list:
                muted += "**I've successfully kicked {0} member(s):**\n".format(total - failed)
                notmuted += f"**However I failed to kick the following {failed} member(s):**\n"
                for num, res in enumerate(success_list, start=0):
                    muted += f"`[{num+1}]` {res}\n"
                for num, res in enumerate(failed_list, start=0):
                    notmuted += f"`[{num+1}]` {res}\n"
                await ctx.send(muted + notmuted)
            if not success_list and failed_list:  
                notmuted += f"**I failed to kick all the members:**\n"
                for num, res in enumerate(failed_list, start=0):
                    notmuted += f"`[{num+1}]` {res}\n"
                await ctx.send(notmuted)
                    
        except Exception as e:
            print(e)
            return await ctx.send(f"{emotes.warning} Something failed! Error: (Please report it to my developers):\n- {e}")

    @commands.command(brief="Ban someone from the server")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], *, reason: str = None):
        """
        Ban members from the server.
        """

        if not members:
            return await ctx.send(f"{emotes.red_mark} | You're missing an argument - **members**")

        error = '\n'
        try:
            total = len(members)
            if total > 10:
                return await ctx.send("You can ban only 10 members at once!") 

            failed = 0
            failed_list = []
            success_list = []
            for member in members:
                if member == ctx.author:
                    failed += 1
                    failed_list.append(f"{member.mention} ({member.id}) - you are the member...")
                    continue
                if member.top_role.position >= ctx.author.top_role.position:
                    failed += 1
                    failed_list.append(f"{member.mention} ({member.id}) - member is above you in role hierarchy or has the same role.")
                    continue
                if member.top_role.position >= ctx.guild.me.top_role.position:
                    failed += 1
                    failed_list.append(f"{member.mention} ({member.id}) - member is above me in role hierarchy or has the same role.")
                    continue
                try:
                    await ctx.guild.ban(member, reason=f"Mod: {ctx.author} - {reason or 'No reason'}")
                    success_list.append(f"{member.mention} ({member.id})")
                except discord.HTTPException as e:
                    print(e)
                    failed += 1
                    failed_list.append(f"{member.mention} - {e}")
                except discord.Forbidden as e:
                    print(e)
                    failed += 1
                    failed_list.append(f"{member.mention} - {e}")
            muted = ""
            notmuted = ""
            if success_list and not failed_list:
                muted += "**I've successfully banned {0} member(s):**\n".format(total)
                for num, res in enumerate(success_list, start=0):
                    muted += f"`[{num+1}]` {res}\n"
                await ctx.send(muted)
            if success_list and failed_list:
                muted += "**I've successfully banned {0} member(s):**\n".format(total - failed)
                notmuted += f"**However I failed to ban the following {failed} member(s):**\n"
                for num, res in enumerate(success_list, start=0):
                    muted += f"`[{num+1}]` {res}\n"
                for num, res in enumerate(failed_list, start=0):
                    notmuted += f"`[{num+1}]` {res}\n"
                await ctx.send(muted + notmuted)
            if not success_list and failed_list:  
                notmuted += f"**I failed to ban all the members:**\n"
                for num, res in enumerate(failed_list, start=0):
                    notmuted += f"`[{num+1}]` {res}\n"
                await ctx.send(notmuted)
                    
        except Exception as e:
            print(e)
            return await ctx.send(f"Something failed! Error:\n- {e}")

def setup(bot):
    bot.add_cog(Moderation(bot))
