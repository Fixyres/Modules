from .. import loader, utils
import aiohttp
import base64
import json

@loader.tds
class AdminFHMod(loader.Module):
    """<emoji document_id=5785175271011259591>🛠️</emoji> Модуль для управления файлами на GitHub"""

    strings = {
        "name": "AdminFH",
        "no_reply": "<emoji document_id=5210952531676504517>❌</emoji> Ответьте на файл .py",
        "invalid_extension": "<emoji document_id=5210952531676504517>❌</emoji> Файл должен иметь расширение .py",
        "upload_success": "<emoji document_id=5206607081334906820>✅</emoji> Файл успешно загружен: {}",
        "delete_success": "<emoji document_id=5206607081334906820>✅</emoji> Файл успешно удален: {}",
        "no_filename": "<emoji document_id=5210952531676504517>❌</emoji> Укажите имя файла (без .py)",
        "upload_error": "<emoji document_id=5210952531676504517>❌</emoji> Ошибка при загрузке: {}",
        "delete_error": "<emoji document_id=5210952531676504517>❌</emoji> Ошибка при удалении: {}",
        "no_token": "<emoji document_id=5210952531676504517>❌</emoji> GitHub токен не настроен. Используйте .settoken <ваш_токен>",
        "token_set": "<emoji document_id=5206607081334906820>✅</emoji> GitHub токен успешно установлен"
    }

    strings_ru = {
        "no_reply": "<emoji document_id=5210952531676504517>❌</emoji> Ответьте на файл .py",
        "invalid_extension": "<emoji document_id=5210952531676504517>❌</emoji> Файл должен иметь расширение .py",
        "upload_success": "<emoji document_id=5206607081334906820>✅</emoji> Файл успешно загружен: {}",
        "delete_success": "<emoji document_id=5206607081334906820>✅</emoji> Файл успешно удален: {}",
        "no_filename": "<emoji document_id=5210952531676504517>❌</emoji> Укажите имя файла (без .py)",
        "upload_error": "<emoji document_id=5210952531676504517>❌</emoji> Ошибка при загрузке: {}",
        "delete_error": "<emoji document_id=5210952531676504517>❌</emoji> Ошибка при удалении: {}",
        "no_token": "<emoji document_id=5210952531676504517>❌</emoji> GitHub токен не настроен. Используйте .settoken <ваш_токен>",
        "token_set": "<emoji document_id=5206607081334906820>✅</emoji> GitHub токен успешно установлен"
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.command(ru_doc="<токен> - Установить GitHub токен")
    async def settoken(self, message):
        """<token> - Set GitHub token"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_token"])
            return
        self.db.set("AdminFH", "github_token", args)
        await utils.answer(message, self.strings["token_set"])

    @loader.command(ru_doc="<имя> - Загрузить файл .py на GitHub (без расширения)")
    async def addmod(self, message):
        """<name> - Upload .py file to GitHub (without extension)"""
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await utils.answer(message, self.strings["no_reply"])
            return

        if not reply.file.name.endswith('.py'):
            await utils.answer(message, self.strings["invalid_extension"])
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_filename"])
            return

        file_name = args.replace('.py', '') + '.py'
        file_content = await reply.download_media(bytes)

        github_token = self.db.get("AdminFH", "github_token")
        if not github_token:
            await utils.answer(message, self.strings["no_token"])
            return

        repo_owner = "Fixyres"
        repo_name = "Modules"

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_name}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "message": f"Upload {file_name}",
            "content": base64.b64encode(file_content).decode('utf-8')
        }

        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=data) as response:
                if response.status == 201:
                    file_url = f"https://github.com/{repo_owner}/{repo_name}/blob/main/{file_name}"
                    await utils.answer(message, self.strings["upload_success"].format(file_url))
                else:
                    error_msg = await response.text()
                    await utils.answer(message, self.strings["upload_error"].format(error_msg))

    @loader.command(ru_doc="<имя> - Удалить файл .py с GitHub (без расширения)")
    async def delmod(self, message):
        """<name> - Delete .py file from GitHub (without extension)"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_filename"])
            return

        file_name = args.replace('.py', '') + '.py'

        github_token = self.db.get("AdminFH", "github_token")
        if not github_token:
            await utils.answer(message, self.strings["no_token"])
            return

        repo_owner = "Fixyres"
        repo_name = "Modules"

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_name}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    await utils.answer(message, self.strings["delete_error"].format("Файл не найден"))
                    return
                file_info = await response.json()

            data = {
                "message": f"Delete {file_name}",
                "sha": file_info["sha"]
            }

            async with session.delete(url, headers=headers, json=data) as response:
                if response.status == 200:
                    await utils.answer(message, self.strings["delete_success"].format(file_name))
                else:
                    error_msg = await response.text()
                    await utils.answer(message, self.strings["delete_error"].format(error_msg))
