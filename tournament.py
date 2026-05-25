import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import sqlite3

REGISTRO_CHANNEL = 1463346916120068106
LOGS_CHANNEL = 1463389943995830445
VALIDADOS_CHANNEL = 1508246884442050690

VIP_ROLE = 1460867416081825904
MEGAVIP_ROLE = 1460867926948057202

MAX_VAGAS = 32

# =========================
# SQLITE
# =========================

conn = sqlite3.connect(
    "database/database.db"
)

cursor = conn.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS tournament (

    user_id INTEGER PRIMARY KEY,

    tipo TEXT,
    nome TEXT,
    roblox TEXT,
    convidado TEXT,

    validado INTEGER DEFAULT 0

)

""")

conn.commit()

def total_inscritos():

    cursor.execute(
        "SELECT COUNT(*) FROM tournament"
    )

    return cursor.fetchone()[0]

# =========================
# MODAIS
# =========================

class NormalModal(Modal, title="Inscrição Normal"):

    nome = TextInput(
        label="Seu nome Discord (@)",
        placeholder="@player"
    )

    roblox = TextInput(
        label="Nick no Roblox"
    )

    convidado = TextInput(
        label="Nome do amigo convidado"
    )

    regras = TextInput(
        label="Concorda com regras? (sim)"
    )

    async def on_submit(self, interaction):

        cursor.execute(

            "SELECT * FROM tournament WHERE user_id = ?",

            (interaction.user.id,)
        )

        if cursor.fetchone():

            return await interaction.response.send_message(
                "❌ Você já está inscrito.",
                ephemeral=True
            )

        if total_inscritos() >= MAX_VAGAS:

            return await interaction.response.send_message(
                "❌ Todas vagas foram preenchidas.",
                ephemeral=True
            )

        cursor.execute("""

        INSERT INTO tournament (

            user_id,
            tipo,
            nome,
            roblox,
            convidado

        )

        VALUES (?, ?, ?, ?, ?)

        """, (

            interaction.user.id,
            "NORMAL",
            self.nome.value,
            self.roblox.value,
            self.convidado.value

        ))

        conn.commit()

        canal = interaction.guild.get_channel(
            LOGS_CHANNEL
        )

        embed = discord.Embed(
            title="📩 NOVA INSCRIÇÃO",
            color=discord.Color.green()
        )

        embed.add_field(
            name="👤 Usuário",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="🎟 Tipo",
            value="NORMAL",
            inline=False
        )

        embed.add_field(
            name="🎮 Roblox",
            value=self.roblox.value,
            inline=False
        )

        embed.add_field(
            name="👥 Convidado",
            value=self.convidado.value,
            inline=False
        )

        await canal.send(embed=embed)

        await interaction.response.send_message(
            "✅ Inscrição enviada para análise.",
            ephemeral=True
        )

class VipModal(Modal):

    def __init__(self, tipo):

        super().__init__(
            title=f"Inscrição {tipo}"
        )

        self.tipo = tipo

        self.nome = TextInput(
            label="Seu nome Discord (@)",
            placeholder="@player"
        )

        self.roblox = TextInput(
            label="Nick no Roblox"
        )

        self.regras = TextInput(
            label="Concorda com regras? (sim)"
        )

        self.add_item(self.nome)
        self.add_item(self.roblox)
        self.add_item(self.regras)

    async def on_submit(self, interaction):

        cursor.execute(

            "SELECT * FROM tournament WHERE user_id = ?",

            (interaction.user.id,)
        )

        if cursor.fetchone():

            return await interaction.response.send_message(
                "❌ Você já está inscrito.",
                ephemeral=True
            )

        if total_inscritos() >= MAX_VAGAS:

            return await interaction.response.send_message(
                "❌ Todas vagas foram preenchidas.",
                ephemeral=True
            )

        cursor.execute("""

        INSERT INTO tournament (

            user_id,
            tipo,
            nome,
            roblox

        )

        VALUES (?, ?, ?, ?)

        """, (

            interaction.user.id,
            self.tipo,
            self.nome.value,
            self.roblox.value

        ))

        conn.commit()

        canal = interaction.guild.get_channel(
            LOGS_CHANNEL
        )

        embed = discord.Embed(
            title="📩 NOVA INSCRIÇÃO",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="👤 Usuário",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="🎟 Tipo",
            value=self.tipo,
            inline=False
        )

        embed.add_field(
            name="🎮 Roblox",
            value=self.roblox.value,
            inline=False
        )

        await canal.send(embed=embed)

        await interaction.response.send_message(
            (
                "✅ Inscrição enviada.\n\n"
                "📩 Abra um ticket para realizar a compra "
                "e aguarde a validação da staff."
            ),
            ephemeral=True
        )

# =========================
# SELECT MENU
# =========================

class TournamentSelect(Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Normal",
                description="Grátis • convidar 1 amigo",
                emoji="📌"
            ),

            discord.SelectOption(
                label="VIP",
                description="10 Robux",
                emoji="💎"
            ),

            discord.SelectOption(
                label="MEGAVIP",
                description="50 Robux",
                emoji="🔥"
            )
        ]

        super().__init__(

            placeholder="Escolha sua inscrição",

            options=options
        )

    async def callback(self, interaction):

        escolha = self.values[0]

        if escolha == "Normal":

            await interaction.response.send_modal(
                NormalModal()
            )

        elif escolha == "VIP":

            await interaction.response.send_modal(
                VipModal("VIP")
            )

        elif escolha == "MEGAVIP":

            await interaction.response.send_modal(
                VipModal("MEGAVIP")
            )

class TournamentView(View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            TournamentSelect()
        )

# =========================
# SETUP
# =========================

def setup_tournament(bot):

    @bot.command()
    async def torneio(ctx):

        if ctx.channel.id != REGISTRO_CHANNEL:

            return

        vagas = MAX_VAGAS - total_inscritos()

        embed = discord.Embed(

            title="🎟 INSCRIÇÕES — TORNEIO FAL",

            description=(

                "Escolha abaixo o tipo de inscrição.\n\n"

                "📌 NORMAL\n"
                "• Gratuito\n"
                "• Necessário convidar 1 amigo\n\n"

                "💎 VIP — 10 Robux\n"
                "• Aprovação prioritária\n\n"

                "🔥 MEGAVIP — 50 Robux\n"
                "• Prioridade máxima\n\n"

                f"🎮 Vagas restantes: {vagas}/{MAX_VAGAS}\n\n"

                "⚠ Todas inscrições passam "
                "por validação da staff."
            ),

            color=discord.Color.red()
        )

        await ctx.send(
            embed=embed,
            view=TournamentView()
        )

    @bot.command()
    async def validar(
        ctx,
        member: discord.Member
    ):

        cursor.execute(

            "SELECT tipo FROM tournament WHERE user_id = ?",

            (member.id,)
        )

        resultado = cursor.fetchone()

        if not resultado:

            return await ctx.send(
                "❌ Usuário não encontrado."
            )

        tipo = resultado[0]

        cursor.execute("""

        UPDATE tournament

        SET validado = 1

        WHERE user_id = ?

        """, (member.id,))

        conn.commit()

        if tipo == "VIP":

            cargo = ctx.guild.get_role(
                VIP_ROLE
            )

            await member.add_roles(cargo)

        elif tipo == "MEGAVIP":

            cargo = ctx.guild.get_role(
                MEGAVIP_ROLE
            )

            await member.add_roles(cargo)

        canal = ctx.guild.get_channel(
            VALIDADOS_CHANNEL
        )

        embed = discord.Embed(

            title="✅ INSCRIÇÃO VALIDADA",

            description=(

                f"{member.mention}\n\n"
                f"🎟 Tipo: {tipo}\n\n"
                "Boa sorte no torneio 🔥"
            ),

            color=discord.Color.green()
        )

        await canal.send(embed=embed)

        await ctx.send(
            "✅ Inscrição validada."
            )
