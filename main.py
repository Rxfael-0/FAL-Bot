# main.py

import os
import discord

from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURAÇÕES
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError(
        "A variável DISCORD_TOKEN não foi encontrada."
    )


# ============================================================
# INTENTS
# ============================================================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True


# ============================================================
# BOT
# ============================================================

class FALBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):

        print("🔄 Carregando módulos...")

        # ----------------------------------------------------
        # ECONOMY
        # ----------------------------------------------------

        try:
            from economy import setup_economy

            await setup_economy(self)

            print("✅ economy.py carregado")

        except Exception as e:

            print(f"❌ Erro ao carregar economy.py: {e}")

        # ----------------------------------------------------
        # HALL
        # ----------------------------------------------------

        try:
            from hall import setup_hall

            await setup_hall(self)

            print("✅ hall.py carregado")

        except Exception as e:

            print(f"❌ Erro ao carregar hall.py: {e}")

        # ----------------------------------------------------
        # SHOP
        # ----------------------------------------------------

        try:
            from shop import setup_shop

            await setup_shop(self)

            print("✅ shop.py carregado")

        except Exception as e:

            print(f"❌ Erro ao carregar shop.py: {e}")

        # ----------------------------------------------------
        # QUEUE SYSTEM
        # ----------------------------------------------------

        try:
            from queue_system import setup_queue

            await setup_queue(self)

            print("✅ queue_system.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar queue_system.py: {e}"
            )

        # ----------------------------------------------------
        # TOURNAMENT
        # ----------------------------------------------------

        try:
            from tournament import setup_tournament

            await setup_tournament(self)

            print("✅ tournament.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar tournament.py: {e}"
            )

        # ----------------------------------------------------
        # RANKED
        # ----------------------------------------------------

        try:
            from ranked import setup_ranked

            await setup_ranked(self)

            print("✅ ranked.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar ranked.py: {e}"
            )

        # ----------------------------------------------------
        # CLANS
        # ----------------------------------------------------

        try:
            from clans import setup_clans

            await setup_clans(self)

            print("✅ clans.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar clans.py: {e}"
            )

        # ----------------------------------------------------
        # EMBEDS
        # ----------------------------------------------------

        try:
            from embed import setup_embed

            await setup_embed(self)

            print("✅ embed.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar embed.py: {e}"
            )

        # ====================================================
        # SINCRONIZAÇÃO DOS SLASH COMMANDS
        # ====================================================

        print("🔄 Sincronizando comandos /...")

        try:

            synced = await self.tree.sync()

            print(
                f"✅ {len(synced)} comandos sincronizados."
            )

        except Exception as e:

            print(
                f"❌ Erro ao sincronizar comandos: {e}"
            )


    async def on_ready(self):

        print("")
        print("========================================")
        print("        FAL-UP BOT ONLINE")
        print("========================================")
        print(f"🤖 Bot: {self.user}")
        print(f"🆔 ID: {self.user.id}")
        print(
            f"🌐 Servidores: {len(self.guilds)}"
        )
        print("========================================")
        print("")


# ============================================================
# INSTÂNCIA
# ============================================================

bot = FALBot()


# ============================================================
# COMANDO DE TESTE
# ============================================================

@bot.tree.command(
    name="ping",
    description="Verifica se o bot está funcionando."
)
async def ping(
    interaction: discord.Interaction
):

    latency = round(bot.latency * 1000)

    await interaction.response.send_message(
        f"🏓 Pong!\n"
        f"📡 Latência: **{latency}ms**"
    )


# ============================================================
# TRATAMENTO DE ERROS DOS SLASH COMMANDS
# ============================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    # --------------------------------------------------------
    # SEM PERMISSÃO
    # --------------------------------------------------------

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        mensagem = (
            "❌ Você não possui permissão "
            "para usar este comando."
        )

    # --------------------------------------------------------
    # COMANDO NÃO ENCONTRADO
    # --------------------------------------------------------

    elif isinstance(
        error,
        app_commands.errors.CommandNotFound
    ):

        mensagem = (
            "❌ Esse comando não existe."
        )

    # --------------------------------------------------------
    # ERRO GENÉRICO
    # --------------------------------------------------------

    else:

        print(
            f"❌ Erro no comando: {error}"
        )

        mensagem = (
            "❌ Ocorreu um erro ao executar "
            "este comando."
        )

    # --------------------------------------------------------
    # ENVIA RESPOSTA
    # --------------------------------------------------------

    try:

        if interaction.response.is_done():

            await interaction.followup.send(
                mensagem,
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                mensagem,
                ephemeral=True
            )

    except Exception as e:

        print(
            f"❌ Erro ao enviar mensagem de erro: {e}"
        )


# ============================================================
# INICIAR BOT
# ============================================================

bot.run(TOKEN)
