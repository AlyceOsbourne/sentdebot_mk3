import random

import nextcord
from nextcord.ext import commands

VANITY_ROLES_NAMES = []

class MiscCogs(commands.Cog, name="Misc Cogs"):
    """Cog that holds random commands"""
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command(name="membercount", help="Get the member count of a guild")
    async def membercount(self, ctx):
        await ctx.send(f"{ctx.guild.member_count}")

    @commands.command(name="commands", aliases=["help"], help="Get all registered commands")
    async def commands(self, ctx):
        await ctx.send("return {\n\t" + ",\n\t".join(f"{k}: {v}" for k, v in sorted(
            [(command.name, command.help) for command in self.bot.commands], key=lambda x: x[0])) + "\n}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 705898465909879552:
            if member.joined_at.timestamp() > 1577836800:
                if random.randint(1, 100) <= 10:
                    # random, choice from role names list
                    role_selection = random.choice(VANITY_ROLES_NAMES)
                    role = nextcord.utils.get(member.guild.roles, name=role_selection)
                    await member.add_roles(role)



def setup(bot):
    bot.add_cog(MiscCogs(bot))
