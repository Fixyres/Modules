from .. import loader
import random, string
def r(l=8): return ''.join(random.choices(string.ascii_lowercase, k=l))
n = r()
@loader.tds
class M(loader.Module):
    strings = {"name": n}
    async def qjdbmfuzcmd(self, message): 
        pass
M.__name__ = n
globals()[n] = M