import contextlib
import logging
import re
import base64
from typing import Union, List, Dict, Tuple

import requests

from .. import loader, utils

logger = logging.getLogger(__name__)

# Паттерны для обнаружения различных методов шифрования
encryption_patterns = {
    "pyarmor": r"__pyarmor__",
    "marshal": r"import\s+marshal",
    "zlib": r"import\s+zlib",
    "lzma": r"import\s+lzma",
    "bz2": r"import\s+bz2",
    "compile": r"compile\s*\([^)]*\)"
}

checker_regex = {
    "critical": [
        {
            "command": "DeleteAccountRequest", 
            "perms": "может удалить ваш аккаунт Telegram", 
            "details": "Эта функция позволяет полностью удалить ваш аккаунт Telegram без возможности восстановления"
        },
        {
            "command": "edit_2fa", 
            "perms": "может изменить ваш пароль двухфакторной аутентификации", 
            "details": "Модуль способен менять настройки безопасности вашего аккаунта, включая пароль двухфакторной аутентификации"
        },
        {
            "command": "get_me", 
            "perms": "может получить доступ к данным вашего профиля", 
            "details": "Получает доступ к вашим личным данным: имени, фото профиля, статусу и другим настройкам"
        },
        {
            "command": "disconnect", 
            "perms": "может отключить ваш аккаунт от Telegram", 
            "details": "Может принудительно разорвать соединение вашего аккаунта с серверами Telegram"
        },
        {
            "command": "log_out", 
            "perms": "может выйти из вашего аккаунта", 
            "details": "Способен завершить текущую сессию, выйдя из вашего аккаунта"
        },
        {
            "command": "ResetAuthorizationRequest", 
            "perms": "может сбросить все ваши активные сессии", 
            "details": "Позволяет завершить все активные сессии на всех устройствах, где вы авторизованы"
        },
        {
            "command": "GetAuthorizationsRequest", 
            "perms": "может украсть данные для входа в ваш аккаунт", 
            "details": "Получает информацию о всех устройствах, где вы авторизованы, что может быть использовано для кражи аккаунта"
        },
        {
            "command": "AddRequest", 
            "perms": "может украсть данные для входа в ваш аккаунт", 
            "details": "Позволяет создавать новые сессии доступа к вашему аккаунту без вашего ведома"
        },
        {
            "command": "pyarmor", 
            "perms": "содержит зашифрованный код - может быть вредоносным", 
            "details": "Использует специальное шифрование кода, что может скрывать опасные функции от проверки"
        },
        {
            "command": "pyrogram", 
            "perms": "использует другой клиент Telegram - может быть опасно", 
            "details": "Применяет альтернативный клиент Telegram, который может иметь меньше ограничений безопасности"
        },
        {
            "command": "system|os\\.system", 
            "perms": "может выполнять любые команды на вашем устройстве", 
            "details": "Получает полный доступ к выполнению системных команд на вашем устройстве"
        },
        {
            "command": "eval", 
            "perms": "может выполнить любой Python код на вашем устройстве", 
            "details": "Позволяет запускать любой код Python без ограничений, что очень опасно"
        },
        {
            "command": "exec", 
            "perms": "может выполнить любой Python код на вашем устройстве", 
            "details": "Аналогично eval, даёт возможность выполнять произвольный код Python"
        },
        {
            "command": "sessions", 
            "perms": "может получить доступ к вашим сессиям Telegram", 
            "details": "Получает доступ к файлам ваших сессий, что может быть использовано для кражи аккаунта"
        },
        {
            "command": "subprocess", 
            "perms": "может выполнять любые команды на вашем устройстве", 
            "details": "Позволяет запускать любые системные процессы на вашем устройстве"
        },
        {
            "command": "torpy", 
            "perms": "может скачивать опасные файлы через TOR", 
            "details": "Использует сеть TOR для скачивания файлов, обходя блокировки и скрывая активность"
        },
        {
            "command": "httpimport", 
            "perms": "может загружать вредоносный код из интернета", 
            "details": "Позволяет загружать и выполнять код напрямую из интернета без проверки"
        },
        {
            "command": "base64\\.|b64decode|b64encode", 
            "perms": "использует шифрование - может скрывать вредоносный код", 
            "details": "Применяет кодирование base64, которое может использоваться для сокрытия опасного кода"
        }
    ],
    "warn": [
        {
            "command": "list_sessions", 
            "perms": "может просматривать ваши сессии", 
            "details": "Получает список всех ваших активных сессий в Telegram"
        },
        {
            "command": "LeaveChannelRequest", 
            "perms": "может выходить из ваших групп и каналов", 
            "details": "Способен автоматически покидать группы и каналы от вашего имени"
        },
        {
            "command": "JoinChannelRequest", 
            "perms": "может подписываться на группы и каналы от вашего имени", 
            "details": "Может автоматически присоединяться к группам и каналам без вашего согласия"
        },
        {
            "command": "ChannelAdminRights", 
            "perms": "может менять права администраторов в ваших чатах", 
            "details": "Имеет возможность управлять правами администраторов в группах, где вы админ"
        },
        {
            "command": "EditBannedRequest", 
            "perms": "может банить участников в ваших чатах", 
            "details": "Способен блокировать пользователей в группах от вашего имени"
        },
        {
            "command": "remove|unlink", 
            "perms": "может удалять файлы с вашего устройства", 
            "details": "Имеет доступ к удалению файлов на вашем устройстве"
        },
        {
            "command": "rmdir|rmtree", 
            "perms": "может удалять папки с вашего устройства", 
            "details": "Может удалять целые папки с файлами на вашем устройстве"
        },
        {
            "command": "telethon", 
            "perms": "использует прямой доступ к Telegram API", 
            "details": "Работает напрямую с API Telegram, что даёт широкие возможности управления"
        },
        {
            "command": "get_response", 
            "perms": "может читать ваши сообщения", 
            "details": "Имеет доступ к содержимому ваших сообщений в Telegram"
        }
    ],
    "info": [
        {
            "command": "requests", 
            "perms": "отправляет запросы в интернет", 
            "details": "Может обмениваться данными с разными веб-сервисами"
        },
        {
            "command": "get_entity", 
            "perms": "получает информацию о пользователях", 
            "details": "Собирает базовую информацию о пользователях Telegram"
        },
        {
            "command": "get_dialogs", 
            "perms": "получает список ваших чатов", 
            "details": "Может просматривать список всех ваших диалогов в Telegram"
        },
        {
            "command": "os\\.path|os\\.name", 
            "perms": "получает информацию о системе", 
            "details": "Считывает основную информацию о вашей операционной системе"
        },
        {
            "command": "sys\\.", 
            "perms": "получает информацию о Python", 
            "details": "Получает доступ к системным функциям Python"
        },
        {
            "command": "import", 
            "perms": "подключает дополнительные модули", 
            "details": "Использует дополнительные библиотеки Python для своей работы"
        },
        {
            "command": "client", 
            "perms": "использует функции Telegram", 
            "details": "Взаимодействует с основными функциями клиента Telegram"
        },
        {
            "command": "send_message", 
            "perms": "отправляет сообщения", 
            "details": "Может отправлять сообщения через ваш аккаунт"
        },
        {
            "command": "send_file", 
            "perms": "отправляет файлы", 
            "details": "Способен отправлять файлы через Telegram"
        },
        {
            "command": "TelegramClient", 
            "perms": "создаёт подключение к Telegram", 
            "details": "Устанавливает новое соединение с серверами Telegram"
        },
        {
            "command": "download_file", 
            "perms": "скачивает файлы", 
            "details": "Может загружать файлы из Telegram"
        },
        {
            "command": "ModuleConfig", 
            "perms": "имеет настройки", 
            "details": "Содержит настраиваемые параметры для работы модуля"
        }
    ]
}

