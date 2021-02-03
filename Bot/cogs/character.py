import logging
from typing import Optional

from discord import Embed
from discord.ext import commands
from discord.member import Member
from pony.orm import db_session, raw_sql, select

from Bot import load_colour
from Database import Character, update_data

LOGGER = logging.getLogger(__name__)


def generate_embed(character: Character, author: Member) -> Embed:
    embed = Embed(title=character.name, colour=load_colour(character.affinity.colour_code))

    embed.add_field(name='Affiliations', value=', '.join(sorted([it.name for it in character.affiliations])))
    embed.add_field(name='Health', value=character.health)
    embed.add_field(name='Intelligence', value=character.intelligence)
    embed.add_field(name='Speed', value=character.speed)
    embed.add_field(name='Strength', value=character.strength)
    embed.add_field(name='Tier', value=f"Tier {character.tier.name}" if character.tier else 'None')

    if character.image_url:
        embed.set_thumbnail(url=character.image_url)
    embed.set_footer(
        text=f"Requested by {author.name}|Data from https://dcltoolkit.com",
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
        name='Update',
        pass_context=True,
        usage=None,
        hidden=True
    )
    async def update_db(self, ctx):
        with db_session:
            update_data()
            await ctx.message.add_reaction('✅')


def setup(bot):
    bot.add_cog(CharacterCog(bot))
