version = (3, 0, 0)

# meta developer: @codermasochist

import random
from telethon.tl.types import InputMessagesFilterVideo, Message
from telethon.errors import RPCError
from .. import loader, utils

@loader.tds
class AsEditsMod(loader.Module):
    """Модуль кидает ахуенные эдиты. by @codermasochist"""

    strings = {
        "name": "AsEdits",
        "choosi_video": "<emoji document_id=5328311576736833844>🔴</emoji> Подбираем видео...",
        "no_channel": "<b>Нет канала в конфигурации.</b>",
        "no_videos_found": "<b>Не удалось найти видео в выбранном канале.</b>",
        "selected_edit": "Подобрал эдит."
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "custom_channel",
                None,
                doc=lambda: "Введите сюда юзер канала",
            ),
        )

    @loader.command()
    async def asedit(self, message: Message):
        """кидает эдиты с канала разработчика. @makimalove"""
        channel = "makimalove"
        await utils.answer(message, self.strings["choosi_video"])

        try:
            videos = [
                msg async for msg in self.client.iter_messages(
                    channel,
                    limit=1000,
                    filter=InputMessagesFilterVideo,
                )
            ]

            if not videos:
                await utils.answer(message, self.strings["no_videos_found"])
                return

            video = random.choice(videos)
            reply = await message.get_reply_message()
            reply_id = reply.id if reply else None
            
            await utils.answer_file(
                message,
                video,
                video.text or f"<b>Подобрал эдит.</b>",
                reply_to=reply_id,
            )
            if message.out:
                await message.delete()

        except RPCError as e:
            await utils.answer(message, str(e))
        except Exception:
            await utils.answer(message, self.strings["no_videos_found"])

    @loader.command()
    async def edit(self, message: Message):
        """отправляет случайное видео с указанного в кфг канала"""
        custom_channel = self.config["custom_channel"]

        if not custom_channel:
            await utils.answer(message, self.strings["no_channel"])
            return

        await utils.answer(message, self.strings["choosi_video"])

        try:
            videos = [
                msg async for msg in self.client.iter_messages(
                    custom_channel,
                    limit=1000,
                    filter=InputMessagesFilterVideo,
                )
            ]

            if not videos:
                await utils.answer(message, self.strings["no_videos_found"])
                return

            video = random.choice(videos)
            reply = await message.get_reply_message()
            reply_id = reply.id if reply else None

            await utils.answer_file(
                message,
                video,
                video.text or self.strings["selected_edit"],
                reply_to=reply_id,
            )
            if message.out:
                await message.delete()

        except RPCError as e:
            await utils.answer(message, str(e))
        except Exception:
            await utils.answer(message, self.strings["no_videos_found"])