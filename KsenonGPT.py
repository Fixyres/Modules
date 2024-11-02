from .. import loader, utils
import aiohttp
import io
import inspect
import gdown
import os
import requests
from bs4 import BeautifulSoup

# meta developer: @MeKsenon
# 🔒      Licensed under the GNU AGPLv3
# meta desc: Generate text and photo - FREE.

# requires: gdown

version = (1, 1, 5)
__version__ = version

# changelog: Малый баг-фикс 

@loader.tds
class KsenonGPTMod(loader.Module):
    """🤖 Модуль для работы с KsenonGPT и генерации изображений"""

    strings = {"name": "KsenonGPT"}

    async def client_ready(self, client, db):
        self.client = client
        self.github_token = await self.get_github_token()

    async def get_github_token(self):
        token_file = "github_token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                return f.read().strip()
        else:
            url = "https://drive.google.com/file/d/14ZyWbeOX5qKBiBAwaxQzuJpJKQ5nChM2/view?usp=drivesdk"
            file_id = url.split("/")[-2]
            download_url = f"https://drive.google.com/uc?id={file_id}"
            try:
                gdown.download(download_url, output=token_file, quiet=False)
                with open(token_file, "r") as f:
                    token = f.read().strip()
                return token
            except Exception as e:
                self.log.error(f"Ошибка при загрузке токена GitHub: {e}")
                return None

    @loader.command()
    async def gpt(self, message):
        """💬 Запрос к GPT с Интернетом. .gpt <запрос>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji><b> Укажите запрос для GPT.</b>")
            return

        await utils.answer(message, '<emoji document_id=5443038326535759644>💬</emoji> <b>Генерирую ответ на ваш запрос...</b>')

        url = "http://theksenon.pro/api/gpt/generate"
        headers = {"Content-Type": "application/json"}
        prompt = f"{args}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json={"prompt": prompt}) as response:
                    response.raise_for_status()
                    gpt_response = await response.text()
                    gpt_response = gpt_response.encode().decode('unicode-escape').replace('{"response":"', '').rstrip('}')

            await utils.answer(message, f'<emoji document_id=5443038326535759644>💬</emoji> <b>Запрос:</b> <i>{args}</i>\n\n<emoji document_id=5372981976804366741>🤖</emoji> <b>{gpt_response}</b>')

        except Exception as e:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Произошла ошибка при получении ответа от GPT: {str(e)}</b>")


    @loader.command()
    async def flux(self, message):
        """🎨 Сгенерировать фото, модель flux-pro. .flux <prompt>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji><b> Пожалуйста, укажите запрос для генерации изображения. </b>")
            return

        import random
        hints = [
            "<emoji document_id=5224607267797606837>☄️</emoji> <b>Добавьте \"pixel graphic\" чтобы получить пиксельное фото.</b>",
            "<emoji document_id=5224607267797606837>☄️</emoji> <b>Добавьте \"4K-hyper realistic\" чтобы получить реалистичный результат.</b>",
            "<emoji document_id=5224607267797606837>☄️</emoji> <b>Добавьте \"no blur\" чтобы не было размытия.</b>",
            "<emoji document_id=5224607267797606837>☄️</emoji> <b>Добавьте \"DSC_0123.JPG\" чтобы было супер реалистично.</b>",
            "" 
        ]
        hint = random.choice(hints)


        await utils.answer(message, f'<emoji document_id=5431456208487716895>🎨</emoji> <b>Генерирую изображение по запросу </b><i>"{args}"</i>\n{hint}')

        url = "http://theksenon.pro/api/flux/generate"
        headers = {"Content-Type": "application/json"}
        data = {"prompt": args}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    response.raise_for_status()
                    image_url = await response.text()

                async with session.get(image_url) as image_response:
                    image_response.raise_for_status()
                    image_content = io.BytesIO(await image_response.read())

            await message.delete()
            await self.client.send_file(
                message.chat_id,
                image_content,
                caption=(
                    "┏ <emoji document_id=5372981976804366741>🤖</emoji> <b>Изображение успешно создано!</b>\n"
                    "┃\n"
                    f"┣ <emoji document_id=5431456208487716895>🎨</emoji> <b>Запрос:</b> <i>{args}</i>\n"
                    "┃\n"
                    "┣ <emoji document_id=5447410659077661506>🌐</emoji> <b>Модель:</b> <i>flux-pro</i>\n"
                    "┃\n"
                    f"┗ <emoji document_id=5427009714745517609>✅</emoji> <b>Ссылка:</b> <a href='{image_url}'>Изображение</a>"
                )
            )
        except aiohttp.ClientError as e:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Ошибка при генерации изображения: {str(e)}</b>")
        except Exception as e:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Неизвестная ошибка: {str(e)}</b>")


    @loader.command()
    async def kupdate(self, message):
        """- Проверить обновления модуля."""
        module_name = "KsenonGPT"
        module = self.lookup(module_name)
        sys_module = inspect.getmodule(module)

        local_version = sys_module.version
        local_version_str = ".".join(map(str, local_version))

        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("https://api.github.com/repos/TheKsenon/MyHikkaModules/contents/ksenongpt.py") as response:
                if response.status == 200:
                    data = await response.json()
                    remote_content = await (await session.get(data['download_url'])).text()
                    remote_lines = remote_content.splitlines()

                    try:
                        version_line = next(line for line in remote_lines if line.strip().startswith("version ="))
                        new_version = tuple(map(int, version_line.split("=", 1)[1].strip().strip("()").replace(",", "").split()))
                        new_version_str = ".".join(map(str, new_version))

                        changelog = next((line.split(":", 1)[1].strip() for line in remote_lines if line.startswith("# changelog:")), "Нет информации")

                        if new_version > local_version:
                            await utils.answer(message,
                                f"<emoji document_id=5420323339723881652>⚠️</emoji> <b>У вас старая версия KsenonGPT!</b>\n\n"
                                f"<emoji document_id=5449683594425410231>🔼</emoji> <b>Новая версия: {new_version_str}</b>\n"
                                f"<emoji document_id=5447183459602669338>🔽</emoji> <b>У вас версия: {local_version_str}</b>\n\n"
                                f"<emoji document_id=5447410659077661506>🌐</emoji> <b>Change-log:</b>\n"
                                f"<emoji document_id=5458603043203327669>🔔</emoji> <i>{changelog}</i>\n\n"
                                f"<emoji document_id=5206607081334906820>✔️</emoji> <b>Команда для обновления:</b>\n"
                                f"<code>.dlmod {data['download_url']}</code>"
                            )
                        else:
                            await utils.answer(message,
                                f"<emoji document_id=5370870691140737817>🥳</emoji> <b>У вас последняя версия KsenonGPT!</b>\n\n"
                                f"<emoji document_id=5447644880824181073>⚠️</emoji><b> Разработчик модуля почти каждый день делают обновления и баг фиксы, так что часто проверяйте!</b>"
                            )
                    except StopIteration:
                        await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Не удалось найти информацию о версии в удаленном файле.</b>")
                    except Exception as e:
                        await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Произошла ошибка при обработке версии: {str(e)}</b>")
                else:
                    await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Не удалось проверить обновления. Попробуйте позже. ({response.status})</b>")

    @loader.command()
    async def google(self, message):
        """🔎 Искать в Google. Используй: .google <запрос>"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<emoji document_id=5210952531676504517>❌</emoji><b> Укажите запрос для поиска.</b>")
            return

        await message.edit("<emoji document_id=5188311512791393083>🔎</emoji><b>Ищу информацию в Google...</b>")

        query = args
        url = f"https://www.google.com/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            search_results = soup.find_all("div", class_="g")

            if not search_results:
                await message.edit("Результаты поиска не найдены.")
                return

            output = "┏ <emoji document_id=5188311512791393083>🔎</emoji> <b>Результаты поиска в Google:</b>\n┃\n"

            for i, result in enumerate(search_results[:3], 1):
                title_elem = result.find("h3")
                description_elem = result.find("div", class_="VwiC3b")
                link_elem = result.find("a")

                title = title_elem.text if title_elem else "Без названия"
                description = description_elem.text.strip() if description_elem else "Нет описания."
                link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else "Ссылка не найдена"

                output += f"┣ {i}️⃣ <b>{title}</b>\n"
                output += f"┣ 📑 <i>Описание: {description}</i>\n"
                output += f"┣ 🌐 URL: <a href='{link}'>Ссылка</a>\n┃\n"


            output += "┗  <emoji document_id=5427009714745517609>✅</emoji> KsenonGPT"
            await message.edit(output)

        except requests.RequestException as e:
            await message.edit(f"<emoji document_id=5210952531676504517>❌</emoji><b> Произошла ошибка при выполнении запроса: {e}</b>")
        except Exception as e:
            await message.edit(f"<emoji document_id=5210952531676504517>❌</emoji><b> Произошла неожиданная ошибка: {e}</b>")