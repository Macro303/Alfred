import logging

from discord.ext import commands
from pony.orm import db_session

from Database import Tier

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
        usage='<Tier|str>'
    )
    async def tier_group(self, ctx, name: str):
        with db_session:
            result = Tier.get(name=name)
            if result:
                LOGGER.info(f"Loading Tier List for {name}")
                result_str = '```\n' + ('\n'.join([char.name for char in result.characters])) + '```'
                await ctx.send(f"**__Tier {name}__**{result_str}")
                await ctx.message.delete()
            else:
                LOGGER.warning(f"Unable to find Tier: {name}")
                await ctx.message.add_reaction('❎')

    @tier_group.command(
        name='List',
        pass_context=True,
        usage=''
    )
    async def tier_list(self, ctx):
        with db_session:
            results = Tier.select()[:]
            if results:
                result_str = '```\n' + ('\n'.join([tier.name for tier in sorted(results, key=lambda x: x.index)])) + '```'
                await ctx.send(f"**__Tier List__**{result_str}")
                await ctx.message.delete()
            else:
                LOGGER.warning(f"Unable to find any Tiers")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @tier_group.command(
        name='Create',
        pass_context=True,
        usage='<Index|Int> <Name|str>',
        hidden=True
    )
    async def create_tier(self, ctx, index: int, name: str):
        with db_session:
            Tier.safe_insert(index, name)
            await ctx.message.add_reaction('✅')

    @commands.has_role('Editor')
    @tier_group.command(
        name='Edit',
        pass_context=True,
        usage='<Index|Int> <Name|str>',
        hidden=True
    )
    async def edit_tier(self, ctx, index: int, name: str):
        with db_session:
            tier = Tier.get(index=index)
            if tier:
                tier.name = name
                await ctx.message.add_reaction('✅')
            else:
                LOGGER.warning(f"Unable to find Tier: {name}")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @tier_group.command(
        name='Delete',
        pass_context=True,
        usage='<Index|Int>',
        hidden=True
    )
    async def delete_tier(self, ctx, index: int):
        with db_session:
            tier = Tier.get(index=index)
            if tier:
                tier.delete
                await ctx.message.add_reaction('✅')
            else:
                LOGGER.warning(f"Unable to find Tier: {index}")
                await ctx.message.add_reaction('❎')


def setup(bot):
    bot.add_cog(TierCog(bot))
