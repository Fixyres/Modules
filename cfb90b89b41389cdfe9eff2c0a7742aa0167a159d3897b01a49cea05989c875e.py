"""

░█░█░█▀▀░█▀█░█▀▀░▀█▀░█▀▄░█▀▀
░▄▀▄░█▀▀░█░█░▀▀█░░█░░█░█░█▀▀
░▀░▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀░░▀▀▀
 🔒 Licensed under the AGPL-3.0
 🌐 https://www.gnu.org/licenses/agpl-3.0.html"""
 
# meta developer: @XenSideMOD
from .. import loader, utils
from telethon.tl.types import Message

@loader.tds
class VirtualKeyboardMod(loader.Module):
    strings = {
        "name": "VirtualKeyboard",
        "keyboard_title": "Виртуальная клавиатура",
        "message_placeholder": "Введите текст...",
    }
    
    def __init__(self):
        self.current_text = {}
    
    @loader.command(ru_doc=".keyb - Показать виртуальную клавиатуру ГАЙД: @XENSIDEMOD")
    async def keyb(self, message: Message):
        chat_id = str(message.chat_id)
        if chat_id not in self.current_text:
            self.current_text[chat_id] = ""
        
        await self.inline.form(
            text=self.strings["message_placeholder"],
            message=message,
            reply_markup=self.generate_keyboard(chat_id),
        )
    
    def generate_keyboard(self, chat_id):
        rows = []
        letters = [
            ['й', 'ц', 'у', 'к', 'е', 'н', 'г'],
            ['ш', 'щ', 'з', 'х', 'ъ', 'ф', 'ы'],
            ['в', 'а', 'п', 'р', 'о', 'л', 'д'],
            ['ж', 'э', 'я', 'ч', 'с', 'м', 'и'],
            ['т', 'ь', 'б', 'ю']
        ]
        
        for row in letters:
            btn_row = [
                {
                    "text": letter.upper(),
                    "callback": self.add_letter,
                    "args": (letter, chat_id),
                } for letter in row
            ]
            rows.append(btn_row)
        
        bottom_row = [
            {
                "text": "⌫",
                "callback": self.delete_last_char,
                "args": (chat_id,),
            },
            {
                "text": "Пробел",
                "callback": self.add_space,
                "args": (chat_id,),
            },
            {
                "text": "Отправить ✅",
                "callback": self.send_message,
                "args": (chat_id,),
            },
        ]
        rows.append(bottom_row)
        return rows
    
    async def add_letter(self, call, letter: str, chat_id: str):
        self.current_text[chat_id] += letter
        await call.edit(
            text=self.current_text[chat_id] or self.strings["message_placeholder"],
            reply_markup=self.generate_keyboard(chat_id),
        )
    
    async def add_space(self, call, chat_id: str):
        self.current_text[chat_id] += " "
        await call.edit(
            text=self.current_text[chat_id] or self.strings["message_placeholder"],
            reply_markup=self.generate_keyboard(chat_id),
        )
    
    async def delete_last_char(self, call, chat_id: str):
        if self.current_text[chat_id]:
            self.current_text[chat_id] = self.current_text[chat_id][:-1]
        await call.edit(
            text=self.current_text[chat_id] or self.strings["message_placeholder"],
            reply_markup=self.generate_keyboard(chat_id),
        )
    
    async def send_message(self, call, chat_id: str):
        text = self.current_text.get(chat_id, "")
        if text:
            await self._client.send_message(int(chat_id), text)
            del self.current_text[chat_id]
            await call.delete()
        else:
            await call.answer("Сообщение пустое!", show_alert=True)
