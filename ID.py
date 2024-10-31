#║██       ╔═███   ╔██         ██ ╔█████
#║██      ╔╝██ ██  ╚╗██       ██  ║█ 
#║██      ║██    ██ ╚╗██      ██  ║█████
#║██      ║██   ██   ╚╗██    ██   ║█
#║██████╗╚╗██ ██     ╚╗██ ██     ║█████╗
#╚══════╝ ╚═███        ╚═██       ╚═════╝
# © Gydro4ka & mertv_ya_naxyi 2024-2025
# this file - unofficial module for Hikka Userbot
#  /\_/\   This module was loaded through https://t.me/hikka_gmod
# ( o.o )   Licensed under the GNU AGPLv3.
#  > ^ <  
# ------------------------------------------------
# Name: ID
# meta developer: @Gydro4ka & @mertv_ya_naxyi
# Description: Инструменты для работы с ID
# Commands:  .uid | .cid | .mid
# Thanks: me
# ------------------------------------------------
# Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html
# channel: https://t.me/hikka_gmod
from .. import loader, utils

@loader.tds
class iddocs(loader.Module):
    """Инструменты для работы с ID"""
    strings = {'name': '🌘 ID '}
    
    @loader.command(alias="юид")
    async def uid(self, message):
        """[реплай] - посмотреть ID юзера"""
        reply_to = await message.get_reply_message()
        if reply_to:
            reply_user_id = reply_to.sender_id
            await message.edit(f"🔥 <b>ID пользователя</b>: <code>{reply_user_id}</code>")
        else:
            await message.edit("<b>Ошибка! uid</b>\n<i>нету реплая!</i>")

    @loader.command(alias="мид")
    async def mid(self, message):
        """- показать ваше ID """
        await message.edit(f"🔥 <b>Ваш ID</b>: <code>{message.sender_id}</code>")

    @loader.command(alias="чид")
    async def cid(self, message):
        """- показать ID чата"""
        await message.edit("<b>загрузка...</b>")
        await message.edit(f"🔥 <b>ID этого чата</b>: <code>{message.chat_id}</code>")
