import asyncio
import time
from telethon.errors import AlreadyInConversationError
from .. import loader

class Farm:
    async def _pay_taxes(self):
        try:
            async with self._client.conversation(self._bot, exclusive=False) as conv:
                for i in range(1, 8):
                    await asyncio.sleep(3)
                    await conv.send_message(f'планета {i}')
                    r = await conv.get_response()
                    await asyncio.sleep(3)
                    await r.click(0)
                    await asyncio.sleep(3)
                    print(f'Планета {i}, собрал прибыль')
        except AlreadyInConversationError:
            print("Уже есть открытая беседа, пропускаем")

    async def _explore_planet(self):
        try:
            async with self._client.conversation(self._bot, exclusive=False) as conv:
                await conv.send_message('испытать планету')
                print("испытываю планету")
        except AlreadyInConversationError:
            print("Уже есть открытая беседа, пропускаем")

    async def _send_bonus(self):
        try:
            async with self._client.conversation(self._bot, exclusive=False) as conv:
                await conv.send_message('бонус')
                print("Отправлено сообщение: бонус")
        except AlreadyInConversationError:
            print("Уже есть открытая беседа, пропускаем")

class AstroKs(loader.Module, Farm):
    """
    Модуль для фарма в @astro_GameBot от @Apolon99
    """

    strings = {"name": "AstroKs"}

    _bot = "@astro_GameBot"     
    
    def __init__(self):        
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "AutoTree",
                True,
                "Включить или отключить автофарм планет.",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "PlanetInterval",
                3600,
                "Интервал в секундах для сбора прибыли с планет.",
                validator=loader.validators.Integer(minimum=60),
            ),
            loader.ConfigValue(
                "BonusInterval",
                43200,
                "Интервал в секундах для отправки бонуса.",
                validator=loader.validators.Integer(minimum=3600),
            ),
        )            
     
    @loader.loop(interval=1, autostart=True)
    async def main_loop(self):
        current_time = time.time()
        
        if self.config["AutoTree"]:
            # Собираем налоги с планет с установленным интервалом
            if not self.get("Tree_time") or (current_time - self.get("Tree_time")) >= self.config["PlanetInterval"]:
                await self._pay_taxes()
                self.set("Tree_time", int(current_time))
            
            # Испытываем планету каждый раз с установленным интервалом
            if not self.get("Explore_time") or (current_time - self.get("Explore_time")) >= self.config["PlanetInterval"]:
                await self._explore_planet()
                self.set("Explore_time", int(current_time))
            
            # Отправляем бонус с установленным интервалом
            if not self.get("Bonus_time") or (current_time - self.get("Bonus_time")) >= self.config["BonusInterval"]:
                await self._send_bonus()
                self.set("Bonus_time", int(current_time))
    
    @loader.command()
    async def astr(self, message):
        """- для начала авто фарминга в боте."""
        self.config["AutoTree"] = True
        self.main_loop.start()
        await message.edit("<b><i>автоматический фарм успешно начат!</i></b><emoji document_id=5436278610652577660>💀</emoji>\n<b><u>ожидайте</b></u>.")
        
    @loader.command()
    async def astrstop(self, message):
        """- для остановки фарма в боте."""
        self.config["AutoTree"] = False
        self.main_loop.stop()
        await message.edit("<b>автоматическая работа остановлена</b>. <emoji document_id=5433707707653704490>💀</emoji>")