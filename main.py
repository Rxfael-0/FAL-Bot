import discord
from discord.ext import commands
import os

from ranked import setup_ranked
from hall import setup_hall
from shop import setup_shop, reset_shop_limits
from economy import setup_economy
from queue_system import setup_queue
from clans import setup_clans, check_inactive
from embed import setup_embed
from tournament import setup_tournament

intents = discord.Intents.default()

intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():

    print(f"🔥 Bot ligado como {bot.user}")

    if not check_inactive.is_running():
        check_inactive.start()

    if not reset_shop_limits.is_running():
        reset_shop_limits.start()

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    print("MSG:", message.content)

    await bot.process_commands(message)

setup_ranked(bot)
setup_hall(bot)
setup_shop(bot)
setup_economy(bot)
setup_queue(bot)
setup_clans(bot)
setup_embed(bot)
setup_tournament(bot)

bot.run(os.getenv("TOKEN"))
