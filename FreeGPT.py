#   █▀▀ ▄▀█   █▀▄▀█ █▀█ █▀▄ █▀
#   █▀░ █▀█   █░▀░█ █▄█ █▄▀ ▄█

#   https://t.me/famods

# 🔒    Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# ---------------------------------------------------------------------------------
# Name: FreeGPT
# Description: Бесплатный ChatGPT. БЕЗ API. БЕЗ БОТОВ.
# meta developer: @FAmods
# meta banner: https://github.com/FajoX1/FAmods/blob/main/assets/banners/freegpt.png?raw=true
# requires: g4f[all]
# ---------------------------------------------------------------------------------

import asyncio
import logging

from g4f.client import Client

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class FreeGPT(loader.Module):
    """Бесплатный ChatGPT. БЕЗ API. БЕЗ БОТОВ."""

    strings = {
        "name": "FreeGPT",

        "no_args": "<emoji document_id=5854929766146118183>❌</emoji> <b>Нужно </b><code>{}{} {}</code>",

        "asking_chatgpt": """<emoji document_id=5334675996714999970>🔄</emoji> <b>Спрашиваю ChatGPT...</b>

<i><emoji document_id=5370869711888194012>👾</emoji> Вы также можете получать ответы в реальном времены с помощью stream_answer в {prefix}cfg FreeGPT</i>""",
        "creating_image": "<emoji document_id=5334675996714999970>🔄</emoji> <b>Генерирую изображение...</b>",

        "answer_text": """<emoji document_id=5818813162815753343>👨‍💻</emoji> <b>Вопрос:</b> {question}

<emoji document_id=5372981976804366741>🤖</emoji> <b>Ответ:</b> {answer}

<emoji document_id=5424753383741346604>🖥</emoji> <b>Модель</b>: <code>{model}</code>""",

        "photo_caption": """<emoji document_id=5375074927252621134>🖼</emoji> <b>Промпт:</b> <code>{prompt}</code>
        
<emoji document_id=5424753383741346604>🖥</emoji> <b>Модель</b>: <code>{model}</code>""",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "model",
                "gpt-4o",
                lambda: "Модель ChatGPT",
            ),
            loader.ConfigValue(
                "image_model",
                "flux",
                lambda: "Модель для генерации изображений",
            ),
            loader.ConfigValue(
                "role",
                "user",
                lambda: "Кто ты для ChatGPT?",
            ),
            loader.ConfigValue(
                "stream_answer",
                False,
                lambda: "Ответ в реальном времени",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "stream_answer_delay",
                1.162131238129,
                lambda: "Задержка обновлений в реальном времени",
            ),
        )

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    @loader.command()
    async def gf(self, message):
        """Задать вопрос к ChatGPT"""
        q = utils.get_args_raw(message)
        if not q:
            return await utils.answer(message, self.strings["no_args"].format(self.get_prefix(), "gf", "[вопрос]"))

        if not self.config['stream_answer']:
            await utils.answer(message, self.strings['asking_chatgpt'].format(prefix=self.get_prefix()))

            client = Client()
            response = client.chat.completions.create(
                model=self.config['model'],
                messages=[{"role": self.config['role'], "content": q}],
                stream=False,
            )

            return await utils.answer(message, self.strings['answer_text'].format(question=q, answer=response.choices[0].message.content, model=self.config['model']))
        
        await utils.answer(message, self.strings['answer_text'].format(question=q, answer="<code>Загрузка...</code>", model=self.config['model']))

        client = Client()
        response = client.chat.completions.create(
            model=self.config['model'],
            messages=[{"role": self.config['role'], "content": q}],
            stream=self.config['stream_answer'],
        )

        response_text = ""

        for chunk in response:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                await utils.answer(message, self.strings['answer_text'].format(question=q, answer=response_text+"...", model=self.config['model']))
                await asyncio.sleep(self.config['stream_answer_delay'])

        return await utils.answer(message, self.strings['answer_text'].format(question=q, answer=response_text, model=self.config['model']))    

    @loader.command()
    async def gfi(self, message):
        """Сгенерировать картинку"""
        prompt = utils.get_args_raw(message)
        if not prompt:
            return await utils.answer(message, self.strings["no_args"].format(self.get_prefix(), "gfi", "[промпт]"))

        m = await utils.answer(message, self.strings['creating_image'])

        client = Client()
        response = client.images.generate(
            model=self.config['image_model'],
            prompt=prompt.replace(" ", "+"),
        )

        await self.client.send_file(m.peer_id, response.data[0].url, force_document=True, caption=self.strings['photo_caption'].format(prompt=prompt, model=self.config['image_model']))
        await m.delete()