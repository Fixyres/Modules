from .. import loader, utils
from telethon.tl.types import Message
from ..inline.types import InlineCall
import aiohttp
import asyncio
import time
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

@loader.tds
class MW_APIMod(loader.Module):
    """🤖 Продвинутый модуль для работы с различными AI моделями"""

    strings = {
        "name": "MW API",
        "processing": "🤔 <b>Обрабатываю запрос...</b>",
        "response": "🤖 <b>Ответ от {}:</b>\n\n{}\n\n⏱ Время: {:.2f}с\n📊 Модель: {}\n🔧 API: MW",
        "error": "🚫 <b>Произошла ошибка при обработке запроса</b>",
        "no_args": "❌ <b>Укажите запрос!</b>",
        "settings_header": "⚙️ <b>Настройки MW API</b>\n\n📝 <b>Текущая модель:</b> <code>{}</code>",
        "model_changed": "✅ <b>Модель изменена на:</b> <code>{}</code>",
        "select_model": "🔄 <b>Выберите модель AI:</b>",
        "not_subscribed": (
            "🔒 <b>Для использования модуля необходимо подписаться на канал:</b>\n"
            "@mwapi_dev"
        ),
        "rate_limit": "⏱ <b>Подождите {} секунд между запросами</b>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "API_URL",
            "http://146.19.48.160:25974/generate",
            "URL API",

            "MODEL",
            "gpt3",
            "Модель по умолчанию",

            "RATE_LIMIT",
            2,
            "Задержка между запросами (в секундах)"
        )
        self.last_request = 0
        self.models = {
            
            "antigpt": "Anti-GPT",
            "gpt3": "GPT 3.5",
            "gemini-pro": "Gemini 1.5 Pro",
            "gpt4-turbo": "GPT-4 Turbo",
            "gpt4": "GPT-4",
            "gemini": "Gemini 1.5 Flash"
        }

    async def _check_subscription(self, message: Message) -> bool:
        try:
            await self.client(GetParticipantRequest(
                channel="@mwapi_dev",
                participant=message.sender_id
            ))
            return True
        except UserNotParticipantError:
            await self.inline.form(
                message=message,
                text=self.strings["not_subscribed"],
                reply_markup=[
                    [
                        {
                            "text": "📢 Подписаться",
                            "url": "https://t.me/mwapi_dev"
                        }
                    ],
                    [
                        {
                            "text": "🔄 Проверить подписку",
                            "callback": self._check_sub_callback
                        }
                    ]
                ],
                silent=True
            )
            return False
        except Exception:
            return True

    async def _check_sub_callback(self, call: InlineCall):
        try:
            await self.client(GetParticipantRequest(
                channel="@mwapi_dev",
                participant=call.from_user.id
            ))
            await call.edit(
                "✅ <b>Спасибо за подписку!</b>\n"
                "Теперь вы можете использовать все функции модуля.",
                reply_markup=[[{"text": "🔥 Начать", "action": "close"}]]
            )
        except UserNotParticipantError:
            await call.answer("❌ Вы все ещё не подписаны на канал!", show_alert=True)
        except Exception:
            await call.answer("🤔 Не удалось проверить подписку", show_alert=True)

    def get_model_buttons(self):
        buttons = []
        row = []
        for model_key, model_name in self.models.items():
            if len(row) == 2:
                buttons.append(row)
                row = []
            row.append({
                "text": model_name,
                "callback": self.model_callback,
                "args": (model_key,)
            })
        if row:
            buttons.append(row)

        buttons.append([{"text": "🔙 Закрыть", "action": "close"}])
        return buttons

    async def model_callback(self, call: InlineCall, model: str):
        self.config["MODEL"] = model
        await call.edit(
            self.strings["settings_header"].format(self.models[model]),
            reply_markup=self.get_model_buttons()
        )

    @loader.command()
    async def ai(self, message: Message):
        """🤖 Запрос к AI. Использование: .ai <запрос>"""
        if not await self._check_subscription(message):
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"])
            return

        if time.time() - self.last_request < self.config["RATE_LIMIT"]:
            await utils.answer(
                message,
                self.strings["rate_limit"].format(self.config["RATE_LIMIT"])
            )
            return

        self.last_request = time.time()
        status = await utils.answer(message, self.strings["processing"])
        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config["API_URL"],
                    json={
                        "prompt": args,
                        "model_name": self.config["MODEL"]
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=30
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    response_time = time.time() - start_time

                    await self.inline.form(
                        message=status,
                        text=self.strings["response"].format(
                            self.models[self.config["MODEL"]],
                            result.get("response", "Нет ответа"),
                            response_time,
                            self.config["MODEL"]
                        ),
                        reply_markup=[
                            [
                                {
                                    "text": "🔄 Повторить",
                                    "callback": self.retry_request,
                                    "args": (args,)
                                },
                                {
                                    "text": "📝 Новый запрос",
                                    "callback": self.new_request
                                }
                            ],
                            [
                                {
                                    "text": "⚙️ Сменить модель",
                                    "callback": self.show_models
                                }
                            ],
                            [
                                {
                                    "text": "🔙 Закрыть",
                                    "action": "close"
                                }
                            ]
                        ]
                    )

        except Exception:
            await utils.answer(status, self.strings["error"])

    async def retry_request(self, call: InlineCall, query: str):
        message = await call.edit(self.strings["processing"])
        await self.ai(message)

    async def new_request(self, call: InlineCall):
        await call.edit(
            "✍️ <b>Введите новый запрос:</b>",
            reply_markup=[[{"text": "🔙 Отмена", "action": "close"}]]
        )

    async def show_models(self, call: InlineCall):
        await call.edit(
            self.strings["select_model"],
            reply_markup=self.get_model_buttons()
        )

    @loader.command()
    async def aimodels(self, message: Message):
        """⚙️ Настройки и выбор модели"""
        if not await self._check_subscription(message):
            return

        await self.inline.form(
            message=message,
            text=self.strings["settings_header"].format(
                self.models[self.config["MODEL"]]
            ),
            reply_markup=self.get_model_buttons()
        )
