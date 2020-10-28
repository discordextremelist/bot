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
import asyncio
import time
from typing import List, Union, Optional
from io import BytesIO

import discord
from discord.ext import commands

from ext.checks import mod_check

from .types import tagTypes


class TagsCog(commands.Cog, name="Tags"):

    def __init__(self, bot):
        self.bot = bot
        self.help_icon = f"{self.bot.settings['emoji']['label']}"

    async def embed_colour(self, ctx):
        """
        Gets the bots display colour and returns a colour code able to be used on embeds.
        """
        global colour

        bot_guild_member = await ctx.guild.fetch_member(self.bot.user.id)
        if len(str(bot_guild_member.colour.value)) == 1:
            colour = 0xFFFFFA
        else:
            colour = bot_guild_member.colour.value

        return colour

    async def tag_name_exists(self, name: str) -> Union[List[bool], Optional[tagTypes.DelTag]]:
        """
        Checks if a tag name or alias matching the name specified exists in the database.
        Returns a boolean stating whether the tag exists in an array in position 0.
        If boolean in pos 0 is True, pos 1 will contain the tag.
        """
        all_tags = self.bot.db.tags.find()
        async for tag in all_tags:
            if tag["_id"] == name.lower():
                return [True, tag]

            if tag["aliases"] is not None and len(tag["aliases"]) > 0:
                for alias in tag["aliases"]:
                    if alias == name.lower():
                        return [True, tag]

        return [False]

    async def tag_exists_error(self, ctx, name):
        """
        Sends an error message stating that there is a tag name/alias conflict.
        """
        return await ctx.send(f"{self.bot.settings['formats']['error']} **Name conflict:** A tag or tag alias with "
                              f"the name **\"**{discord.utils.escape_markdown(name, as_needed=False)}**\"** already"
                              f" exists.")

    async def tag_nf_error(self, ctx, name):
        """
        Sends an error message stating that the specified tag does not exist.
        """
        return await ctx.send(f"{self.bot.settings['formats']['error']} **Not found:** A tag with the name of "
                              f"**\"**{discord.utils.escape_markdown(name, as_needed=False)}**\"** was not found.")

    @commands.command(name="create-tag", aliases=["newtag", "new-tag", "add-tag", "addtag"],
                      usage="create-tag <tag> <content>", description="Allows moderators to create a tag.")
    @commands.guild_only()
    @mod_check()
    async def create_tag(self, ctx, name: str, *, tag: str):
        """
        Allows moderators to create a tag.
        """
        tag_name_exists = await self.tag_name_exists(name)
        if tag_name_exists[0]:
            return await self.tag_exists_error(ctx, name)

        try:
            def check(r, u):
                return r.message.id == language_picker.id and u.id != ctx.bot.user.id

            language_picker = await ctx.send("Which language are you creating this tag in?")
            await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["britian"])
            await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["turkey"])
            await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["france"])
            await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["portugal"])
            await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["spain"])

            responded = False
            languages = []
            languages_dict = self.bot.settings["emoji"]["flags"]

            for language in languages_dict:
                languages.append(languages_dict[language])

            while not responded:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30.0)

                if user.id != ctx.author.id:
                    await language_picker.remove_reaction(reaction, user)
                elif str(reaction) not in languages:
                    await language_picker.remove_reaction(reaction, user)
                elif user.id == ctx.author.id:
                    await language_picker.clear_reactions()

                    contents = {
                        "en": "",
                        "tr": "",
                        "fr": "",
                        "pt": "",
                        "es": ""
                    }

                    reaction_name = ""
                    if str(reaction) == self.bot.settings["emoji"]["flags"]["britian"]:
                        contents["en"] = tag
                        reaction_name = "English"
                    elif str(reaction) == self.bot.settings["emoji"]["flags"]["turkey"]:
                        contents["tr"] = tag
                        reaction_name = "Turkish"
                    elif str(reaction) == self.bot.settings["emoji"]["flags"]["france"]:
                        contents["fr"] = tag
                        reaction_name = "French"
                    elif str(reaction) == self.bot.settings["emoji"]["flags"]["portugal"]:
                        contents["pt"] = tag
                        reaction_name = "Portuguese"
                    elif str(reaction) == self.bot.settings["emoji"]["flags"]["spain"]:
                        contents["es"] = tag
                        reaction_name = "Spanish"

                    await self.bot.db.tags.insert_one({
                        "_id": name.lower(),
                        "creator": str(ctx.author.id),
                        "creationDate": 0,
                        "contents": contents,
                        "aliases": []
                    })

                    return await ctx.channel.send(f"{self.bot.settings['formats']['success']} **Tag created:** A tag "
                                                  f"with the name of "
                                                  f"**\"**{discord.utils.escape_markdown(name, as_needed=False)}**\"**,"
                                                  f" in the language {reaction} **{reaction_name}** was successfully "
                                                  f"created.")
        except asyncio.TimeoutError:
            return

    @commands.command(name="edit-tag", aliases=["modify-tag", "update-tag", "change-tag", "edittag"],
                      usage="edit-tag <tag> <content>", description="Allows moderators to edit a tag.")
    @commands.guild_only()
    @mod_check()
    async def edit_tag(self, ctx, name: str, *, content: str):
        """
        Allows moderators to edit a tag.
        """
        tag = await self.tag_name_exists(name)
        if tag[0]:
            try:
                def check(r, u):
                    return r.message.id == language_picker.id and u.id != ctx.bot.user.id

                language_picker = await ctx.send("Which language of this tag are you editing/adding?")
                await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["britian"])
                await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["turkey"])
                await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["france"])
                await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["portugal"])
                await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["spain"])

                responded = False
                languages = []
                languages_dict = self.bot.settings["emoji"]["flags"]

                for language in languages_dict:
                    languages.append(languages_dict[language])

                while not responded:
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30.0)

                    if user.id != ctx.author.id:
                        await language_picker.remove_reaction(reaction, user)
                    elif str(reaction) not in languages:
                        await language_picker.remove_reaction(reaction, user)
                    elif user.id == ctx.author.id:
                        await language_picker.clear_reactions()

                        contents = {
                            "en": tag[1]["contents"]["en"],
                            "tr": tag[1]["contents"]["tr"],
                            "fr": tag[1]["contents"]["fr"],
                            "pt": tag[1]["contents"]["pt"],
                            "es": tag[1]["contents"]["es"]
                        }

                        contents_backup = \
                            discord.File(BytesIO((str(contents)).encode("utf-8")),
                                         filename=f"{tag[1]['_id']}-{time.time()}.json")

                        reaction_name = ""
                        if str(reaction) == self.bot.settings["emoji"]["flags"]["britian"]:
                            contents["en"] = content
                            reaction_name = "English"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["turkey"]:
                            contents["tr"] = content
                            reaction_name = "Turkish"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["france"]:
                            contents["fr"] = content
                            reaction_name = "French"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["portugal"]:
                            contents["pt"] = content
                            reaction_name = "Portuguese"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["spain"]:
                            contents["es"] = content
                            reaction_name = "Spanish"

                        await ctx.bot.db.tags.update_one({"_id": tag[1]["_id"]}, {
                            "$set": {
                                "contents": contents
                            }
                        })

                        await ctx.author.send(content=f"Here's a backup of the tag "
                                                      f"**\"**{discord.utils.escape_markdown(name, as_needed=False)}"
                                                      f"**\"** which you just edited, before your edits were made. "
                                                      f"Just in case!",
                                              file=contents_backup)

                        return await ctx.channel.send(f"{self.bot.settings['formats']['success']} **Tag edited:** A tag"
                                                      f" with the name of "
                                                      f"**\"**{discord.utils.escape_markdown(name, as_needed=False)}**"
                                                      f"\"**, in the language {reaction} **{reaction_name}** was "
                                                      f"successfully edited.")
            except asyncio.TimeoutError:
                return
        else:
            return await self.tag_nf_error(ctx, name)

    @commands.command(name="tag-aliases", aliases=["alias-tag"], usage="tag-aliases <name/alias>",
                      description="Allows users to view a tag's aliases.")
    @commands.guild_only()
    async def tag_aliases(self, ctx, *, name: str):
        tag = await self.tag_name_exists(name)
        if tag[0]:
            if len(tag[1]["aliases"]) > 0:
                return await ctx.send(f"{self.bot.settings['formats']['info']} **Aliases:** This tag has the following "
                                      f"aliases - {'`' + '`, `'.join(tag[1]['aliases']) + '`'}.")
            else:
                return await ctx.send(f"{self.bot.settings['formats']['info']} **Aliases:** This tag has no aliases.")
        else:
            return await self.tag_nf_error(ctx, name)

    @commands.command(name="add-tag-alias", usage="add-tag-alias <name> <alias>", description="Allows moderators to add"
                                                                                              " an alias for a tag.")
    @commands.guild_only()
    @mod_check()
    async def add_tag_aliases(self, ctx, name: str, *, alias: str):
        """
        Allows moderators to add an alias for a tag.
        """
        exists = await self.tag_name_exists(alias)
        tag = await self.tag_name_exists(name)

        if not exists[0] and tag[0]:
            if len(alias) > 20:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Too longth:** The alias name you "
                                      f"inputted is too long.")
            elif len(alias) < 2:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Too longth:** The alias name you "
                                      f"inputted is too short.")

            aliases = tag[1]["aliases"]
            aliases.append(alias.lower())
            await ctx.bot.db.tags.update_one({"_id": tag[1]["_id"]}, {
                "$set": {
                    "aliases": aliases
                }
            })

            return await ctx.send(f"{self.bot.settings['formats']['success']} **Added alias:** The alias was "
                                  f"successfully added.")
        else:
            if exists[0]:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Duplicated alias:** This tag already "
                                      f"has this alias.")
            else:
                return await self.tag_nf_error(ctx, name)

    @commands.command(name="remove-tag-alias", usage="remove-tag-alias <name> <alias>",
                      aliases=["del-tag-alias", "rm-tag-alias"], description="Allows moderators to remove an alias for "
                                                                             "a tag.")
    @commands.guild_only()
    @mod_check()
    async def remove_tag_alias(self, ctx, name: str, *, alias: str):
        """
        Allows moderators to remove an alias for a tag.
        """
        tag = await self.tag_name_exists(name)

        if tag[0]:
            if alias.lower() in tag[1]["aliases"]:

                aliases = tag[1]["aliases"]
                aliases.remove(alias.lower())
                await ctx.bot.db.tags.update_one({"_id": tag[1]["_id"]}, {
                    "$set": {
                        "aliases": aliases
                    }
                })

                return await ctx.send(f"{self.bot.settings['formats']['success']} **Removed alias:** The alias was "
                                      f"successfully removed.")
            else:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Not found:** The specified alias "
                                      f"does not belong to the specified tag.")
        else:
            return await self.tag_nf_error(ctx, name)

    @commands.command(name="tags", usage="tags", aliases=["list-tags", "tag-list", "list-tag"],
                      description="Shows all of the saved tags.")
    @commands.guild_only()
    async def tags(self, ctx):
        """
        Shows all of the saved tags.
        """
        all_tags = self.bot.db.tags.find()
        tags = ""
        async for tag in all_tags:
            tags += "`" + tag["_id"] + f"`, "

        if len(tags) > 0:
            await ctx.send(f"{self.bot.settings['formats']['info']} **Tags:** A full list of tags is available below:"
                           f"\n\n{tags[:-2]}")
        else:
            await ctx.send(f"{self.bot.settings['formats']['info']} **Tags:** There are no saved tags.")

    @commands.command(name="raw-tag", usage="raw-tag <name/alias>", aliases=["tag-raw", "txt-tag"],
                      description="Allows moderators to get the content of a specific language of a tag in a raw file.")
    @commands.guild_only()
    @mod_check()
    async def raw_tag(self, ctx, *, name: str):
        """
        Allows moderators to get the content of a specific language of a tag in a raw file.
        """
        tag = await self.tag_name_exists(name)

        if tag[0]:
            try:
                def check(r, u):
                    return r.message.id == language_picker.id and u.id != ctx.bot.user.id

                language_picker = await ctx.send("Which language do you want to get the raw text in for this tag?")
                if len(tag[1]["contents"]["en"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["britian"])
                if len(tag[1]["contents"]["tr"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["turkey"])
                if len(tag[1]["contents"]["fr"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["france"])
                if len(tag[1]["contents"]["pt"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["portugal"])
                if len(tag[1]["contents"]["es"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["spain"])

                responded = False
                languages = []
                languages_dict = self.bot.settings["emoji"]["flags"]

                for language in languages_dict:
                    languages.append(languages_dict[language])

                while not responded:
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30.0)

                    if user.id != ctx.author.id:
                        await language_picker.remove_reaction(reaction, user)
                    elif str(reaction) not in languages:
                        await language_picker.remove_reaction(reaction, user)
                    elif user.id == ctx.author.id:
                        await language_picker.clear_reactions()

                        locale = ""
                        if str(reaction) == self.bot.settings["emoji"]["flags"]["britian"]:
                            locale = "en"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["turkey"]:
                            locale = "tr"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["france"]:
                            locale = "fr"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["portugal"]:
                            locale = "pt"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["spain"]:
                            locale = "es"

                        raw_tag = discord.File(BytesIO((str(tag[1]["contents"][locale])).encode("utf-8")),
                                               filename=f"{tag[1]['_id']}-{time.time()}.txt")
                        return await ctx.send(file=raw_tag)

            except asyncio.TimeoutError:
                return
        else:
            return await self.tag_nf_error(ctx, name)

    @commands.command(name="tag", aliases=["show-tag", "view-tag"], usage="tag <name/alias>",
                      description="Allows users to view a tag.")
    @commands.guild_only()
    async def tag(self, ctx, *, name: str):
        """
        Allows users to view a tag.
        """
        tag = await self.tag_name_exists(name)
        if tag[0]:
            try:
                def check(r, u):
                    return r.message.id == language_picker.id and u.id != ctx.bot.user.id

                language_picker = await ctx.send("Which language do you want to view this tag in?")
                if len(tag[1]["contents"]["en"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["britian"])
                if len(tag[1]["contents"]["tr"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["turkey"])
                if len(tag[1]["contents"]["fr"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["france"])
                if len(tag[1]["contents"]["pt"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["portugal"])
                if len(tag[1]["contents"]["es"]) > 0:
                    await language_picker.add_reaction(self.bot.settings["emoji"]["flags"]["spain"])

                responded = False
                languages = []
                languages_dict = self.bot.settings["emoji"]["flags"]

                for language in languages_dict:
                    languages.append(languages_dict[language])

                while not responded:
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30.0)

                    if user.id != ctx.author.id:
                        await language_picker.remove_reaction(reaction, user)
                    elif str(reaction) not in languages:
                        await language_picker.remove_reaction(reaction, user)
                    elif user.id == ctx.author.id:
                        await language_picker.clear_reactions()

                        locale = ""
                        if str(reaction) == self.bot.settings["emoji"]["flags"]["britian"]:
                            locale = "en"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["turkey"]:
                            locale = "tr"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["france"]:
                            locale = "fr"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["portugal"]:
                            locale = "pt"
                        elif str(reaction) == self.bot.settings["emoji"]["flags"]["spain"]:
                            locale = "es"

                        return await ctx.send(tag[1]["contents"][locale])

            except asyncio.TimeoutError:
                return
        else:
            return await self.tag_nf_error(ctx, name)

    @commands.command(name="delete-tag", usage="delete-tag <name/alias>",
                      aliases=["remove-tag", "del-tag"], description="Allows moderators to delete a tag.")
    @commands.guild_only()
    @commands.cooldown(1, 120, commands.BucketType.user)
    @mod_check()
    async def delete_tag(self, ctx, *, name: str):
        """
        Allows moderators to delete a tag.
        """
        tag = await self.tag_name_exists(name)

        if tag[0]:
            try:
                def check(r, u):
                    return r.message.id == language_picker.id and u.id != ctx.bot.user.id

                language_picker = await ctx.send("Are you sure you want to **__delete__** this tag?")
                await asyncio.sleep(1.75)
                await language_picker.add_reaction(self.bot.settings["emoji"]["check"])
                await language_picker.add_reaction(self.bot.settings["emoji"]["cross"])

                responded = False
                responses = [self.bot.settings["emoji"]["check"], self.bot.settings["emoji"]["cross"]]

                while not responded:
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30.0)

                    if user.id != ctx.author.id:
                        await language_picker.remove_reaction(reaction, user)
                    elif str(reaction) not in responses:
                        await language_picker.remove_reaction(reaction, user)
                    elif user.id == ctx.author.id:
                        await language_picker.clear_reactions()

                        if str(reaction) == self.bot.settings["emoji"]["check"]:
                            tag_backup = \
                                discord.File(BytesIO((str(tag[1])).encode("utf-8")),
                                             filename=f"{tag[1]['_id']}-{time.time()}.json")

                            await ctx.author.send(content=f"Here's a backup of the tag **\"**"
                                                          f"{discord.utils.escape_markdown(name, as_needed=False)}"
                                                          f"**\"** which you just deleted, Just in case!",
                                                  file=tag_backup)

                            await ctx.bot.db.tags.delete_one({"_id": tag[1]["_id"]})

                            return await ctx.send(
                                f"{self.bot.settings['formats']['success']} **Deleted:** Successfully deleted the "
                                f"specified tag.")
                        else:
                            return await ctx.send(
                                f"{self.bot.settings['formats']['success']} **Cancelled:** Safely cancelled the "
                                f"deletion of the specified tag.")

            except asyncio.TimeoutError:
                return
        else:
            return await self.tag_nf_error(ctx, name)


def setup(bot):
    bot.add_cog(TagsCog(bot))
