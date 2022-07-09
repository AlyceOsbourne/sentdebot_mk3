import nextcord
from nextcord.ext import commands


class MiscCogs(commands.Cog, name="Misc Cogs"):
    """Cog that holds random commands"""
    def __init__(self, bot):
        self.bot = bot
        # delete the help command
        self.bot.remove_command('help')

    @commands.command(name="membercount", help="Get the member count of a guild")
    async def membercount(self, ctx):
        await ctx.send(f"{ctx.guild.member_count}")

    @commands.command(name="commands", aliases=["help"], help="Get all registered commands")
    async def commands(self, ctx):
        c = []
        for command in self.bot.commands:
            c.append((command.name, command.help))
        c.sort(key=lambda x: x[0])
        # format like python dict return
        await ctx.send("return {\n\t" + ",\n\t".join(f"{k}: {v}" for k, v in c) + "\n}")




def setup(bot):
    bot.add_cog(MiscCogs(bot))
