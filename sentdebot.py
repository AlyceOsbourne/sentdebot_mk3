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
            for channel in guild.text_channels:
                await channel.send(f"Sentdebot {bot_version} is ready!")


if __name__ == "__main__":
    bot = Sentdebot()
    bot.run()
