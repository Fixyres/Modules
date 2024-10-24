# meta developer: @Foxy437

import os
import sys
import json
import subprocess
import aiohttp
import io
from telethon import events
import g4f
from deep_translator import GoogleTranslator
from .. import loader, utils

class FoGPT(loader.Module):
    '''dev: foxy437.t.me'''
    strings = {"name": "FoGPT"}

    def __init__(self):
        self.def_history = [
            {"role": "user", "content": "??????"},
            {"role": "assistant", "content": "??????"}
        ]
        self.history_file = 'history.txt'
        self.conversation_history = []
        self.load_history_from_file()

    def save_history_to_file(self):
        with open(self.history_file, 'w', encoding='utf-8') as file:
            json.dump(self.conversation_history, file, ensure_ascii=False, indent=4)

    def load_history_from_file(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as file:
                self.conversation_history = json.load(file)
                if not self.conversation_history:
                    self.conversation_history = self.def_history
                    self.save_history_to_file()
        else:
            self.conversation_history = self.def_history
            self.save_history_to_file()

    async def process_request(self, user_input, chat_id, msg):
        self.conversation_history.append({"role": "user", "content": user_input})
        try:
            response = await g4f.ChatCompletion.create_async(
                model="gpt-4o",
                messages=self.conversation_history,
            )
            chat_gpt_response = response
        except Exception as e:
            print(f"Ошибка: {e}")
            chat_gpt_response = "..."

        if chat_gpt_response == "...":
            self.conversation_history.pop()
        else:
            self.conversation_history.append({"role": "assistant", "content": chat_gpt_response})
            self.save_history_to_file()
            await msg.edit(f"❓ **Запрос:** `{user_input}`\n\n✏️ **Ответ:** {chat_gpt_response}", parse_mode='md')

    @loader.sudo
    async def newcmd(self, message):
        '''- Сбросить историю'''
        self.conversation_history = self.def_history
        await message.edit("<b><emoji document_id=5409143295039252230>🗑️</emoji> История сброшена!</b>")
        self.save_history_to_file()

    async def gcmd(self, message):
        '''- Пример: .g привет как дела'''
        user_input = utils.get_args_raw(message)
        chat_id = message.chat_id

        if not user_input:
            reply = await message.get_reply_message()
            if reply:
                user_input = reply.raw_text
            else:
                await utils.answer(message, "<b><emoji document_id=5321288244350951776>👎</emoji> Вы не задали запрос.</b>")
                return

        await message.delete()
        msg = await message.respond("<b><emoji document_id=5409143295039252230>🔄</emoji> Генерация ответа...</b>")
        await self.process_request(user_input, chat_id, msg)
