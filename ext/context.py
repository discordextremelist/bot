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


class EditingContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None,
                   allowed_mentions=None):
        if file or files:
            return await super().send(content=content, tts=tts, embed=embed, file=file, files=files,
                                      delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions)
        reply = None
        try:
            reply = self.bot.cmd_edits[self.message.id]
        except KeyError:
            pass
        if reply:
            return await reply.edit(content=content, embed=embed, delete_after=delete_after)
        reference = self.message.reference
        if reference and isinstance(reference.resolved, discord.Message):
            msg = await reference.resolved.reply(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions)
        else:
            msg = await super().send(content=content, tts=tts, embed=embed, file=file, files=files,
                                     delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions)
        self.bot.cmd_edits[self.message.id] = msg
        return msg



