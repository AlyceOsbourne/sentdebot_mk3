from nextcord.ext import commands


class MiscCogs(commands.Cog, name="Misc Cogs"):
    """Cog that holds random commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="membercount", help="Get the member count of a guild")
    async def membercount(self, ctx):
        await ctx.send(f"{ctx.guild.member_count}")

    @commands.command(name="commands", help="Get all registered commands")
    async def commands(self, ctx):
        c = []
        for command in self.bot.commands:
            if not command.hidden:
                c.append(command.name)
        await ctx.send("return {" + ", ".join(f'"{command}": {command.help}' for command in c) + "}")


def setup(bot):
    bot.add_cog(MiscCogs(bot))
