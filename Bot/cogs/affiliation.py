import logging

from discord.ext import commands
from pony.orm import db_session, raw_sql, select

from Database import Affiliation, Character

LOGGER = logging.getLogger(__name__)


class AffiliationCog(commands.Cog, name='Affiliation Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name='Affiliation',
        aliases=['Affiliations'],
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
        usage='<Name|str>'
    )
    async def affiliation_group(self, ctx, name: str):
        with db_session:
            results = Affiliation.select(lambda x: name in x.name)[:]
            if results:
                for _affiliation in results:
                    result_str = '\n'.join([x.name for x in sorted(_affiliation.characters)])
                    await ctx.send(f"**{_affiliation.name} Characters**```\n{result_str}```")
            else:
                LOGGER.warning(f"Unable to find any Characters with Affiliation: {name}")
                await ctx.message.add_reaction('❎')

    @affiliation_group.command(
        name='List',
        pass_context=True,
        usage=''
    )
    async def list_affiliations(self, ctx):
        with db_session:
            await ctx.send('**Affiliations:** ' + (', '.join([x.name for x in Affiliation.select()[:]])))


def setup(bot):
    bot.add_cog(AffiliationCog(bot))
