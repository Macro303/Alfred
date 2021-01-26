import logging

from discord.ext import commands
from pony.orm import db_session, raw_sql, select

from Database import Tier, Character

LOGGER = logging.getLogger(__name__)


class TierCog(commands.Cog, name='Tier Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name='Tier',
        aliases=['Tiers'],
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
        usage='<Name|str>'
    )
    async def tier_group(self, ctx, name: str):
        with db_session:
            _tier = Tier.find(name)
            results = select(x for x in Character if raw_sql(f'x.tier == "{_tier}"'))[:]
            if results:
                result_str = '\n'.join([x.name for x in sorted(results)])
                await ctx.send(f"**Tier {_tier} Characters**```\n{result_str}```")
            else:
                LOGGER.warning(f"Unable to find any Characters with Tier: {_tier}")
                await ctx.message.add_reaction('❎')

    @tier_group.command(
        name='List',
        pass_context=True,
        usage=''
    )
    async def list_tiers(self, ctx):
        with db_session:
            await ctx.send('**Tiers:** ' + (', '.join([x.__str__().title() for x in Tier.__members__])))


def setup(bot):
    bot.add_cog(TierCog(bot))
