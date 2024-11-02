from .. import loader, utils
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError, ImageProcessFailedError
import io

#meta developer: Ksenon | @justksenon

@loader.tds
class CopyUserModule(loader.Module):
    """🖼️ Копирует аватарку и информацию указанного пользователя на ваш аккаунт"""

    strings = {"name": "CopyUser-Ksenon"}

    @loader.command()
    async def copyuser(self, message):
        """🖼️ Скопировать пользователя. Использование: .copy <username>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "👉 Укажите username пользователя!")
            return

        try:
            user = await message.client.get_entity(args)
            full_user = await message.client(GetFullUserRequest(user.id))
            
            # Копируем аватарку
            if full_user.full_user.profile_photo:
                try:
                    avatar = await message.client.download_profile_photo(user, bytes)
                    if avatar:
                        # Удаляем текущие аватарки
                        photos = await message.client.get_profile_photos('me')
                        await message.client(DeletePhotosRequest(photos))
                        
                        # Загружаем новую аватарку
                        await message.client(UploadProfilePhotoRequest(
                            file=await message.client.upload_file(io.BytesIO(avatar))
                        ))
                        await utils.answer(message, "✅ Аватарка была обновлена.")
                    else:
                        await utils.answer(message, "⚠️ Не удалось загрузить аватарку пользователя.")
                except ImageProcessFailedError:
                    await utils.answer(message, "⚠️ Не удалось обработать изображение аватарки.")
            else:
                await utils.answer(message, "ℹ️ У пользователя нет аватарки.")
            
            # Копируем информацию профиля
            await message.client(UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                about=full_user.full_user.about or ""
            ))
            
            await utils.answer(message, "✅ Пользователь скопирован!")
        except UsernameNotOccupiedError:
            await utils.answer(message, "❌ Пользователь с таким username не существует!")
        except UsernameInvalidError:
            await utils.answer(message, "❌ Неверный формат username!")
        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")