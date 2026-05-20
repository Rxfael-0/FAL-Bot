import discord
from discord.ext import commands
import os

from bot.ranked import setup_ranked
from bot.hall import setup_hall
from bot.shop import setup_shop
from bot.queue import setup_queue
from bot.clans import setup_clans

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():

    print(
        f"🔥 Bot ligado como {bot.user}"
    )

setup_ranked(bot)
setup_hall(bot)
setup_shop(bot)
setup_queue(bot)
setup_clans(bot)

bot.run(os.getenv("TOKEN"))
