import discord
from discord.ext import commands

import os

# =========================
# SISTEMAS
# =========================

from ranked import setup_ranked

from hall import setup_hall

from shop import (
    setup_shop,
    reset_shop_limits
)

from economy import (
    setup_economy,
    mensal_auto
)

from queue_system import setup_queue

from clans import (
    setup_clans,
    check_inactive
)

from embed import setup_embed

from tournament import setup_tournament


# =========================
# INTENTS
# =========================

intents = discord.Intents.default()

intents.message_content = True

intents.members = True


# =========================
# BOT
# =========================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# READY
# =========================

@bot.event
async def on_ready():

    print(
        f"🔥 Bot ligado como {bot.user}"
    )

    # -------------------------
    # CLÃS INATIVOS
    # -------------------------

    if not check_inactive.is_running():

        check_inactive.start()

    # -------------------------
    # LOJA
    # -------------------------

    if not reset_shop_limits.is_running():

        reset_shop_limits.start()

    # -------------------------
    # COINS MENSAIS
    # -------------------------

    if not mensal_auto.is_running():

        mensal_auto.start(bot)

    print(
        "✅ Sistemas automáticos iniciados."
    )


# =========================
# MESSAGE LOG
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:

        return

    print(
        "MSG:",
        message.content
    )

    await bot.process_commands(
        message
    )


# =========================
# SISTEMAS
# =========================

setup_ranked(bot)

setup_hall(bot)

setup_shop(bot)

setup_economy(bot)

setup_queue(bot)

setup_clans(bot)

setup_embed(bot)

setup_tournament(bot)


# =========================
# DATABASE
# =========================

import database_setup

print(
    "🗄️ SQLITE OK"
)


# =========================
# TOKEN
# =========================

TOKEN = os.getenv(
    "TOKEN"
)

if not TOKEN:

    raise RuntimeError(
        "❌ TOKEN não encontrado nas variáveis de ambiente."
    )


# =========================
# RUN
# =========================

bot.run(
    TOKEN
)
