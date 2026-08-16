import discord
from discord.ext import commands
from discord.ui import View, button
import asyncio

# =========================
# CONFIGURAÇÕES
# =========================

L1_CHANNEL = 1460497983194923174
L2_CHANNEL = 1460498463417569402
L3_CHANNEL = 1460498551804133397

ANALISTA = 1399531186472226898

L1_ROLE = 1460723355945795821
L2_ROLE = 1460723503971172403
L3_ROLE = 1460723621025681523

PLAYERS_PER_QUEUE = 4
COOLDOWN_SECONDS = 1200


# =========================
# FILAS
# =========================

filas = {
    "L1": [],
    "L2": [],
    "L3": []
}

cooldowns = {
    "L1": False,
    "L2": False,
    "L3": False
}


# =========================
# VIEW DA FILA
# =========================

class QueueView(View):

    def __init__(self, league):

        super().__init__(
            timeout=None
        )

        self.league = league


    # =========================
    # ENTRAR
    # =========================

    @button(
        label="Entrar na fila",
        style=discord.ButtonStyle.green,
        emoji="✅"
    )
    async def entrar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        league = self.league

        role_id = {
            "L1": L1_ROLE,
            "L2": L2_ROLE,
            "L3": L3_ROLE
        }[league]

        role = interaction.guild.get_role(
            role_id
        )

        if role is None:

            return await interaction.response.send_message(
                "❌ Cargo da league não encontrado.",
                ephemeral=True
            )

        if role not in interaction.user.roles:

            return await interaction.response.send_message(
                f"❌ Você não pertence à **{league}**.",
                ephemeral=True
            )

        if cooldowns[league]:

            return await interaction.response.send_message(
                "⏳ Esta fila está em cooldown.",
                ephemeral=True
            )

        if interaction.user in filas[league]:

            return await interaction.response.send_message(
                "❌ Você já está na fila.",
                ephemeral=True
            )

        # Adiciona jogador

        filas[league].append(
            interaction.user
        )

        posicao = len(
            filas[league]
        )

        await interaction.response.send_message(
            (
                f"✅ Você entrou na fila **{league}**!\n"
                f"📍 Posição: **{posicao}/{PLAYERS_PER_QUEUE}**"
            ),
            ephemeral=True
        )

        # =========================
        # FILA COMPLETA
        # =========================

        if len(filas[league]) >= PLAYERS_PER_QUEUE:

            cooldowns[league] = True

            players = ""

            for membro in filas[league][
                :PLAYERS_PER_QUEUE
            ]:

                players += (
                    f"• {membro.mention}\n"
                )

            analista = interaction.guild.get_role(
                ANALISTA
            )

            analista_mention = (
                analista.mention
                if analista
                else "Analista não encontrado"
            )

            embed = discord.Embed(
                title=f"⚔️ FILA {league} COMPLETA",
                description=(
                    "🎮 **Partida encontrada!**\n\n"
                    f"{players}"
                ),
                color=discord.Color.red()
            )

            embed.add_field(
                name="🎯 Analista",
                value=analista_mention,
                inline=False
            )

            embed.set_footer(
                text="FAL • Ranked"
            )

            await interaction.channel.send(
                content=(
                    f"{players}\n"
                    f"{analista_mention}"
                ),
                embed=embed
            )

            # Limpa a fila

            filas[league] = []

            # =========================
            # COOLDOWN
            # =========================

            asyncio.create_task(
                liberar_fila(
                    league
                )
            )


    # =========================
    # SAIR
    # =========================

    @button(
        label="Sair da fila",
        style=discord.ButtonStyle.red,
        emoji="❌"
    )
    async def sair(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        league = self.league

        if interaction.user not in filas[league]:

            return await interaction.response.send_message(
                "❌ Você não está na fila.",
                ephemeral=True
            )

        filas[league].remove(
            interaction.user
        )

        await interaction.response.send_message(
            (
                f"❌ Você saiu da fila **{league}**."
            ),
            ephemeral=True
        )


# =========================
# LIBERAR FILA
# =========================

async def liberar_fila(league):

    await asyncio.sleep(
        COOLDOWN_SECONDS
    )

    cooldowns[league] = False

    print(
        f"🔓 Fila {league} liberada."
    )


# =========================
# SETUP
# =========================

def setup_queue(bot):

    @bot.command()
    async def fila(
        ctx,
        league
    ):

        league = league.upper()

        if league not in [
            "L1",
            "L2",
            "L3"
        ]:

            return await ctx.send(
                "❌ League inválida.\n"
                "Use: `!fila L1`, `!fila L2` ou `!fila L3`."
            )

        canal_correto = {
            "L1": L1_CHANNEL,
            "L2": L2_CHANNEL,
            "L3": L3_CHANNEL
        }[league]

        if ctx.channel.id != canal_correto:

            return await ctx.send(
                "❌ Este comando só pode ser usado "
                "no canal correto da fila."
            )

        if cooldowns[league]:

            return await ctx.send(
                "⏳ Esta fila está em cooldown."
            )

        embed = discord.Embed(
            title=f"⚔️ FILA {league}",
            description=(
                "Entre na fila para encontrar "
                "uma partida ranked.\n\n"
                "Clique nos botões abaixo para "
                "entrar ou sair."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="📌 Regras",
            value=(
                "• Apenas membros da league\n"
                "• 4 players por partida\n"
                "• Após completar, cooldown de 20 minutos"
            ),
            inline=False
        )

        embed.add_field(
            name="👥 Jogadores",
            value=(
                f"**{len(filas[league])}"
                f"/{PLAYERS_PER_QUEUE}**"
            ),
            inline=False
        )

        embed.set_footer(
            text="FAL • Ranked Queue"
        )

        await ctx.send(
            embed=embed,
            view=QueueView(league)
        )
