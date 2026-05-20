import discord
from discord.ext import commands
import os

from ranked import setup_ranked
from hall import setup_hall
from shop import setup_shop
from economy import setup_economy
from queue_system import setup_queue
from clans import setup_clans

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
setup_clans(bot)

bot.run(
    os.getenv("TOKEN")
)

@bot.event
async def on_message(message):
    print("MSG RECEBIDA:", message.content)
    await bot.process_commands(message)
