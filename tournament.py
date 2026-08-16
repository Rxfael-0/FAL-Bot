import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import sqlite3

DATABASE = "database/database.db"

REGISTRO_CHANNEL = 1463346916120068106
LOGS_CHANNEL = 1463389943995830445
VALIDADOS_CHANNEL = 1508246884442050690

VIP_ROLE = 1460867416081825904
MEGAVIP_ROLE = 1460867926948057202

MAX_VAGAS = 32


# =========================
# SQLITE
# =========================

def connect_db():
    return sqlite3.connect(DATABASE)


def setup_database():

    conn = connect_db()
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
    conn.close()


setup_database()


# =========================
# INSCRITOS
# =========================

def total_inscritos():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM tournament"
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total


def usuario_inscrito(user_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tournament
        WHERE user_id = ?
        """,
        (user_id,)
    )

    resultado = cursor.fetchone()

    conn.close()

    return resultado


# =========================
# MODAL NORMAL
# =========================

class NormalModal(
    Modal,
    title="Inscrição Normal"
):

    nome = TextInput(
        label="Seu nome Discord (@)",
        placeholder="@player",
        max_length=100
    )

    roblox = TextInput(
        label="Nick no Roblox",
        placeholder="Seu nick",
        max_length=50
    )

    convidado = TextInput(
        label="Nome do amigo convidado",
        placeholder="Nick do amigo",
        max_length=50
    )

    regras = TextInput(
        label="Concorda com as regras? (sim)",
        placeholder="sim",
        max_length=10
    )


    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if usuario_inscrito(
            interaction.user.id
        ):

            return await interaction.response.send_message(
                "❌ Você já está inscrito.",
                ephemeral=True
            )

        if total_inscritos() >= MAX_VAGAS:

            return await interaction.response.send_message(
                "❌ Todas as vagas foram preenchidas.",
                ephemeral=True
            )

        if self.regras.value.lower() not in [
            "sim",
            "s",
            "yes"
        ]:

            return await interaction.response.send_message(
                "❌ Você precisa concordar com as regras.",
                ephemeral=True
            )

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tournament (
                user_id,
                tipo,
                nome,
                roblox,
                convidado,
                validado
            )

            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (
                interaction.user.id,
                "NORMAL",
                self.nome.value,
                self.roblox.value,
                self.convidado.value
            )
        )

        conn.commit()
        conn.close()

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

        if canal:

            await canal.send(
                embed=embed
            )

        await interaction.response.send_message(
            "✅ Inscrição enviada para análise da staff.",
            ephemeral=True
        )


# =========================
# MODAL VIP
# =========================

class VipModal(Modal):

    def __init__(self, tipo):

        super().__init__(
            title=f"Inscrição {tipo}"
        )

        self.tipo = tipo

        self.nome = TextInput(
            label="Seu nome Discord (@)",
            placeholder="@player",
            max_length=100
        )

        self.roblox = TextInput(
            label="Nick no Roblox",
            placeholder="Seu nick",
            max_length=50
        )

        self.regras = TextInput(
            label="Concorda com as regras? (sim)",
            placeholder="sim",
            max_length=10
        )

        self.add_item(
            self.nome
        )

        self.add_item(
            self.roblox
        )

        self.add_item(
            self.regras
        )


    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if usuario_inscrito(
            interaction.user.id
        ):

            return await interaction.response.send_message(
                "❌ Você já está inscrito.",
                ephemeral=True
            )

        if total_inscritos() >= MAX_VAGAS:

            return await interaction.response.send_message(
                "❌ Todas as vagas foram preenchidas.",
                ephemeral=True
            )

        if self.regras.value.lower() not in [
            "sim",
            "s",
            "yes"
        ]:

            return await interaction.response.send_message(
                "❌ Você precisa concordar com as regras.",
                ephemeral=True
            )

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tournament (
                user_id,
                tipo,
                nome,
                roblox,
                convidado,
                validado
            )

            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (
                interaction.user.id,
                self.tipo,
                self.nome.value,
                self.roblox.value,
                None
            )
        )

        conn.commit()
        conn.close()

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

        if canal:

            await canal.send(
                embed=embed
            )

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
                emoji="📌",
                value="NORMAL"
            ),

            discord.SelectOption(
                label="VIP",
                description="10 Robux",
                emoji="💎",
                value="VIP"
            ),

            discord.SelectOption(
                label="MEGAVIP",
                description="50 Robux",
                emoji="🔥",
                value="MEGAVIP"
            )
        ]

        super().__init__(
            placeholder="Escolha sua inscrição",
            options=options,
            min_values=1,
            max_values=1
        )


    async def callback(
        self,
        interaction: discord.Interaction
    ):

        escolha = self.values[0]

        if escolha == "NORMAL":

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


# =========================
# VIEW
# =========================

class TournamentView(View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

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

        vagas = max(
            0,
            MAX_VAGAS - total_inscritos()
        )

        embed = discord.Embed(
            title="🎟 INSCRIÇÕES — TORNEIO FAL",
            description=(
                "Escolha abaixo o tipo de inscrição.\n\n"

                "📌 **NORMAL**\n"
                "• Gratuito\n"
                "• Necessário convidar 1 amigo\n\n"

                "💎 **VIP — 10 Robux**\n"
                "• Aprovação prioritária\n\n"

                "🔥 **MEGAVIP — 50 Robux**\n"
                "• Prioridade máxima\n\n"

                f"🎮 **Vagas restantes: "
                f"{vagas}/{MAX_VAGAS}**\n\n"

                "⚠ Todas as inscrições passam "
                "por validação da staff."
            ),
            color=discord.Color.red()
        )

        embed.set_footer(
            text="FAL • Torneio"
        )

        await ctx.send(
            embed=embed,
            view=TournamentView()
        )


    # =========================
    # VALIDAR
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def validar(
        ctx,
        member: discord.Member
    ):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT tipo, validado
            FROM tournament
            WHERE user_id = ?
            """,
            (member.id,)
        )

        resultado = cursor.fetchone()

        if not resultado:

            conn.close()

            return await ctx.send(
                "❌ Usuário não encontrado."
            )

        tipo = resultado[0]
        validado = resultado[1]

        if validado:

            conn.close()

            return await ctx.send(
                "❌ Esta inscrição já foi validada."
            )

        cursor.execute(
            """
            UPDATE tournament

            SET validado = 1

            WHERE user_id = ?
            """,
            (member.id,)
        )

        conn.commit()
        conn.close()

        # =========================
        # CARGO
        # =========================

        if tipo == "VIP":

            cargo = ctx.guild.get_role(
                VIP_ROLE
            )

            if cargo:

                await member.add_roles(
                    cargo
                )

        elif tipo == "MEGAVIP":

            cargo = ctx.guild.get_role(
                MEGAVIP_ROLE
            )

            if cargo:

                await member.add_roles(
                    cargo
                )

        # =========================
        # CANAL VALIDADO
        # =========================

        canal = ctx.guild.get_channel(
            VALIDADOS_CHANNEL
        )

        embed = discord.Embed(
            title="✅ INSCRIÇÃO VALIDADA",
            description=(
                f"{member.mention}\n\n"
                f"🎟 **Tipo:** {tipo}\n\n"
                "Boa sorte no torneio! 🔥"
            ),
            color=discord.Color.green()
        )

        if member.display_avatar:

            embed.set_thumbnail(
                url=member.display_avatar.url
            )

        if canal:

            await canal.send(
                embed=embed
            )

        await ctx.send(
            "✅ Inscrição validada."
        )
