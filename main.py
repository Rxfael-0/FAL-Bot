import discord
from discord.ext import commands
import os

from ranked import setup_ranked
from queue import setup_queue
from economy import setup_economy
from shop import setup_shop
from hall import setup_hall
from clans import setup_clans

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

setup_ranked(bot)
setup_queue(bot)
setup_economy(bot)
setup_shop(bot)
setup_hall(bot)
setup_clans(bot)

@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")

bot.run(os.getenv("TOKEN"))
