from .. import loader, utils
import aiohttp
from bs4 import BeautifulSoup
import re

#meta developer: Ksenon

@loader.tds
class EnhancedSearchMod(loader.Module):
    """🔍 Модуль для расширенного поиска с использованием Wikipedia и Google"""

    strings = {"name": "EnhancedSearch"}

    async def search_wikipedia(self, query):
        url = f"https://ru.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=1&explaintext=1&titles={query}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                pages = data['query']['pages']
                page_id = next(iter(pages))
                if 'extract' in pages[page_id]:
                    extract = pages[page_id]['extract']
                    if extract:
                        summary = re.split(r'(?<=[.!?])\s+', extract)[0]  # Берём первое предложение
                        if len(summary) > 300:
                            summary = summary[:300] + '...'
                        return f"📚 <b>Из Википедии:</b>\n{summary}\n<a href='https://ru.wikipedia.org/wiki/{query}'>Подробнее...</a>\n\n"
        return ""

    async def search_google(self, query):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"https://www.google.com/search?q={query}&hl=ru") as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

        results = []
        seen_titles = set()
        for g in soup.find_all('div', class_='g'):
            title_elem = g.find('h3')
            snippet_elem = g.find('div', class_='VwiC3b')
            link_elem = g.find('a')
            
            if title_elem and snippet_elem and link_elem:
                title = title_elem.text
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                snippet = snippet_elem.text.strip()
                link = link_elem['href']
                if snippet:
                    snippet = (snippet[:100] + '...') if len(snippet) > 100 else snippet
                results.append(f"🔗 <b><a href='{link}'>{title}</a></b>\n{snippet}\n\n")

            if len(results) == 3:
                break

        return results

    @loader.command()
    async def search(self, message):
        """🔎 Расширенный поиск. Использование: .search <запрос>"""
        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, "❌ Пожалуйста, укажите поисковый запрос!")
            return

        await utils.answer(message, "🕵️ Ищу информацию...")

        wiki_result = await self.search_wikipedia(query)
        google_results = await self.search_google(query)

        response = f"🔍 Результаты поиска по запросу '<b>{query}</b>':\n\n"
        response += wiki_result
        response += "<b>🌐 Результаты из Google:</b>\n\n" + "".join(google_results)

        await utils.answer(message, response)