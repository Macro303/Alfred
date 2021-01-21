import logging
from typing import List

from discord import Embed
from discord.ext import commands
from discord.ext.commands.core import Group

from Bot import CONFIG

LOGGER = logging.getLogger(__name__)


def parse_commands(comm_list, output: List[str], add_hidden: bool, parent_name: str = '') -> List[str]:
    for comm in sorted(comm_list, key=lambda x: (isinstance(x, Group), x.name)):
        usage = f"{CONFIG['Prefix']}{parent_name}{comm.name} {comm.usage}".strip()
        if isinstance(comm, Group):
            output.append(f"__{parent_name}{comm.name}__")
            if comm.aliases:
                names = [comm.name, *comm.aliases]
                names_str = f", {parent_name}".join(names)
                output.append(f"Aliases: {parent_name}{names_str}")
            if comm.usage is not None and (add_hidden or not comm.hidden):
                output.append(f" - `{usage}`")
            output = parse_commands(comm.commands, output, add_hidden, f"{parent_name}{comm.name} ")
        else:
            if comm.usage is not None and (add_hidden or not comm.hidden):
                output.append(f" - `{usage}`")

    return output


class OtherCog(commands.Cog, name='Other Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='Help',
        description='The help command',
        usage=''
    )
    async def help_command(self, ctx):
        embed = Embed(
            title='Alfred Commands'
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        for cog in sorted([c for c in self.bot.cogs.keys()]):
            if cog == 'Other Commands':
                continue
            comm_list = parse_commands(self.bot.get_cog(cog).get_commands(), [],
                                       'Editor' in [x.name for x in ctx.author.roles])
            if comm_list:
                embed.add_field(name=cog, value='\n'.join(comm_list), inline=False)

        comm_list = parse_commands(self.bot.get_cog('Other Commands').get_commands(), [],
                                   'Editor' in [x.name for x in ctx.author.roles])
        if comm_list:
            embed.add_field(name='Other Commands', value='\n'.join(comm_list), inline=False)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(OtherCog(bot))
