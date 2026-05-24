import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import json

REGISTRO_CHANNEL = 1463346916120068106
LOGS_CHANNEL = 1463389943995830445
VALIDADOS_CHANNEL = 1508246884442050690

VIP_ROLE = 1460867416081825904
MEGAVIP_ROLE = 1460867926948057202

MAX_VAGAS = 32

INSCRICOES = "database/tournament.json"

def load_data():

    try:

        with open(INSCRICOES, "r") as f:

            return json.load(f)

    except:

        return {}

def save_data(data):

    with open(INSCRICOES, "w") as f:

        json.dump(data, f, indent=4)

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

        data = load_data()

        if str(interaction.user.id) in data:

            return await interaction.response.send_message(
                "❌ Você já está inscrito.",
                ephemeral=True
            )

        if len(data) >= MAX_VAGAS:

            return await interaction.response.send_message(
                "❌ Todas vagas foram preenchidas.",
                ephemeral=True
            )

        data[str(interaction.user.id)] = {

            "tipo": "NORMAL",
            "nome": self.nome.value,
            "roblox": self.roblox.value,
            "convidado": self.convidado.value,
            "validado": False
        }

        save_data(data)

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

        data = load_data()

        if str(interaction.user.id) in data:

            return await interaction.response.send_message(
                "❌ Você já está inscrito.",
                ephemeral=True
            )

        if len(data) >= MAX_VAGAS:

            return await interaction.response.send_message(
                "❌ Todas vagas foram preenchidas.",
                ephemeral=True
            )

        data[str(interaction.user.id)] = {

            "tipo": self.tipo,
            "nome": self.nome.value,
            "roblox": self.roblox.value,
            "validado": False
        }

        save_data(data)

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

                f"🎮 Vagas disponíveis: {MAX_VAGAS}\n\n"

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

        data = load_data()

        if str(member.id) not in data:

            return await ctx.send(
                "❌ Usuário não encontrado."
            )

        data[str(member.id)]["validado"] = True

        tipo = data[str(member.id)]["tipo"]

        save_data(data)

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
