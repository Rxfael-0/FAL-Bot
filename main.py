# main.py

import os
import inspect
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


    # ========================================================
    # SETUP
    # ========================================================

    async def setup_hook(self):

        print("")
        print("========================================")
        print("       🔄 CARREGANDO FAL-UP BOT")
        print("========================================")
        print("")


        # ====================================================
        # DATABASE
        # ====================================================

        try:

            import database_setup

            print("✅ database_setup.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar database_setup.py: {e}"
            )


        # ====================================================
        # FUNÇÃO AUXILIAR
        # ====================================================

        async def carregar(
            nome,
            funcao
        ):

            try:

                resultado = funcao(self)

                if inspect.isawaitable(resultado):

                    await resultado

                print(
                    f"✅ {nome} carregado"
                )

            except Exception as e:

                print(
                    f"❌ Erro ao carregar {nome}: {e}"
                )


        # ====================================================
        # ECONOMY
        # ====================================================

        try:

            from economy import setup_economy

            resultado = setup_economy(self)

            if inspect.isawaitable(resultado):

                await resultado

            print("✅ economy.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar economy.py: {e}"
            )


        # ====================================================
        # HALL
        # ====================================================

        try:

            from hall import setup_hall

            resultado = setup_hall(self)

            if inspect.isawaitable(resultado):

                await resultado

            print("✅ hall.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar hall.py: {e}"
            )


        # ====================================================
        # RANKED
        # ====================================================

        try:

            from ranked import setup_ranked

            resultado = setup_ranked(self)

            if inspect.isawaitable(resultado):

                await resultado

            print("✅ ranked.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar ranked.py: {e}"
            )


        # ====================================================
        # QUEUE SYSTEM
        # ====================================================

        try:

            from queue_system import setup_queue

            resultado = setup_queue(self)

            if inspect.isawaitable(resultado):

                await resultado

            print("✅ queue_system.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar queue_system.py: {e}"
            )


        # ====================================================
        # SHOP
        # ====================================================

        try:

            from shop import setup_shop

            resultado = setup_shop(self)

            if inspect.isawaitable(resultado):

                await resultado

            print("✅ shop.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar shop.py: {e}"
            )


        # ====================================================
        # CLANS
        # ====================================================

        try:

            from clans import setup_clans

            resultado = setup_clans(self)

            if inspect.isawaitable(resultado):

                await resultado

            print("✅ clans.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar clans.py: {e}"
            )


        # ====================================================
        # EMBED
        # ====================================================

        try:

            from embed import setup_embed

            resultado = setup_embed(self)

            if inspect.isawaitable(resultado):

                await resultado

            print("✅ embed.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar embed.py: {e}"
            )


        # ====================================================
        # TOURNAMENT
        # ====================================================

        try:

            from tournament import setup_tournament

            resultado = setup_tournament(self)

            if inspect.isawaitable(resultado):

                await resultado

            print("✅ tournament.py carregado")

        except Exception as e:

            print(
                f"❌ Erro ao carregar tournament.py: {e}"
            )


        # ====================================================
        # SINCRONIZAR SLASH COMMANDS
        # ====================================================

        print("")
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


        print("")
        print("========================================")
        print("       ✅ MÓDULOS CARREGADOS")
        print("========================================")
        print("")


    # ========================================================
    # READY
    # ========================================================

    async def on_ready(self):

        print("")
        print("========================================")
        print("          FAL-UP BOT ONLINE")
        print("========================================")
        print(f"🤖 Bot: {self.user}")
        print(f"🆔 ID: {self.user.id}")
        print(f"🌐 Servidores: {len(self.guilds)}")
        print("========================================")
        print("")


# ============================================================
# INSTÂNCIA
# ============================================================

bot = FALBot()


# ============================================================
# /PING
# ============================================================

@bot.tree.command(
    name="ping",
    description="Verifica se o bot está funcionando."
)
async def ping(
    interaction: discord.Interaction
):

    latency = round(
        bot.latency * 1000
    )

    await interaction.response.send_message(
        f"🏓 Pong!\n"
        f"📡 Latência: **{latency}ms**"
    )


# ============================================================
# ERROS DOS SLASH COMMANDS
# ============================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    # ========================================================
    # SEM PERMISSÃO
    # ========================================================

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        mensagem = (
            "❌ Você não possui permissão "
            "para usar este comando."
        )


    # ========================================================
    # COMANDO NÃO ENCONTRADO
    # ========================================================

    elif isinstance(
        error,
        app_commands.errors.CommandNotFound
    ):

        mensagem = (
            "❌ Esse comando não existe."
        )


    # ========================================================
    # ERRO GENÉRICO
    # ========================================================

    else:

        print("")
        print("========================================")
        print("❌ ERRO EM SLASH COMMAND")
        print("========================================")
        print(error)
        print("========================================")
        print("")

        mensagem = (
            "❌ Ocorreu um erro ao executar "
            "este comando."
        )


    # ========================================================
    # ENVIAR ERRO
    # ========================================================

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
