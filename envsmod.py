# -*- coding: utf-8 -*-

#   Friendly Telegram (telegram userbot)
#   Copyright (C) 2018-2020 The Authors

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

#  SOURCE: rf0x3d.su.
# meta developer: rf0x3d.su & @eremod 

from .. import loader, utils  # pylint: disable=relative-beyond-top-level
import logging
from os import remove as DelFile
import requests
from requests import HTTPError

logger = logging.getLogger(__name__)


@loader.tds
class envsMod(loader.Module):
    """envs.sh reuploader"""
    strings = {
        "name": "envs.sh Reuploader",
        "connection_error": "Host is unreachable for now, try again later.",
        "no_reply": "<b>You must be reply to a message with media</b>",
        "success": "URL for <code>{}</code>:\n\n<code>{}</code>",
        "error": "An error occured:\n<code>{}</code>",
        "uploading": "<b>Uploading {} ({}{})...</b>"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.sudo
    async def envcmd(self, message):
        """Reupload to envs.sh."""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            return await utils.answer(message, self.strings('no_reply',
                                                            message))
        size_len, size_unit = self.convert(reply.file.size)
        await utils.answer(message,
                           self.strings('uploading',
                                        message).format(reply.file.name,
                                                        size_len,
                                                        size_unit))
        path = await self.client.download_media(reply)
        try:
            uploaded = await upload(path)
        except ConnectionError:
            return await utils.answer(message,
                                      self.strings('connection_error',
                                                   message))
        except HTTPError as e:
            return await utils.answer(message,
                                      self.strings('error',
                                                   message).format(str(e)))
        return await utils.answer(message, self.strings('success',
                                  message).format(path, uploaded))

    def convert(self, size):
        power = 2**10
        zero = 0
        units = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while size > power:
            size /= power
            zero += 1
        return round(size, 2), units[zero]


async def upload(path):
    try:
        req = requests.post('https://envs.sh',
                            files={'file': open(path, 'rb')})
    except ConnectionError:
        DelFile(path)
        raise ConnectionError()
    if req.status_code != 200:
        DelFile(path)
        raise HTTPError(req.text)
    DelFile(path)
    return req.text