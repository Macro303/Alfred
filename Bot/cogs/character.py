import logging
from typing import Optional

from discord import Embed
from discord.ext import commands
from discord.member import Member
from pony.orm import db_session, raw_sql, select

from Bot import load_colour
from Database import Affinity, Affiliation, Tier, Character

LOGGER = logging.getLogger(__name__)


def generate_embed(character: Character, author: Member) -> Embed:
    embed = Embed(title=character.name, colour=load_colour(character.affinity.colour_code))

    embed.add_field(name='Affiliations', value=', '.join(sorted([it.name for it in character.affiliations])))
    embed.add_field(name='Tier', value=f"Tier {character.tier.name}" if character.tier else 'None')

    if character.image_url:
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
        usage='<Name|str> <Title|str=%>'
    )
    async def character_group(self, ctx, name: str, title: str='%'):
        with db_session:
            results = select(x for x in Character if raw_sql(f'x.title LIKE "{title}"') and name in x.name)[:]
            if results:
                for character in sorted(results):
                    await ctx.send(embed=generate_embed(character, ctx.author))
            else:
                LOGGER.warning(f"Unable to find Character: {name}, {title}")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @character_group.command(
        name='Create',
        pass_context=True,
        usage='<Name|str> <Title|str> <Affinity|str> <Tier|str=None> <Image Url|str=None> [<Affiliations|str>]',
        hidden=True
    )
    async def create_character(self, ctx, name: str, title: str, affinity: str, tier: Optional[str] = None, image_url: Optional[str] = None, *affiliations: str):
        with db_session:
            if not image_url or image_url.lower() == 'none':
                image_url = None
            character = Character.safe_insert(name, title, Affinity.find(affinity), list(set([Affiliation.safe_insert(it) for it in affiliations])), Tier.find(tier), image_url)
            await ctx.send(embed=generate_embed(character, ctx.author))

    @commands.has_role('Editor')
    @character_group.group(
        name='Edit',
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
        hidden=True
    )
    async def edit_group(self, ctx):
        pass

    @commands.has_role('Editor')
    @edit_group.command(
        name='Affinity',
        pass_context=True,
        usage='<Name|str> <Title|str> <Affinity|str>',
        hidden=True
    )
    async def edit_affinity(self, ctx, name: str, title: str, affinity: str):
        with db_session:
            character = Character.get(name=name, title=title)
            if character:
                character.affinity = Affinity.find(affinity)
                await ctx.send(embed=generate_embed(character, ctx.author))
            else:
                LOGGER.warning(f"Unable to find Character: {name}, {title}")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @edit_group.command(
        name='Tier',
        pass_context=True,
        usage='<Name|str> <Title|str> <Tier|str=None>',
        hidden=True
    )
    async def edit_tier(self, ctx, name: str, title: str, tier: Optional[str] = None):
        with db_session:
            character = Character.get(name=name, title=title)
            if character:
                character.tier = Tier.find(tier)
                await ctx.send(embed=generate_embed(character, ctx.author))
            else:
                LOGGER.warning(f"Unable to find Character: {name}, {title}")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @edit_group.command(
        name='Image',
        pass_context=True,
        usage='<Name|str> <Title|str> <Image Url|str=None>',
        hidden=True
    )
    async def edit_image(self, ctx, name: str, title: str, image_url: Optional[str] = None):
        with db_session:
            character = Character.get(name=name, title=title)
            if character:
                character.image_url = image_url
                await ctx.send(embed=generate_embed(character, ctx.author))
            else:
                LOGGER.warning(f"Unable to find Character: {name}, {title}")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @edit_group.command(
        name='Tags',
        aliases=['Tag'],
        pass_context=True,
        usage='<Name|str> <Title|str> [<Affiliations|str>]',
        hidden=True
    )
    async def edit_affiliations(self, ctx, name: str, title: str, *affiliations: str):
        with db_session:
            character = Character.get(name=name, title=title)
            if character:
                character.tags = list(set([Affiliation.safe_insert(it) for it in affiliations]))
                await ctx.send(embed=generate_embed(character, ctx.author))
            else:
                LOGGER.warning(f"Unable to find Character: {name}, {title}")
                await ctx.message.add_reaction('❎')

    @commands.has_role('Editor')
    @character_group.command(
        name='Delete',
        pass_context=True,
        usage='<Name|str> <Title|str>',
        hidden=True
    )
    async def delete_character(self, ctx, name: str, title: str):
        with db_session:
            character = Character.get(name=name, title=title)
            if character:
                character.delete()
                await ctx.message.add_reaction('✅')
            else:
                LOGGER.warning(f"Unable to find Character: {name}, {title}")
                await ctx.message.add_reaction('❎')


def setup(bot):
    bot.add_cog(CharacterCog(bot))
