from telethon.tl.functions.channels import JoinChannelRequest
import aiohttp
from bs4 import BeautifulSoup
from .. import loader, utils

#meta developer: Ksenon

@loader.tds
class HabrParserMod(loader.Module):
    """🖥️ Модуль для поиска статей на Хабре"""

    strings = {"name": "HabrParser"}

    async def client_ready(self, client, db):
        await client(JoinChannelRequest("ksenonmodules"))

    @loader.command()
    async def habr(self, message):
        """🔎 Поиск статей на Хабре. Использование: .habr <запрос>"""
        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, "⚠️ Пожалуйста, укажите поисковый запрос!")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://habr.com/ru/search/?q={query}&target_type=posts") as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                articles = soup.find_all('article', class_='tm-articles-list__item')[:5]

                if not articles:
                    await utils.answer(message, "😕 По вашему запросу ничего не найдено.")
                    return

                result = "┏ 🖥️ HabrParser\n┃\n"
                for article in articles:
                    title_elem = article.find('h2', class_='tm-title tm-title_h2')
                    title = title_elem.text.strip() if title_elem else "Заголовок не найден"

                    url_elem = article.find('a', class_='tm-title__link')
                    url = "https://habr.com" + url_elem['href'] if url_elem else "URL не найден"

                    description_elem = article.find('div', class_='article-formatted-body')
                    description = description_elem.text.strip() if description_elem else "Описание не найдено"

                    result += f"┣ 📑 <b>{title}</b>\n┃ \n"
                    result += f"┣ 💭 <code>{description[:100]}...</code>\n┃\n"
                    result += f"┣ 🌍 <code>{url}</code>\n┃\n"

                result += "┃\n┗ 🕶️ Habr"

                await utils.answer(message, result)