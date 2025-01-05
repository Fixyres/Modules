# meta developer: @Foxy437
# Попросил сделать: @qequqo

from .. import loader, utils

@loader.tds
class BoldMod(loader.Module):
    """Модуль для авто замены шрифта на жирный."""
    strings = {"name": "Bold"}
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.db.set(self.strings["name"], "bold_enabled", False)

    async def on_boldcmd(self, message):
        """Включить авто замену шрифта на жирный."""
        self.db.set(self.strings["name"], "bold_enabled", True)
        await utils.answer(message, "СЭР ДА СЭР!")

    async def off_boldcmd(self, message):
        """Выключить авто замену шрифта на жирный."""
        self.db.set(self.strings["name"], "bold_enabled", False)
        await utils.answer(message, "СЭР ДА СЭР!")

    async def watcher(self, message):
        if self.db.get(self.strings["name"], "bold_enabled"):
            if message.out:
                bold_text = f"<b>{message.text}</b>"
                await message.edit(bold_text)
