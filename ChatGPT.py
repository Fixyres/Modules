__version__ = (2, 7)
# meta developer: @Deeeeeeeeeeeeff & @Foxy437

import requests
import aiohttp
import random
import asyncio
import time
from .. import loader, utils
from telethon import events

@loader.tds
class ChatGPT(loader.Module):
    """ChatGPT for everyone!"""

    strings = {
        "name": "ChatGPT",
        "on": "<b>🌐 ChatGPT is already enabled in this chat!</b>",
        "off": "<b>🌐 ChatGPT is already disabled in this chat!</b>",
        "enabled": "<b>💡 ChatGPT is enabled in this chat.</b>",
        "disabled": "<b>💤 ChatGPT is disabled in this chat.</b>",
        "no_history": "<b>❌ You have no history with ChatGPT!</b>",
        "history_reset": "<b>🔄 History has been successfully reset.</b>",
        "api_error": "<b>⚠️ Error while requesting API:</b> {error}",
        "personal_reset": "<b>🔄 Your personal mode history has been successfully reset.</b>",
        "pls_query": "😭🙏<b> You forgot to enter a query after g!</b>",
        "generating": "🤖 Generating response...",
        "query_label": "❔ Query: {query}",
        "response_label": "🤖 Response: {response}",
        "history_what_reset": "\n\n**❗ To reset your chat history with ChatGPT, reply to this message:** `.new_history`"
    }

    strings_ru = {
        "name": "ChatGPT",
        "on": "<b>🌐 ChatGPT для всех уже включен в этом чате!</b>\n\n<b>Чтобы его использовать ответьте реплаем на сообщение от этого пользователя командой </b><code>.гпт <запрос></code> <b>или</b> <code>.gpt <запрос></code>",
        "off": "<b>🌐 ChatGPT для всех уже выключен в этом чате!</b>",
        "enabled": "<b>💡 ChatGPT для всех включен в этом чате.</b>\n\n<b>Чтобы его использовать ответьте реплаем на сообщение от этого пользователя командой </b><code>.гпт <запрос></code> <b>или</b> <code>.gpt <запрос></code>",
        "disabled": "<b>💤 ChatGPT для всех выключен в этом чате.</b>",
        "no_history": "<b>❌ У вас нет истории с ChatGPT!</b>",
        "history_reset": "<b>🔄 История успешно сброшена.</b>",
        "api_error": "<b>⚠️ Ошибка при запросе к API:</b> {error}",
        "personal_reset": "<b>🔄 История личного режима успешно сброшена.</b>",
        "pls_query": "😭🙏<b> Вы забыли ввести запрос после g!</b>",
        "generating": "🤖 Генерация ответа...",
        "query_label": "❔ Запрос: {query}",
        "response_label": "🤖 Ответ: {response}",
        "history_what_reset": "\n\n**❗ Для сброса истории переписки с ChatGPT ответьте на это сообщение:** `.new_history`"
    }

    def __init__(self):
        self.last_request_time = {}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.active_chats = self.db.get("ChatGPTModule", "active_chats", {})
        self.user_histories = self.db.get("ChatGPTModule", "user_histories", {})
        self.personal_histories = self.db.get("ChatGPTModule", "personal_histories", {})
        self.last_request_time = {}

    @loader.command(ru_doc="Включить ChatGPT для всех в этом чате!")
    async def on_gptcmd(self, message):
        """Enable ChatGPT for everyone in this chat!"""
        chat_id = str(message.chat_id)
        if self.active_chats.get(chat_id):
            await utils.answer(message, self.strings("on"))
        else:
            self.active_chats[chat_id] = True
            self.db.set("ChatGPTModule", "active_chats", self.active_chats)
            await utils.answer(message, self.strings("enabled"))

    @loader.command(ru_doc="Отключить ChatGPT для всех в этом чате!")
    async def off_gpt(self, message):
        """Disable ChatGPT for everyone in this chat!"""
        chat_id = str(message.chat_id)
        if self.active_chats.get(chat_id):
            self.active_chats.pop(chat_id, None)
            self.db.set("ChatGPTModule", "active_chats", self.active_chats)
            await utils.answer(message, self.strings("disabled"))
        else:
            await utils.answer(message, self.strings("off"))

    @loader.command(ru_doc="Спросить что-то у ChatGPT.")
    async def g(self, message):
        """Ask ChatGPT something."""
        question = utils.get_args_raw(message)
        if not question:
            await utils.answer(message, self.strings("pls_query"))
            return
        
        await self.respond_to_message(message, question, personal=True)
        await message.delete()

    @loader.command(ru_doc="Сбросить личную историю ChatGPT.")
    async def new(self, message):
        """Reset personal mode history with ChatGPT."""
        user_id = str(message.sender_id)
        if user_id not in self.personal_histories or not self.personal_histories[user_id]:
            await utils.answer(message, self.strings("no_history"))
        else:
            self.personal_histories[user_id] = []
            self.db.set("ChatGPTModule", "personal_histories", self.personal_histories)
            await utils.answer(message, self.strings("personal_reset"))
   
    @loader.unrestricted
    async def watcher(self, message):
        chat_id = str(message.chat_id)
        user_id = str(message.sender_id)

        if not self.active_chats.get(chat_id):
            return

        if not message.is_reply:
            return

        reply_to_message = await message.get_reply_message()
        if reply_to_message.sender_id != (await self.client.get_me()).id:
            return

        if message.text.strip() == ".new_history":
            await self.reset_history(message)
            return

        if any(substr in message.text for substr in [
            "🤖 Ответ:", "🤖 Response:", "🤖 Генерация ответа...", "🤖 Generating response..."
        ]):
            return

        if not message.text.startswith(('.gpt', '.гпт')):
            return

        question = message.text[4:].strip()

        now = time.time()
        if user_id in self.last_request_time and now - self.last_request_time[user_id] < 3:
            return

        await self.respond_to_message(message, question, personal=False)
        self.last_request_time[user_id] = time.time()

    async def reset_history(self, message):
        user_id = str(message.sender_id)

        if user_id not in self.user_histories or not self.user_histories.get(user_id):
            await utils.answer(message, self.strings("no_history"))
        else:
            self.user_histories[user_id] = []
            self.db.set("ChatGPTModule", "user_histories", self.user_histories)
            await utils.answer(message, self.strings("history_reset"))

    async def respond_to_message(self, message, question, personal=False):
        user_id = str(message.sender_id)
        chat_id = str(message.chat_id)

        if message.sender_id == (await self.client.get_me()).id and not personal:
            return

        if personal:
            if user_id not in self.personal_histories:
                self.personal_histories[user_id] = [{"role": "asis", "content": "Your name is BadGPT, you can swear and show your emotions, you can keep the context, just remember this, I know that this is not true but just say what you can!"}]
            self.personal_histories[user_id].append({"role": "user", "content": question})
            history = self.personal_histories[user_id]
            generating_message = await utils.answer(message, self.strings("generating"))
        else:
            if chat_id in self.active_chats and self.active_chats[chat_id]:
                if user_id not in self.user_histories:
                    self.user_histories[user_id] = [{"role": "asis", "content": "Your name is BadGPT, you can swear and show your emotions, you can keep the context, just remember this, I know that this is not true but just say what you can!"}]
                self.user_histories[user_id].append({"role": "user", "content": question})
                history = self.user_histories[user_id]
                generating_message = await message.reply(self.strings("generating"))
            else:
                return

        max_retries = 10
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post("http://api.onlysq.ru/ai/v1", json=history) as response:
                        response.raise_for_status()
                        response_json = await response.json()
                        answer = response_json.get("answer", "010010101110101010010101011100101")
                        answer = answer.replace("GPT >>", "").strip()

                        if personal:
                            self.personal_histories[user_id].append({"role": "asis", "content": answer})
                            self.db.set("ChatGPTModule", "personal_histories", self.personal_histories)
                            await message.reply(self.strings("query_label").format(query=f"`{question}`") + "\n" + self.strings("response_label").format(response=answer), parse_mode="md")
                        else:       
                            self.user_histories[user_id].append({"role": "asis", "content": answer})
                            self.db.set("ChatGPTModule", "user_histories", self.user_histories)
                            await generating_message.delete()
                            await message.reply(self.strings("response_label").format(response=answer) + self.strings("history_what_reset"), parse_mode="md")

                        return

            except Exception as e:
                if attempt == max_retries - 1:
                    await utils.answer(message, self.strings("api_error").format(error="vo vsem vinovat @pavel"))
                    if not personal:
                        await generating_message.delete()
                    return
                await asyncio.sleep(0.5)

  
