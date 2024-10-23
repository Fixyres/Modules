from .. import loader, utils
from datetime import datetime

@loader.tds
class DateInfo(loader.Module):
    """Модуль для получения информации о дате"""
    strings = {'name': 'DateInfo'}
    
    birthdays = {}

    @loader.command()
    async def bd(self, message):
        """[день] [месяц] - установить свой день рождения"""
        args = message.text.split()
        
        if len(args) != 3:
            await message.edit("📛 <b>Error</b> | <code>.bd</code>\n<b>Не верный формат (день и месяц должны быть числом, пример: 1 1)</b>")
            return

        try:
            day = int(args[1])
            month = int(args[2])
            
            if month < 1 or month > 12 or day < 1 or day > 31:
                await message.edit("📛 <b>Error</b> | <code>.bd</code>\n<b>Не верный формат</b>")
                return

            self.birthdays[message.sender_id] = (day, month)

            await message.edit(f"✅ <b>Beautiful</b> | <code>.bd</code>\n<b>Ваш день рождения {day} {month} успешно сохранен</b>")
        except ValueError:
            await message.edit("📛 <b>Error</b> | <code>.bd</code>\n<b>Не верный формат</b>")

    @loader.command()
    async def di(self, message):
        """- показать информацию о сегодня"""
        now = datetime.now()
        
        months = [
            "Январь", "Февраль", "Март", "Апрель",
            "Май", "Июнь", "Июль", "Август",
            "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

        seasons = [
            "Зима", "Зима", "Весна", "Весна",
            "Весна", "Лето", "Лето", "Лето",
            "Осень", "Осень", "Осень", "Зима"
        ]

        emojis = {
            "Зима": ("☃️", "❄️"),
            "Весна": ("🌹", "🌾"),
            "Лето": ("🍃", "🪴"),
            "Осень": ("🍂", "🍁")
        }

        holidays = {
            (1, 1): "❄️ Новый год",
            (2, 23): "🇷🇺 День защитника Отечества",
            (3, 8): "🌸 Международный женский день",
            (5, 1): "🛠 Праздник весны и труда",
            (5, 9): "🫡 День Победы",
            (6, 1): "🥵 День защиты детей",
            (6, 12): "🎉 День России",
            (9, 1): "📚 День знаний",
            (11, 4): "🇷🇺 День народного единства",
            (2, 14): "🩷 День влюбленных",
            (12, 31): "🎉 Новый год по старому стилю"
        }

        current_year = now.year
        next_month_index = now.month 
        current_day = now.day
        current_weekday = now.strftime("%A")

        weekdays_ru = {
            "Monday": "Понедельник",
            "Tuesday": "Вторник",
            "Wednesday": "Среда",
            "Thursday": "Четверг",
            "Friday": "Пятница",
            "Saturday": "Суббота",
            "Sunday": "Воскресенье"
        }

        current_weekday_ru = weekdays_ru[current_weekday]
        weekend_days = ["Суббота", "Воскресенье"]
        day_emoji = "❕" if current_weekday_ru in weekend_days else "❗️"

        days_in_month = (datetime(current_year, (next_month_index % 12) + 1, 1) - datetime(current_year, next_month_index, 1)).days
        days_remaining = days_in_month - current_day
        last_day_of_year = datetime(current_year, 12, 31)
        days_until_end_of_year = (last_day_of_year - now).days

        holiday = holidays.get((now.month, now.day), None)
        holiday_message = f"🎉<b>{holiday}!</b>" if holiday else "😭 <b>Сегодня праздник не отмечается</b>"
        is_leap_year = (current_year % 4 == 0 and current_year % 100 != 0) or (current_year % 400 == 0)

        next_leap_year = current_year + 1
        while not ((next_leap_year % 4 == 0 and next_leap_year % 100 != 0) or (next_leap_year % 400 == 0)):
            next_leap_year += 1
        days_until_next_leap_year = (datetime(next_leap_year, 2, 29) - now).days if not is_leap_year else 0

        birthday_message = ""
        if message.sender_id in self.birthdays:
            bd_day, bd_month = self.birthdays[message.sender_id]
            if bd_day == current_day and bd_month == next_month_index:
                birthday_message = f"🎂 <b>Сегодня ваш день рождения!</b>"
            else:
                next_birthday_year = current_year if (bd_month > next_month_index or (bd_month == next_month_index and bd_day > current_day)) else current_year + 1
                next_birthday_date = datetime(next_birthday_year, bd_month, bd_day)
                days_until_birthday = (next_birthday_date - now).days
                birthday_message = f"🎉 <b>До вашего дня рождения осталось {days_until_birthday} дней</b>"

        current_season = seasons[next_month_index - 1]
        current_emojis = emojis[current_season]

        response = (
            f"{current_emojis[0]} <b>Сейчас:</b> <code>{months[next_month_index - 1]} ({next_month_index})</code>\n"
            f"{current_emojis[1]} <b>Время года</b>: <code>{current_season}</code>\n\n"
            f"{day_emoji} <b>Число:</b> <code>{current_day}</code>\n"
            f"📅 <b>Год:</b> <code>{current_year}</code>\n"
            f"💬 <b>День недели:</b> <code>{current_weekday_ru}</code>\n"
            f"{holiday_message}\n"
            f"{birthday_message}\n\n"
            f"💤 <b>Всего дней в месяце:</b> <code>{days_in_month}</code>\n"
            f"✅ <b>До конца месяца осталось <code>{days_remaining}</code> дней</b>\n"
            f"📆 <b>До конца года осталось <code>{days_until_end_of_year}</code> дней</b>\n"
            f"🔄 <b>Это {'високосный' if is_leap_year else 'не высокого'} год</b>\n"
            f"⏳ <b>До следующего високосного года осталось:</b> <code>{days_until_next_leap_year}</code> дней\n"
            f"➡️ <b>Следующий месяц</b>: <code>{months[next_month_index % 12]}</code>"
        )
        
        await message.respond(response)
        await message.delete()
        
    @loader.command()
    async def mi(self, message):
        """- показать все месяца по индексам"""
        await utils.answer(message, "🕡 <b>Считаю..</b>")
        monts_indeks = """🌜 <b>Месяца по индексам</b>
🌨️ <b>Январь:</b> <code>1</code>
🏔️ <b>Февраль:</b> <code>2</code>
🌥️ <b>Март:</b> <code>3</code>
🌸 <b>Апрель:</b> <code>4</code>
🌹 <b>Май:</b> <code>5</code>
🌡️ <b>Июнь:</b> <code>6</code>
🔥 <b>Июль:</b> <code>7</code>
🥀 <b>Август:</b> <code>8</code>
🌦️ <b>Сентябрь:</b> <code>9</code>
🍂 <b>Октябрь:</b> <code>10</code>
🍁 <b>Ноябрь:</b> <code>11</code>
🌨️ <b>Декабрь:</b> <code>12</code>"""
        await utils.answer(message, monts_indeks)