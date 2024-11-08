from .. import loader, utils
from telethon.tl.types import Message

@loader.tds
class ZOVMod(loader.Module):
    strings = {
        "name": "ZOV Text Modifier"
    }

    async def client_ready(self, client, db):
        self.db = db
        self._client = client
        self.enabled = self.db.get("zovmod", "enabled", False)

    async def zovcmd(self, message: Message):
        """Включить или отключить режим ZOV с опциональным аргументом vivo"""
        args = utils.get_args_raw(message)
        self.enabled = not self.enabled
        self.db.set("zovmod", "enabled", self.enabled)

        if self.enabled:
            response = "<b><emoji document_id=5260237736664643163>🔤</emoji> Режим ZOV успешно включен.</b>"
            if args == "vivo":
                self.db.set("zovmod", "vivo_mode", True)
            else:
                self.db.set("zovmod", "vivo_mode", False)
        else:
            response = "<emoji document_id=5210952531676504517>🚫</emoji> <b>Режим ZOV отключен</b>"

        await utils.answer(message=message, response=response)

    async def watcher(self, message: Message):
        if self.enabled and message.out:
            # Заменяем буквы на указанные символы
            new_text = message.text.translate(str.maketrans({
                'о': 'O', 'О': 'O',
                'з': 'Z', 'З': 'Z',
                'в': 'V', 'В': 'V',
                'н': 'N', 'Н': 'N',
                'ш': 'Zh', 'Ш': 'Zh'
            }))

            # Проверяем, включен ли режим vivo
            if self.db.get("zovmod", "vivo_mode", False):
                new_text += "\nСмартфон vivo"

            # Редактируем сообщение с новым текстом
            await self._client.edit_message(message.peer_id, message.id, new_text)