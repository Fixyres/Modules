from .. import loader, utils
import aiohttp
from bs4 import BeautifulSoup

#meta developer: Ksenon

@loader.tds
class GoogleSearchMod(loader.Module):
    """🔍 Модуль для поиска в Google и красивого оформления результатов"""

    strings = {"name": "GoogleSearch"}

    @loader.command()
    async def gsearch(self, message):
        """🔎 Поиск в Google. Использование: .gsearch <запрос>"""
        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, "❌ Пожалуйста, укажите поисковый запрос!")
            return

        await utils.answer(message, "🕵️ Ищу информацию...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"https://www.google.com/search?q={query}&hl=ru") as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

        results = []
        for g in soup.find_all('div', class_='g'):
            title_elem = g.find('h3')
            snippet_elem = g.find('div', class_='VwiC3b')
            
            if title_elem and snippet_elem:
                title = title_elem.text
                snippet = snippet_elem.text.strip()
                results.append(f"<b>📌 {title}</b>\n{snippet}\n\n")

        if results:
            response = f"🔍 Результаты поиска по запросу '<b>{query}</b>':\n\n"
            response += "".join(results[:3])  # Ограничиваем до 3 результатов
            await utils.answer(message, response)
        else:
            await utils.answer(message, "😕 К сожалению, ничего не найдено.")