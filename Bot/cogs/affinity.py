import logging

from discord.ext import commands
from pony.orm import db_session, raw_sql, select

from Database import Affinity, Character

LOGGER = logging.getLogger(__name__)


class AffinityCog(commands.Cog, name='Affinity Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name='Affinity',
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
        usage='<Name|str>'
    )
    async def affinity_group(self, ctx, name: str):
        with db_session:
            _affinity = Affinity.find(name)
            results = select(x for x in Character if raw_sql(f'x.affinity == "{_affinity}"'))[:]
            if results:
                result_str = '\n'.join([f"{x.name}: {x.title}" for x in sorted(results)])
                await ctx.send(f"**{_affinity} Characters**```\n{result_str}```")
            else:
                LOGGER.warning(f"Unable to find any Characters with Affinity: {_affinity}")
                await ctx.message.add_reaction('❎')

    @affinity_group.command(
        name='List',
        pass_context=True,
        usage=''
    )
    async def list_affinities(self, ctx):
        with db_session:
            await ctx.send('**Affinities:** ' + (', '.join([x.__str__().title() for x in Affinity.__members__])))


def setup(bot):
    bot.add_cog(AffinityCog(bot))
