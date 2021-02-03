import logging
from argparse import ArgumentParser, Namespace

import discord
from discord.ext import commands
from pony.orm import db_session

from Bot import CONFIG
from Database import update_data
from Logger import init_logger

LOGGER = logging.getLogger(__name__)
COGS = ['Bot.cogs.affinity', 'Bot.cogs.affiliation', 'Bot.cogs.tier', 'Bot.cogs.character', 'Bot.cogs.other']
bot = commands.Bot(command_prefix=CONFIG['Prefix'], case_insensitive=True)


@bot.event
async def on_ready():
    LOGGER.info(f"Logged in as: {bot.user}")
    bot.remove_command('Help')
    for cog in COGS:
        bot.load_extension(cog)
    await bot.change_presence(activity=discord.Game(name='DC Legends: Fight Superheroes'))


@bot.event
async def on_command_error(ctx, error):
    LOGGER.error(error)
    await ctx.send(error)

def get_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--init', action='store_true')
    return parser.parse_args()

if __name__ == "__main__":
    init_logger('Alfred_Bot')
    args = get_arguments()
    if args.init:
        with db_session:
            update_data()
    if CONFIG['Token']:
        bot.run(CONFIG['Token'], bot=True, reconnect=True)
    else:
        LOGGER.critical('Missing your Discord `Token`, update the config.yaml to continue')
