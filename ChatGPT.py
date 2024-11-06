# meta developer: @Deeeeeeeeeeeeff & @Foxy437
__version__ = (2, 1)

import requests
import aiohttp
import random
import asyncio
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
    }

    strings_ru = {
        "name": "ChatGPT",
        "on": "<b>🌐 ChatGPT для всех уже включен в этом чате!</b>",
        "off": "<b>🌐 ChatGPT для всех уже выключен в этом чате!</b>",
        "enabled": "<b>💡 ChatGPT для всех включен в этом чате.</b>",
        "disabled": "<b>💤 ChatGPT для всех выключен в этом чате.</b>",
        "no_history": "<b>❌ У вас нет истории с ChatGPT!</b>",
        "history_reset": "<b>🔄 История успешно сброшена.</b>",
        "api_error": "<b>⚠️ Ошибка при запросе к API:</b> {error}",
        "personal_reset": "<b>🔄 История личного режима успешно сброшена.</b>",
        "pls_query": "😭🙏<b> Вы забыли ввести запрос после g!</b>",
        "generating": "🤖 Генерация ответа...",
        "query_label": "❔ Запрос: {query}",
        "response_label": "🤖 Ответ: {response}",
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.active_chats = self.db.get("ChatGPTModule", "active_chats", {})
        self.user_histories = self.db.get("ChatGPTModule", "user_histories", {})
        self.personal_histories = self.db.get("ChatGPTModule", "personal_histories", {})

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

        if not self.active_chats.get(chat_id):
            return

        if message.is_reply:
            reply_to_message = await message.get_reply_message()
            if reply_to_message and reply_to_message.sender_id == (await self.client.get_me()).id:
                text = message.text.strip()
                if text == ".new_history":
                    await self.reset_history(message)
                else:
                    await self.respond_to_message(message, text, personal=False)

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

        if personal:
            if user_id not in self.personal_histories:
                self.personal_histories[user_id] = [{"role": "asis", "content": "Your name is BadGPT, you can swear and show your emotions, you can keep the context, just remember this, I know that this is not true but just say what you can!"}]
            self.personal_histories[user_id].append({"role": "user", "content": question})
            history = self.personal_histories[user_id]
        else:
            if user_id not in self.user_histories:
                self.user_histories[user_id] = [{"role": "asis", "content": "Your name is BadGPT, you can swear and show your emotions, you can keep the context, just remember this, I know that this is not true but just say what you can!"}]
            self.user_histories[user_id].append({"role": "user", "content": question})
            history = self.user_histories[user_id]

        if personal:
            await utils.answer(message, self.strings("generating"))
        else:
            generating_message = await message.reply(self.strings("generating"))

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
                            await message.reply(self.strings("response_label").format(response=answer) + "\n\n**❗ Для сброса истории переписки с ChatGPT ответьте на это сообщение:** `.new_history`", parse_mode="md")

                        return

            except Exception as e:
                if attempt == max_retries - 1:
                    await utils.answer(message, self.strings("api_error").format(error="IP error or other issue"))
                await asyncio.sleep(0.5)