@loader.tds
class ModuleCheckerMod(loader.Module):
    """С помощью данного модуля вы можете проверять остальные модули как и на просто что он может делать. Так и на шифровку (расшифровка base64 кода автоматизирована)\n🤍Создатель - @OS7NT"""

    strings = {
        "name": "Warlock Checker",
        "description": "Создатель - @OS7NT",
        "loading": "🔄 <b>Проверяю модуль...</b>",
        "answer": "🔍 <b>Результаты проверки модуля</b>:\n\n{findings}",
        "component": "• {perms}",
        "error": (
            "❌ <b>Ошибка!</b>\n\n"
            "<i>Как использовать:</i>\n"
            "▫️ Отправьте <code>.п</code> и ссылку на модуль\n"
            "▫️ Ответьте командой <code>.п</code> на файл модуля\n"
            "▫️ Отправьте файл модуля с командой <code>.п</code>"
        ),
        "no_findings": "• Ничего не найдено",
        "base64_found": (
            "🔐 <b>Обнаружен зашифрованный Base64 код!</b>\n"
            "<b>Результаты проверки расшифрованного кода</b>:\n\n"
            "{findings}"
        ),
        "encryption_warning": (
            "⚠️ <b>Внимание! В модуле обнаружены методы шифрования кода:</b>\n"
            "{methods}\n"
            "❗️ Код специально скрыт от проверки - будьте осторожны!"
        ),
        "category_headers": {
            "critical": "⛔️ <b>Опасные функции</b> (будьте осторожны!):\n",
            "warn": "⚠️ <b>Подозрительные функции</b> (обратите внимание):\n",
            "info": "ℹ️ <b>Обычные функции</b> (не опасно):\n"
        },
        "encryption_methods": {
            "pyarmor": "PyArmor",
            "marshal": "Marshal",
            "zlib": "Zlib",
            "lzma": "LZMA",
            "bz2": "BZ2",
            "compile": "Скомпилированный код"
        }
    }

    def _format_findings(self, results: Dict[str, List[str]]) -> str:
        """Форматирует результаты проверки в единый текст"""
        output = []
        for category in ["critical", "warn", "info"]:
            if results[category]:
                output.append(self.strings["category_headers"][category] + 
                            "\n".join(self.strings["component"].format(perms=perm)
                                    for perm in results[category]))
            else:
                output.append(self.strings["category_headers"][category] + 
                            self.strings["no_findings"])
        return "\n\n".join(output)

    def _find_base64(self, string: str) -> List[str]:
        """Находит base64 код в строке"""
        base64_pattern = r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})'
        potential_base64 = re.finditer(base64_pattern, string)
        decoded = []
        
        for match in potential_base64:
            encoded = match.group()
            if len(encoded) < 20:
                continue
                
            try:
                decoded_text = base64.b64decode(encoded).decode('utf-8')
                if all(ord(char) < 128 for char in decoded_text):
                    decoded.append(decoded_text)
            except:
                continue
                
        return decoded

    def _check_encryption_methods(self, code: str) -> List[str]:
        """Проверяет код на наличие методов шифрования"""
        found_methods = []
        for method, pattern in encryption_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                found_methods.append(self.strings["encryption_methods"][method])
        return found_methods

    async def _check_code(self, code: str) -> Dict[str, List[str]]:
        """Проверяет код на наличие подозрительных паттернов"""
        results = {
            "critical": set(),
            "warn": set(),
            "info": set()
        }
        
        for category in checker_regex:
            for item in checker_regex[category]:
                if re.search(item["command"], code, re.IGNORECASE):
                    results[category].add(item["perms"])
                    
        return {k: list(v) for k, v in results.items()}

    async def пcmd(self, message):
        """Проверить модуль на опасный код"""
        await utils.answer(message, self.strings["loading"])
        
        args = utils.get_args_raw(message)
        code = None
        
        if args:
            try:
                r = await utils.run_sync(requests.get, args)
                code = r.text
            except Exception:
                pass
                
        if not code:
            try:
                code = (await self.client.download_file(message.media, bytes)).decode("utf-8")
            except Exception:
                try:
                    reply = await message.get_reply_message()
                    code = (await self.client.download_file(reply.media, bytes)).decode("utf-8")
                except Exception:
                    code = None

        if not code:
            await utils.answer(message, self.strings["error"])
            return

        response_lines = []

        # Сначала проверяем на методы шифрования
        encryption_methods = self._check_encryption_methods(code)
        if encryption_methods:
            response_lines.append(
                self.strings["encryption_warning"].format(
                    methods="\n".join(f"• {method}" for method in encryption_methods)
                )
            )

        # Ищем base64 код
        decoded_texts = self._find_base64(code)
        if decoded_texts:
            # Если найден base64, проверяем только расшифрованный код
            decoded_results = {"critical": set(), "warn": set(), "info": set()}
            for decoded in decoded_texts:
                results = await self._check_code(decoded)
                for category in results:
                    decoded_results[category].update(results[category])
                    
            decoded_results = {k: list(v) for k, v in decoded_results.items()}
            findings = self._format_findings(decoded_results)
            response_lines.append(
                self.strings["base64_found"].format(findings=findings)
            )
        else:
            # Если base64 не найден, проверяем исходный код
            results = await self._check_code(code)
            findings = self._format_findings(results)
            response_lines.append(findings)

        # Формируем финальный ответ
        await utils.answer(
            message,
            self.strings["answer"].format(
                findings="\n\n".join(response_lines)
            )
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db