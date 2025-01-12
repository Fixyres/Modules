# meta banner: https://raw.githubusercontent.com/Fixyres/Modules/refs/heads/main/IMG_20250112_185329_901.jpg
# meta developer: @Foxy437 & venom

from .. import loader, utils

@loader.tds
class venomMod(loader.Module):
    """venom"""

    strings = {
        "name": "venom"
    }

    async def venomcmd(self, m):
        """venom"""
        await utils.asyncio.sleep(1)
        self.db.set("venom", "on", not self.db.get("venom", "on", False))
        if self.db.get("venom", "on", False):
            await m.edit("venom")

    async def watcher(self, m):
        if self.db.get("venom", "on", False) and m.out:
            await m.edit("venom")
