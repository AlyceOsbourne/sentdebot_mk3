import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
__version__ = 0, 0, 0, 1

bot_version = f"v{'.'.join(map(str, __version__))}"


class Sentdebot(commands.Bot):
    def __init__(self, **options):
        super().__init__(**options)
        self.token = os.environ.get('TOKEN')

    def run(self):
        super().run(self.token, reconnect=True)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.guilds:
            await guild.system_channel.send(f'Sentdebot {bot_version} is online!')

    @commands.command(name='hi', help='reply hi to a user who says hi')
    async def hi(self, ctx):
        # if user is self, don't reply
        if ctx.author == self.user:
            return
        await ctx.send(f'hi {ctx.author.mention}')


if __name__ == "__main__":
    bot = Sentdebot()
    bot.run()
