#Developer: @ThisColor

import asyncio
import logging
from telethon import functions, types
from telethon.tl.types import Message
from .. import loader, utils
from collections import defaultdict

users_info = defaultdict(dict)

logger = logging.getLogger(__name__)

class CheckBunkerMod(loader.Module):
    """
    CheckBunker for @bfgbunker_bot
    """

    strings = {"name": "CheckBunker"}

    _bot = "@bfgbunker_bot"
    
    async def Infacmd(self, message: Message):
        """(nick or user_id) check bunker player"""
        args = utils.get_args(message)
        identifier = args[0]

        user_id = None
        if identifier.isdigit():  
            user_id = identifier
        else:  
            for uid, user_info in users_info.items():
                if user_info.get("nick").lower() == identifier.lower():                 
                    user_id = uid

        if user_id is not None:
            async with self._client.conversation(self._bot) as conv:
                await conv.send_message(f"Узнать о {user_id}")
                response = await conv.get_response()

                info_text = response.raw_text
                nick_start = info_text.find("🙎‍♂️")
                nick_end = info_text.find("\n", nick_start)  
                nick = info_text[nick_start+4:nick_end].strip()  
                bottles_text = info_text.split("Бутылок:")[1].split()[0].strip()
                bottles = int("".join(filter(str.isdigit, bottles_text)))
                bottles = "{:,}".format(int(bottles)).replace(",", ".")
                money_parts = info_text.split("Баланс:")[1].split()[0].strip().split('/')
                formatted_money = f"{money_parts[0]}/{money_parts[1]}"
                people = int("".join(filter(str.isdigit, info_text.split("Людей в бункере:")[1].split('\n')[0].strip())))
                people_in_line = int("".join(filter(str.isdigit, info_text.split("Людей в очереди в бункер:")[1].split('/')[0].strip())))
                max_people = int("".join(filter(str.isdigit, info_text.split("Макс. вместимость людей:")[1].split()[0].strip())))
                profit_start = info_text.find("💵")
                profit_end = info_text.find("\n", profit_start)  
                profit = info_text[profit_start+1:profit_end].strip()  

                formatted_info = f'''🙎‍♂️ {nick}\n\n🍾 <b>Бутылок:</b> {bottles}\n💰 <b>Крышек:</b> {formatted_money} кр.\n\n🧍 <b>Людей в бункере:</b> {people}\n     ↳<b>Людей в очереди:</b> {people_in_line}\n\n<code>Макс. человек: </code>{max_people}\n\n💵 <b>{profit}</b> '''

                await message.respond(formatted_info)              
        else:
            await message.respond(f"player with <u>{identifier}</u> nickname or ID not found")        


    async def addcmd(self, message: Message):
        """(id) (nick) add nick player"""
        args = utils.get_args(message)

        if len(args) < 2:
            await message.edit(" use: .add [id] [nick]")
            return

        user_id = args[0]
        nick = args[1] 
               
        users_info[user_id] = {"nick": nick, "id": user_id}
        await self._client.send_message(self._CheckerBunker_channel, f"Добавлен новый игрок {user_id} {nick} ")
        await message.respond(f"nickname <u>{nick}</u> for player {user_id} added")
        
    async def listcmd(self, message: Message):
        """show all players (id:nick)"""
        player_list = "\n".join([f"{uid}: {user_info['nick']}" for uid, user_info in users_info.items()])
        await message.respond(f"list of players:\n{player_list}")

    async def delecmd(self, message: Message):
        """(nick) remove player by nickname"""
        args = utils.get_args(message)
    
        if len(args) < 1:
            await message.edit(" use: .del [nick]")
            return

        nick = args[0]
        user_id = None
        for uid, user_info in users_info.items():
            if user_info.get("nick").lower() == nick.lower():
                user_id = uid
                break

        if user_id is not None:
            del users_info[user_id]
            await self._client.send_message(self._CheckerBunker_channel, f"Игрок с ником {nick} был удален")
            await message.respond(f"player with nickname <u>{nick}</u> deleted")
        else:
            await message.respond(f"player with nickname <u>{nick}</u> not found")
        

    async def read_checker_bunker_chat(self):
        async for message in self._client.iter_messages(self._CheckerBunker_channel, limit=None):
            if "новый игрок" in message.text:
                parts = message.text.split(" ")
                if len(parts) >= 4:
                    user_id = parts[3]
                    nick = " ".join(parts[4:])
                    users_info[user_id] = {"nick": nick, "id": user_id}
            elif "игрок удален" in message.text:
                nick = message.text.split("ником")[-1].strip()
                for uid, user_info in users_info.items():
                    if user_info.get("nick").lower() == nick.lower():
                        del users_info[uid]

    async def client_ready(self):
        self._CheckerBunker_channel, _ = await utils.asset_channel(
            self._client,
            "CheckerBunker - чат",
            "этот чат предназначен для модуля CheckerBunker от @ThisColor",
            silent=True,
            archive=True,
            _folder="hikka",
        )

        asyncio.create_task(self.read_checker_bunker_chat())