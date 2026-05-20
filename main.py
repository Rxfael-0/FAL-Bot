import discord
from discord.ext import commands
import os

from bot.ranked import setup_ranked
from bot.hall import setup_hall
from bot.shop import setup_shop
from bot.economy import setup_economy
from bot.queue import setup_queue

intents = discord.Intents.default()

intents.message_content = True
intents.members = True

bot = commands.Bot(

    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():

    print(
        f"🔥 Bot ligado como "
        f"{bot.user}"
    )

setup_ranked(bot)
setup_hall(bot)
setup_shop(bot)
setup_economy(bot)
setup_queue(bot)

bot.run(
    os.getenv("TOKEN")
)
