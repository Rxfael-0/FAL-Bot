import discord
from discord.ext import commands
from discord.ui import View, button
import asyncio

L1_CHANNEL = 1460497983194923174
L2_CHANNEL = 1460498463417569402
L3_CHANNEL = 1460498551804133397

ANALISTA = 1399531186472226898

L1_ROLE = 1460723355945795821
L2_ROLE = 1460723503971172403
L3_ROLE = 1460723621025681523

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

class QueueView(View):

    def __init__(self, league):

        super().__init__(timeout=None)

        self.league = league

    @button(
        label="Entrar fila",
        style=discord.ButtonStyle.green,
        emoji="✅"
    )
    async def entrar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        role_id = {

            "L1": L1_ROLE,
            "L2": L2_ROLE,
            "L3": L3_ROLE

        }[self.league]

        role = interaction.guild.get_role(
            role_id
        )

        if role not in interaction.user.roles:

            return await interaction.response.send_message(
                "❌ Você não pertence "
                f"a {self.league}",
                ephemeral=True
            )

        if cooldowns[self.league]:

            return await interaction.response.send_message(
                "⏳ Fila em cooldown.",
                ephemeral=True
            )

        if interaction.user in filas[self.league]:

            return await interaction.response.send_message(
                "❌ Você já está na fila.",
                ephemeral=True
            )

        filas[self.league].append(
            interaction.user
        )

        await interaction.response.send_message(
            (
                f"✅ {interaction.user.mention} "
                f"entrou na fila "
                f"{self.league}"
            )
        )

        if len(filas[self.league]) >= 4:

            cooldowns[self.league] = True

            players = ""

            for m in filas[self.league]:

                players += f"{m.mention}\n"

            analista = interaction.guild.get_role(
                ANALISTA
            )

            embed = discord.Embed(
                title=f"⚔️ FILA {self.league} COMPLETA",
                description=players,
                color=discord.Color.red()
            )

            embed.add_field(
                name="🎯 Analista",
                value=analista.mention
            )

            await interaction.channel.send(
                embed=embed
            )

            filas[self.league] = []

            await asyncio.sleep(
                1200
            )

            cooldowns[self.league] = False

    @button(
        label="Sair fila",
        style=discord.ButtonStyle.red,
        emoji="❌"
    )
    async def sair(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user not in filas[self.league]:

            return await interaction.response.send_message(
                "❌ Você não está na fila.",
                ephemeral=True
            )

        filas[self.league].remove(
            interaction.user
        )

        await interaction.response.send_message(
            (
                f"❌ {interaction.user.mention} "
                f"saiu da fila."
            )
        )

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
                "❌ League inválida."
            )

        canal_correto = {

            "L1": L1_CHANNEL,
            "L2": L2_CHANNEL,
            "L3": L3_CHANNEL

        }[league]

        if ctx.channel.id != canal_correto:

            return await ctx.send(
                "❌ Canal incorreto."
            )

        embed = discord.Embed(
            title=f"⚔️ FILA {league}",
            description=(
                "Clique abaixo "
                "para entrar na fila."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="📌 Regras",
            value=(
                "• Apenas membros da league\n"
                "• 4 players por fila\n"
                "• cooldown 20 minutos"
            ),
            inline=False
        )

        await ctx.send(
            embed=embed,
            view=QueueView(league)
            )
