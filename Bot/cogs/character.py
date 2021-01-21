import logging
from typing import Optional

from discord import Embed
from discord.ext import commands
from discord.member import Member
from pony.orm import db_session

from Bot import load_colour
from Database import Tier, Availability, Character

LOGGER = logging.getLogger(__name__)


def generate_embed(character: Character, author: Member) -> Embed:
    embed = Embed(title=character.name, colour=load_colour(character.availability.colour_code if character.availability else '000000'))

    embed.add_field(name="Availability", value=character.availability.name if character.availability else 'None')
    embed.add_field(name="Tier", value=character.tier.name if character.tier else 'None')

    embed.set_thumbnail(url=character.image_url)
    embed.set_footer(
        text=f"Requested by {author.name}",
        icon_url=author.avatar_url
    )
    return embed


class CharacterCog(commands.Cog, name='Character Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name='Character',
        aliases=['Char'],
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
        usage='<Name|str>'
    )
    async def character_group(self, ctx, name: str):
        with db_session:
            results = Character.select(lambda x: name in x.name)[:]
            if results:
                for character in sorted(results, key=lambda x: x.name):
                    await ctx.send(embed=generate_embed(character, ctx.author))
                await ctx.message.delete()
            else:
                LOGGER.warning(f"Unable to find Character: {name}")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @character_group.command(
        name='Create',
        pass_context=True,
        usage='<Name|str> <Tier|str> <Availability|str> <Image Url|str=None>',
        hidden=True
    )
    async def create_character(self, ctx, name: str, tier: str, availability: str, image_url: Optional[str] = None):
        with db_session:
            _tier = Tier.get(name=tier)
            _availability = Availability.get(name=availability)
            image_name = name.replace('\'/,!', '').replace(' ', '_').replace(':', '-').lower()
            image_url = image_url or f"https://raw.githubusercontent.com/Macro303/Capsule-Corp/main/Resources/Portraits/{image_name}.png"
            character = Character.safe_insert(name, _tier, _availability, image_url)
            await ctx.send(embed=generate_embed(character, ctx.author))
            await ctx.message.delete()

    @commands.has_role('Editor')
    @character_group.command(
        name='Edit',
        pass_context=True,
        usage='<Name|str> <Tier|str> <Availability|str> <Image Url|str=None>',
        hidden=True
    )
    async def edit_character(self, ctx, name: str, tier: str, availability: str, image_url: Optional[str] = None):
        with db_session:
            character = Character.get(name=name)
            if character:
                _tier = Tier.get(name=tier)
                _availability = Availability.get(name=availability)
                image_name = name.replace('\'/,!', '').replace(' ', '_').replace(':', '-').lower()
                image_url = image_url or f"https://raw.githubusercontent.com/Macro303/Capsule-Corp/main/Resources/Portraits/{image_name}.png"
                character.tier = _tier
                character.availability = _availability
                character.image_url = image_url
                await ctx.send(embed=generate_embed(character, ctx.author))
                await ctx.message.delete()
            else:
                LOGGER.warning(f"Unable to find Character: {name}")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @character_group.command(
        name='Delete',
        pass_context=True,
        usage='<Name|str>',
        hidden=True
    )
    async def delete_availability(self, ctx, name: str):
        with db_session:
            character = Character.get(name=name)
            if character:
                character.delete()
                await ctx.message.add_reaction('✅')
            else:
                LOGGER.warning(f"Unable to find Character: {name}")
                await ctx.message.add_reaction('❎')


def setup(bot):
    bot.add_cog(CharacterCog(bot))
