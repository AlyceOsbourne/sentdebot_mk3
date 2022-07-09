import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
__version__ = 0, 0, 0, 1

bot_version = f"v{'.'.join(map(str, __version__))}"


class Sentdebot(commands.Bot):
    def __init__(self, **options):
        super().__init__(command_prefix="sentdebot.", strip_after_prefix=True, **options)
        self.token = os.environ.get('TOKEN')

    def run(self):
        if not os.path.exists('cogs'):
            os.makedirs('cogs')
        for file in os.listdir('cogs'):
            if file.startswith('cog_'):
                try:
                    if os.path.isdir(os.path.join('cogs', file)):
                        for init_file in os.listdir(os.path.join('cogs', file)):
                            if init_file.startswith('__init__'):
                                self.load_extension(f'cogs.{file}.{init_file[:-3]}')
                    elif file.endswith('.py'):
                        self.load_extension(f'cogs.{file[:-3]}')
                except Exception as e:
                    print(f'Error loading cog: {e}')
                    continue
        super().run(self.token, reconnect=True)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.guilds:
            await guild.system_channel.send(f'Sentdebot {bot_version} is online!')
            # make an embed witha list of loaded cogs
            embed = nextcord.Embed(title='Loaded cogs', color=0x00ff00)
            for cog in self.cogs:
                embed.add_field(name=cog, value=self.get_cog(cog).__doc__)
            await guild.system_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return




if __name__ == "__main__":
    bot = Sentdebot()
    bot.run()
