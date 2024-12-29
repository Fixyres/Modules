# -*- coding: utf-8 -*-
# Hikka Userbot Module
# Модуль для просмотра мешка в Irise by @zhako_o7

from .. import loader, utils
import asyncio  # Для ожидания ответа

class IrisMesh(loader.Module):
    """Модуль для просмотра мешка в Irise by @zhako_o7"""
    strings = {"name": "IrisMesh"}

    async def бcmd(self, message):
        """Используйте .б как ответ на сообщение"""
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("❌ Команда должна быть ответом на сообщение!")
            return
        
        # Получаем информацию о пользователе
        user = reply.sender
        if not user:
            await message.edit("❌ Не удалось получить информацию о пользователе!")
            return

        # Используем username, если есть, иначе ID в формате @ID
        username = f"@{user.username}" if user.username else f"@{user.id}"
        bag_message = f"мешок {username}"
        
        # Изменяем сообщение на "Ожидайте"
        await message.edit("⏳ Ожидайте...")

        # Отправляем сообщение в личку бота
        await message.client.send_message("@iris_black_bot", bag_message)

        # Устанавливаем время ожидания для ответа от бота (4 секунды)
        try:
            # Ждем, пока бот отправит сообщение в чат (не важно, будет ли это реплай)
            await asyncio.sleep(1)  # Даем немного времени боту ответить
            messages = await message.client.get_messages("@iris_black_bot", limit=1)

            # Проверяем, пришел ли ответ от бота
            if messages and messages[0].text:
                # Если бот отправил сообщение, проверяем на "не разрешал заглядывать"
                bot_response = messages[0].text.lower()
                if "не разрешал заглядывать" in bot_response:
                    # Если мешок закрыт, выводим "Мешок закрыт"
                    await message.edit("❌ Мешок закрыт!")
                else:
                    # Если ответ найден, заменяем сообщение
                    await message.edit(messages[0].text)
            else:
                # Если ответа от бота нет
                await message.edit("❌ Бот не ответил!")
        except asyncio.TimeoutError:
            # Если тайм-аут, сообщаем, что бот не ответил
            await message.edit("❌ Бот не ответил в течение 4 секунд.")

