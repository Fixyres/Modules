#meta developer: @xuduk
"""
██████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░██░░░░░░░░█░░░░░░██░░░░░░█░░░░░░░░░░░░███░░░░░░██░░░░░░█░░░░░░██░░░░░░░░█
█░░▄▀▄▀░░██░░▄▀▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀▄▀▄▀▄▀░░░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀▄▀░░█
█░░░░▄▀░░██░░▄▀░░░░█░░▄▀░░██░░▄▀░░█░░▄▀░░░░▄▀▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░░░█
███░░▄▀▄▀░░▄▀▄▀░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░███
███░░░░▄▀▄▀▄▀░░░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░░░░░▄▀░░███
█████░░▄▀▄▀▄▀░░█████░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░███
███░░░░▄▀▄▀▄▀░░░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░░░░░▄▀░░███
███░░▄▀▄▀░░▄▀▄▀░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░███
█░░░░▄▀░░██░░▄▀░░░░█░░▄▀░░░░░░▄▀░░█░░▄▀░░░░▄▀▄▀░░█░░▄▀░░░░░░▄▀░░█░░▄▀░░██░░▄▀░░░░█
█░░▄▀▄▀░░██░░▄▀▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀▄▀▄▀▄▀░░░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░██░░▄▀▄▀░░█
█░░░░░░░░██░░░░░░░░█░░░░░░░░░░░░░░█░░░░░░░░░░░░███░░░░░░░░░░░░░░█░░░░░░██░░░░░░░░█
██████████████████████████████████████████████████████████████████████████████████
"""
from .. import loader, utils

@loader.tds
class GoogleItForMe(loader.Module):
    """Гуглит что-то вместо тебя."""
    strings = {'name': 'Давай погуглим'}

    @loader.command(alias='г')
    async def g(self, message):
        """[запрос] - сгенерировать ссылку которая гуглит за тебя"""
        args = utils.get_args_raw(message)
        text = "<b>Давай погуглим вместе<emoji document_id=5382059733781847797>😉</emoji> \nСсылка:</b> https://googlegiksearch.github.io/?q="
        no_args = "<b>А что гуглить то<emoji document_id=5370763368497944736>😒</emoji></b>"
        if not args:
            return await message.edit(no_args)
        await message.edit(text + args.replace(" ", "+"))