# meta developer: @azotikfantazysbop

from .. import loader, utils

import random
from contextlib import suppress
from telethon.tl.types import Message, MessageMediaPhoto


bullr = [
    "<emoji document_id=5458550322479771836>❤️</emoji> Слыш я твою маму трахал","Я ТВОЮ МАТЬ ПОНИМАЕШ ЧИСТО ХУЕМ УБИВАЛ","<emoji document_id=5458550322479771836>❤️</emoji> Я ТВОЕЙ МАТЕРИ ПИЗДАК ЧИСТА ВЕШАЛ К ХУЮ СВОЕМУ И НА ЗАНОВСКИ ЕЕ НОГИ ЗАХУЯРИЛ","ОТСОСИ МОЙ ХУЙ","с хуя чо?","<emoji document_id=5458550322479771836>❤️</emoji>ну это понятно что ты ебаной кашолки решил мне остосиврувать членовой акригативный член ну так что же ты решил просто пригнуть на негго ало сын ебаноц дегенератки я тебе мать выебал ну ты мне решил врил чета сдклать когда я тебе чисто в ебало даю ну так ало ты сын ебаного дегенерата я тебе мать ебал на сколько глубоко когда же ты пидер не могла мне понять что я тебе в ебало кончил так что же ты пидер нефрибидируваный решил мне сделать? я тебе чисто в ебало давал хуем как шлюхе так что же ты пидер мне делаешь минет? так что же ты дегенерат мне решил отсосирувать? ало сын ебаной блядоты я тебе смать ебал ну ты мне реши чета отсоаать я тебе уже не раз говорил что ты мне будешь дальше делать мрнет так что же ты регил мне делать ало сын ебаной фермерки ты не что не могла мне делать когда я тебе кости просто на кд ломаю так что же ты пидер мне делаешь минте  тебе мать ебал чисто на приколе когда же ты пидер не понимал что тебе пизда чисто так что дальше", " папе чо?", "с хуя соври","тя ебал","а ну высоси член","че папе? мы все под твоим ником", "высосе слыш","мы те таранткла в очко засунем, проверим как он задохнется от твоего дерьма","слыш, когда я тя ебал, у тебя был передоз?","ТЫ ЖЕ ПОНИМАЕШЬ ТВОЯ МАМАША КАК ПРОПЕЛЕР РАСКРУТИЛАСЬ С ОКНА В РАЗБИТОЕ СТЕКЛО К ХУЯМ","соври","соси","тя ебу","хуек пасаси","ну мы чиста твою маму трахали","анука не терпи хуй мой","в честь сталина мы тя расстреляли нахуй, после вырезали твою мамку","ну ка завоеватель ты 9 членов сасай хуй мой", "тя трахал", "деду чо?", " а папе чо с хуя? ври в дик","ты слабая абезянка","в дик скажи","отсоси пенес ты праститутка","засаси мою сперму", "чо бабке после минета?","все я ты","тя ебу пидрила"
 ]


@loader.tds
class FuckerMod(loader.Module):
    strings = {
        "name": "Унижатор Premium"
    }
    
    async def client_ready(self, client, db):
        self.db = db
        self.users = self.db.get("fucker", "users", [])
        self.phrases = self.db.get("fucker", "phrases", [])
    
    def add_phrase(self, phrase: str):
        self.phrases.append(phrase)
        self.db.set("fucker", "phrases", self.phrases)
    
    def add_user(self, user_id: int):
        self.users.append(user_id)
        self.db.set("fucker", "users", self.users)
    
    def remove_user(self, user_id: int):
        self.users.remove(user_id)
        self.db.set("fucker", "users", self.users)
    
    async def clearbcmd(self, message):
        """Никого не трахать"""
        
        self.users = []
        self.db.set("fucker", "users", self.users)
        
        await utils.answer(
            message=message,
            response="<b>Больше я никого не унижаю</b>"
        )
    
    async def baddcmd(self, message):
        """Добавить фразу | .bulla <фраза>"""
        
        args = utils.get_args_raw(message)
        
        if not args:
            return await utils.answer(
                message=message,
                response="<b>🚫 Не указан аргумент</b>"
            )
        
        self.add_phrase(args)
        
        await utils.answer(
            message=message,
            response="<b>Фраза добавлена</b>"
        )
    
    async def bullrcmd(self, message):
        """Вкинуть рандомное оскорбление"""
        
        await utils.answer(
            message=message,
            response=random.choice(bullr + self.phrases)
        )
    
    async def addbcmd(self, message):
        """Буллить чела. <reply>"""
        
        reply = await message.get_reply_message()
        
        if reply is not None:
            if reply.from_id is not None:
                await utils.answer(
                    message=message,
                    response="☠️<emoji document_id=5458550322479771836>❤️</emoji> ну ты сасал"
                )

                self.add_user(reply.from_id)
            
            else:
                await utils.answer(
                    message=message,
                    response="<b>🚫 Модуль не работает на анонимных администраторах или каналах</b>"
                )

        else:
            await utils.answer(
                message=message,
                response="<b>🚫 Нужен реплай сообщения</b>"
            )
    
    async def removebcmd(self, message):
        """Не буллить спермасоса. <reply>"""
        
        reply = await message.get_reply_message()
        
        if reply is not None:
            await utils.answer(
                message=message,
                response="<b><emoji document_id=5458550322479771836>❤️</emoji> сасай</b>"
            )
            
            try:
                self.remove_user(reply.from_id)
            except:
                await utils.answer(
                    message=message,
                    response="<b>💀 Я и так не ебу того сперманоса</b>"
                )

        else:
            await utils.answer(
                message=message,
                response="<b>🚫 Нужен реплай на соо</b>"
            )
    
    async def watcher(self, message):
        if getattr(message, "from_id", None) in self.users:
            await message.reply(random.choice(bullr + self.phrases))