# tournament.py

import discord
from discord import app_commands
from discord.ext import commands

import json
import os
import random


# ============================================================
# CONFIGURAÇÕES
# ============================================================

DATABASE_FOLDER = "database"
TOURNAMENT_FILE = os.path.join(
    DATABASE_FOLDER,
    "tournament.json"
)

MAX_PLAYERS = 32


# ============================================================
# BANCO DE DADOS
# ============================================================

def ensure_database():

    os.makedirs(DATABASE_FOLDER, exist_ok=True)

    if not os.path.exists(TOURNAMENT_FILE):

        data = {
            "active": False,
            "name": "",
            "max_players": MAX_PLAYERS,
            "players": [],
            "matches": [],
            "champion": None
        }

        save_tournament(data)


def load_tournament():

    ensure_database()

    try:

        with open(
            TOURNAMENT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {
            "active": False,
            "name": "",
            "max_players": MAX_PLAYERS,
            "players": [],
            "matches": [],
            "champion": None
        }


def save_tournament(data):

    os.makedirs(DATABASE_FOLDER, exist_ok=True)

    with open(
        TOURNAMENT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# EMBED
# ============================================================

def tournament_embed(data):

    players = data.get("players", [])

    max_players = data.get(
        "max_players",
        MAX_PLAYERS
    )

    name = data.get(
        "name",
        "FAL-UP Tournament"
    )

    embed = discord.Embed(
        title=f"🏆 {name}",
        description=(
            "Inscrições abertas para o torneio!\n\n"
            f"👥 **Jogadores:** "
            f"`{len(players)}/{max_players}`\n\n"
            "Clique no botão abaixo para se inscrever."
        ),
        color=discord.Color.gold()
    )

    if players:

        lista = []

        for index, user_id in enumerate(
            players,
            start=1
        ):

            lista.append(
                f"**{index}.** <@{user_id}>"
            )

        embed.add_field(
            name="👥 Inscritos",
            value="\n".join(lista),
            inline=False
        )

    else:

        embed.add_field(
            name="👥 Inscritos",
            value="Nenhum jogador inscrito.",
            inline=False
        )

    embed.set_footer(
        text="FAL-UP • Tournament System"
    )

    return embed


# ============================================================
# BOTÕES
# ============================================================

class TournamentView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    # --------------------------------------------------------
    # INSCREVER
    # --------------------------------------------------------

    @discord.ui.button(
        label="Inscrever-se",
        emoji="📝",
        style=discord.ButtonStyle.success,
        custom_id="fal_tournament_join"
    )
    async def join(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = load_tournament()

        if not data.get("active", False):

            await interaction.response.send_message(
                "❌ Não existe nenhum torneio aberto.",
                ephemeral=True
            )

            return

        players = data.get(
            "players",
            []
        )

        user_id = interaction.user.id

        if user_id in players:

            await interaction.response.send_message(
                "❌ Você já está inscrito neste torneio.",
                ephemeral=True
            )

            return

        max_players = data.get(
            "max_players",
            MAX_PLAYERS
        )

        if len(players) >= max_players:

            await interaction.response.send_message(
                "❌ O torneio está lotado.",
                ephemeral=True
            )

            return

        players.append(user_id)

        data["players"] = players

        save_tournament(data)

        try:

            await interaction.message.edit(
                embed=tournament_embed(data),
                view=TournamentView()
            )

        except Exception:

            pass

        await interaction.response.send_message(
            "✅ Você foi inscrito no torneio!",
            ephemeral=True
        )


    # --------------------------------------------------------
    # SAIR
    # --------------------------------------------------------

    @discord.ui.button(
        label="Sair",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        custom_id="fal_tournament_leave"
    )
    async def leave(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = load_tournament()

        players = data.get(
            "players",
            []
        )

        user_id = interaction.user.id

        if user_id not in players:

            await interaction.response.send_message(
                "❌ Você não está inscrito.",
                ephemeral=True
            )

            return

        players.remove(user_id)

        data["players"] = players

        save_tournament(data)

        try:

            await interaction.message.edit(
                embed=tournament_embed(data),
                view=TournamentView()
            )

        except Exception:

            pass

        await interaction.response.send_message(
            "👋 Você saiu do torneio.",
            ephemeral=True
        )


# ============================================================
# COG
# ============================================================

class Tournament(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    # ========================================================
    # /torneio criar
    # ========================================================

    @app_commands.command(
        name="torneio-criar",
        description="Cria um novo torneio."
    )
    @app_commands.describe(
        nome="Nome do torneio.",
        vagas="Quantidade máxima de jogadores."
    )
    async def criar(
        self,
        interaction: discord.Interaction,
        nome: str,
        vagas: int = MAX_PLAYERS
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "❌ Apenas administradores podem criar torneios.",
                ephemeral=True
            )

            return

        if vagas < 2:

            await interaction.response.send_message(
                "❌ O torneio precisa ter pelo menos 2 jogadores.",
                ephemeral=True
            )

            return

        if vagas > 64:

            await interaction.response.send_message(
                "❌ O limite máximo é de 64 jogadores.",
                ephemeral=True
            )

            return

        data = load_tournament()

        if data.get("active", False):

            await interaction.response.send_message(
                "❌ Já existe um torneio ativo.",
                ephemeral=True
            )

            return

        data = {
            "active": True,
            "name": nome,
            "max_players": vagas,
            "players": [],
            "matches": [],
            "champion": None
        }

        save_tournament(data)

        embed = tournament_embed(data)

        await interaction.response.send_message(
            embed=embed,
            view=TournamentView()
        )


    # ========================================================
    # /torneio cancelar
    # ========================================================

    @app_commands.command(
        name="torneio-cancelar",
        description="Cancela o torneio atual."
    )
    async def cancelar(
        self,
        interaction: discord.Interaction
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "❌ Apenas administradores podem cancelar o torneio.",
                ephemeral=True
            )

            return

        data = load_tournament()

        if not data.get("active", False):

            await interaction.response.send_message(
                "❌ Não existe nenhum torneio ativo.",
                ephemeral=True
            )

            return

        data["active"] = False

        save_tournament(data)

        await interaction.response.send_message(
            "🛑 **Torneio cancelado.**"
        )


    # ========================================================
    # /torneio status
    # ========================================================

    @app_commands.command(
        name="torneio-status",
        description="Mostra o status do torneio."
    )
    async def status(
        self,
        interaction: discord.Interaction
    ):

        data = load_tournament()

        if not data.get("active", False):

            await interaction.response.send_message(
                "❌ Não existe nenhum torneio ativo.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            embed=tournament_embed(data)
        )


    # ========================================================
    # /torneio sortear
    # ========================================================

    @app_commands.command(
        name="torneio-sortear",
        description="Sorteia os confrontos do torneio."
    )
    async def sortear(
        self,
        interaction: discord.Interaction
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "❌ Apenas administradores podem sortear os confrontos.",
                ephemeral=True
            )

            return

        data = load_tournament()

        if not data.get("active", False):

            await interaction.response.send_message(
                "❌ Não existe nenhum torneio ativo.",
                ephemeral=True
            )

            return

        players = data.get(
            "players",
            []
        )

        if len(players) < 2:

            await interaction.response.send_message(
                "❌ É necessário ter pelo menos 2 jogadores.",
                ephemeral=True
            )

            return

        random.shuffle(players)

        matches = []

        for i in range(
            0,
            len(players),
            2
        ):

            player1 = players[i]

            if i + 1 < len(players):

                player2 = players[i + 1]

            else:

                player2 = None

            matches.append({
                "player1": player1,
                "player2": player2,
                "winner": None
            })

        data["matches"] = matches

        save_tournament(data)

        embed = discord.Embed(
            title="🎲 CONFRONTOS SORTEADOS",
            description=(
                f"🏆 **{data.get('name')}**"
            ),
            color=discord.Color.gold()
        )

        for index, match in enumerate(
            matches,
            start=1
        ):

            p1 = f"<@{match['player1']}>"

            if match["player2"]:

                p2 = f"<@{match['player2']}>"


                texto = (
                    f"{p1} **VS** {p2}"
                )

            else:

                texto = (
                    f"{p1} **BYE**"
                )

            embed.add_field(
                name=f"⚔️ Partida {index}",
                value=texto,
                inline=False
            )

        await interaction.response.send_message(
            embed=embed
        )


    # ========================================================
    # /torneio encerrar
    # ========================================================

    @app_commands.command(
        name="torneio-encerrar",
        description="Encerra o torneio e define o campeão."
    )
    @app_commands.describe(
        vencedor="Jogador vencedor."
    )
    async def encerrar(
        self,
        interaction: discord.Interaction,
        vencedor: discord.Member
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "❌ Apenas administradores podem encerrar o torneio.",
                ephemeral=True
            )

            return

        data = load_tournament()

        if not data.get("active", False):

            await interaction.response.send_message(
                "❌ Não existe nenhum torneio ativo.",
                ephemeral=True
            )

            return

        data["active"] = False

        data["champion"] = vencedor.id

        save_tournament(data)

        embed = discord.Embed(
            title="🏆 TORNEIO ENCERRADO!",
            description=(
                f"Parabéns a {vencedor.mention}!\n\n"
                "👑 **CAMPEÃO DO TORNEIO**"
            ),
            color=discord.Color.gold()
        )

        embed.set_footer(
            text="FAL-UP • Tournament System"
        )

        await interaction.response.send_message(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup_tournament(bot):

    ensure_database()

    await bot.add_cog(
        Tournament(bot)
    )

    bot.add_view(
        TournamentView()
    )
