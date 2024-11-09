__version__ = (1, 2, 5)

#            © Copyright 2024
#           https://t.me/HikkTutor 
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
#┏┓━┏┓━━┏┓━━┏┓━━┏━━━━┓━━━━━┏┓━━━━━━━━━━━━
#┃┃━┃┃━━┃┃━━┃┃━━┃┏┓┏┓┃━━━━┏┛┗┓━━━━━━━━━━━
#┃┗━┛┃┏┓┃┃┏┓┃┃┏┓┗┛┃┃┗┛┏┓┏┓┗┓┏┛┏━━┓┏━┓━━━━
#┃┏━┓┃┣┫┃┗┛┛┃┗┛┛━━┃┃━━┃┃┃┃━┃┃━┃┏┓┃┃┏┛━━━━
#┃┃━┃┃┃┃┃┏┓┓┃┏┓┓━┏┛┗┓━┃┗┛┃━┃┗┓┃┗┛┃┃┃━━━━━
#┗┛━┗┛┗┛┗┛┗┛┗┛┗┛━┗━━┛━┗━━┛━┗━┛┗━━┛┗┛━━━━━
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# load from: t.me:HikkTutor 
# meta developer:@HikkTutor 
# meta banner:https://t.me/HikkTutor
# name: Fping

import os
import time
import random
import asyncio
from datetime import datetime
from .. import loader, utils

@loader.tds
class FpingMod(loader.Module):
    """Модуль для настройки и отображения фейкового пинга"""

    strings = {
        "name": "Fping",
        "results_ping": (
            "<emoji document_id=5431449001532594346>⚡️</emoji> <b>Скорость отклика Telegram:</b> <b><code>{}</code> ms</b>\n"
            "<emoji document_id=5445284980978621387>🚀</emoji> <b>Прошло с последней перезагрузки:</b> <b>{}</b>"
        ),
        "moon": "🌘",
        "additional_info": (
            "<emoji document_id=5472146462362048818>💡</emoji> <i>Скорость отклика Telegram в большей степени зависит от загруженности серверов Telegram и других внешних факторов и никак не связана с параметрами сервера, на который установлен юзербот</i>"
        ),
        "future_messages": [
            "да честно говорю, я просто из будущего и живу прямо на спутнике",
            "провайдер настолько боится {username}, что делает ему отрицательный пинг",
            "ваш интернет быстрее, чем скорость света, {username}!",
            "кажется, ваше соединение обогнало время, {username}!",
            "<b>Ошибка:</b> <i>Вы разорвали пространственно-временной континуум.</i>"
        ],
        "future_messages_double_minus": [
            "вы разорвали вселенную, {username}!",
            "ваше соединение достигло бесконечности и за ее пределы!",
            "ваш интернет так быстр, что он обогнал сам себя, {username}!",
            "вы находитесь впереди всех времен, {username}!",
            "<b>Ошибка:</b> <i>Вы создали новую линию времени.</i>",
            "время и пространство больше не имеют значения для вашего интернета, {username}!",
            "ваш пинг настолько отрицательный, что вы видите будущее, {username}!",
            "ваш сигнал достиг антиматерии и вернулся, {username}!",
            "вы настолько быстры, что даже свет не успевает за вами, {username}!",
            "ваше соединение — это новое определение скорости, {username}!"
        ],
        "invalid_input": "<b>Пожалуйста, укажите корректное значение пинга в миллисекундах.</b>",
        "infinity_error": "<b>Ошибка:</b> Бесконечность - предел!"
    }

    def __init__(self):
        self.name = self.strings["name"]
        self.config_dir = utils.get_base_dir()
        self.boot_time_file = os.path.join(self.config_dir, "boot_time.txt")
        self.record_boot_time()

    def record_boot_time(self):
        """Записывает текущее время как время последней загрузки модуля."""
        with open(self.boot_time_file, 'w') as file:
            file.write(str(datetime.now().timestamp()))

    def get_uptime(self):
        """Возвращает время, прошедшее с момента последней загрузки модуля."""
        with open(self.boot_time_file, 'r') as file:
            boot_time = float(file.read().strip())
        boot_datetime = datetime.fromtimestamp(boot_time)
        return datetime.now() - boot_datetime

    @loader.command()
    async def fping(self, message):
        """Устанавливает и отображает фейковый пинг"""
        args = utils.get_args(message)
        if not args or not args[0].lstrip('-').isdigit():
            await utils.answer(message, self.strings["invalid_input"])
            return

        if args[0].startswith('---'):
            await utils.answer(message, self.strings["infinity_error"])
            return

        base_ping = int(args[0].lstrip('-'))
        double_minus = args[0].startswith('--')

        if double_minus:
            base_ping = min(max(base_ping, -10000), 25000)
        else:
            base_ping = min(max(base_ping, 0), 25000)

        if args[0].startswith('-'):
            minus_prefix = '--' if double_minus else '-'
            realistic_ping_with_decimal = f"{minus_prefix}{base_ping}.000"
            initial_delay = final_delay = 0.5
        else:
            deviation = int(base_ping / 25)
            realistic_ping = base_ping + random.randint(-deviation, deviation)
            realistic_ping_with_decimal = f"{realistic_ping}.{random.randint(100, 999)}"
            initial_delay = random.uniform(0.3, 0.5)
            final_delay = max(0, realistic_ping / 1000 - initial_delay)

        await message.edit(".рing")
        time.sleep(initial_delay)
        await utils.answer(message, self.strings["moon"])
        time.sleep(final_delay)

        uptime_simulated = self.get_uptime()
        formatted_uptime = str(uptime_simulated).split('.')[0]

        response = self.strings["results_ping"].format(realistic_ping_with_decimal, formatted_uptime)
        result_message = await utils.answer(message, response)

        if args[0].startswith('-'):
            await asyncio.sleep(2)
            sender = await message.get_sender()
            first_name = sender.first_name.strip() if sender.first_name else ""
            last_name = sender.last_name.strip() if sender.last_name else ""
            if first_name or last_name:
                username = f"{first_name} {last_name}".strip()
            else:
                username = "пользователь"
            future_message_list = self.strings["future_messages_double_minus"] if double_minus else self.strings["future_messages"]
            future_message = random.choice(future_message_list).format(username=username)
            await message.client.send_message(message.chat_id, future_message, reply_to=result_message.id)