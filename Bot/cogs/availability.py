import logging

from discord.ext import commands
from pony.orm import db_session

from Database import Availability

LOGGER = logging.getLogger(__name__)


class AvailabilityCog(commands.Cog, name='Availability Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name='Availability',
        aliases=['Availabilities', 'Ava'],
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
        usage='<Availability|str>'
    )
    async def availability_group(self, ctx, name: str):
        with db_session:
            availability = Availability.get(name=name)
            if availability:
                LOGGER.info(f"Loading Availability List for {name}")
                result_str = '```\n' + ('\n'.join([char.name for char in availability.characters])) + '```'
                await ctx.send(f"**__Availability {name}__**{result_str}")
                await ctx.message.delete()
            else:
                LOGGER.warning(f"Unable to find Availability: {name}")
                await ctx.message.add_reaction('❎')

    @availability_group.command(
        name='List',
        pass_context=True,
        usage=''
    )
    async def tier_list(self, ctx):
        with db_session:
            results = Availability.select()[:]
            if results:
                result_str = '```\n' + ('\n'.join([availability.name for availability in sorted(results, key=lambda x: x.name)])) + '```'
                await ctx.send(f"**__Availability List__**{result_str}")
                await ctx.message.delete()
            else:
                LOGGER.warning(f"Unable to find any Availabilities")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @availability_group.command(
        name='Create',
        pass_context=True,
        usage='<Name|str> <Colour Code|str=000000>',
        hidden=True
    )
    async def create_availability(self, ctx, name: str, colour_code: str = '000000'):
        with db_session:
            Availability.safe_insert(name, colour_code)
            await ctx.message.add_reaction('✅')

    @commands.has_role('Editor')
    @availability_group.command(
        name='Edit',
        pass_context=True,
        usage='<Name|str> <Colour Code|str=000000>',
        hidden=True
    )
    async def edit_availability(self, ctx, name: str, colour_code: str = '000000'):
        with db_session:
            availability = Availability.get(name=name)
            if availability:
                availability.colour_code = colour_code
                await ctx.message.add_reaction('✅')
            else:
                LOGGER.warning(f"Unable to find Availability: {name}")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @availability_group.command(
        name='Delete',
        pass_context=True,
        usage='<Name|str>',
        hidden=True
    )
    async def delete_availability(self, ctx, name: str):
        with db_session:
            availability = Availability.get(name=name)
            if availability:
                availability.delete()
                await ctx.message.add_reaction('✅')
            else:
                LOGGER.warning(f"Unable to find Availability: {name}")
                await ctx.message.add_reaction('❎')


def setup(bot):
    bot.add_cog(AvailabilityCog(bot))
