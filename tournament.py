# tournament.py

import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import random
import json


DATABASE = "database/database.db"

MAX_PLAYERS = 32


# ============================================================
# SQLITE
# ============================================================

def connect_db():
    return sqlite3.connect(DATABASE)


def setup_tournament_database():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournament (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        active INTEGER DEFAULT 0,
        name TEXT DEFAULT '',
        max_players INTEGER DEFAULT 32,
        players TEXT DEFAULT '[]',
        matches TEXT DEFAULT '[]',
        champion INTEGER
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO tournament (
        id,
        active,
        name,
        max_players,
        players,
        matches,
        champion
    )
    VALUES (
        1,
        0,
        '',
        32,
        '[]',
        '[]',
        NULL
    )
    """)

    conn.commit()
    conn.close()


def load_tournament():

    setup_tournament_database()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        active,
        name,
        max_players,
        players,
        matches,
        champion
    FROM tournament
    WHERE id = 1
    """)

    data = cursor.fetchone()

    conn.close()

    if not data:

        return {
            "active": False,
            "name": "",
            "max_players": MAX_PLAYERS,
            "players": [],
            "matches": [],
            "champion": None
        }

    return {
        "active": bool(data[0]),
        "name": data[1],
        "max_players": data[2],
        "players": json.loads(data[3]),
        "matches": json.loads(data[4]),
        "champion": data[5]
    }


def save_tournament(data):

    setup_tournament_database()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE tournament
    SET
        active = ?,
        name = ?,
        max_players = ?,
        players = ?,
        matches = ?,
        champion = ?
    WHERE id = 1
    """, (
        1 if data.get("active") else 0,
        data.get("name", ""),
        data.get("max_players", MAX_PLAYERS),
        json.dumps(data.get("players", [])),
        json.dumps(data.get("matches", [])),
        data.get("champion")
    ))

    conn.commit()
    conn.close()


# ============================================================
# EMBED
# ============================================================

def tournament_embed(data):

    players = data.get(
        "players",
        []
    )

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
            "Clique nos botões abaixo para participar."
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


    # ========================================================
    # INSCREVER
    # ========================================================

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

            return await interaction.response.send_message(
                "❌ Não existe nenhum torneio aberto.",
                ephemeral=True
            )

        players = data.get(
            "players",
            []
        )

        user_id = interaction.user.id

        if user_id in players:

            return await interaction.response.send_message(
                "❌ Você já está inscrito neste torneio.",
                ephemeral=True
            )

        max_players = data.get(
            "max_players",
            MAX_PLAYERS
        )

        if len(players) >= max_players:

            return await interaction.response.send_message(
                "❌ O torneio está lotado.",
                ephemeral=True
            )

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


    # ========================================================
    # SAIR
    # ========================================================

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

            return await interaction.response.send_message(
                "❌ Você não está inscrito.",
                ephemeral=True
            )

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
    # /torneio-criar
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

            return await interaction.response.send_message(
                "❌ Apenas administradores podem criar torneios.",
                ephemeral=True
            )

        if vagas < 2:

            return await interaction.response.send_message(
                "❌ O torneio precisa ter pelo menos 2 jogadores.",
                ephemeral=True
            )

        if vagas > 64:

            return await interaction.response.send_message(
                "❌ O limite máximo é de 64 jogadores.",
                ephemeral=True
            )

        data = load_tournament()

        if data.get("active", False):

            return await interaction.response.send_message(
                "❌ Já existe um torneio ativo.",
                ephemeral=True
            )

        data = {
            "active": True,
            "name": nome,
            "max_players": vagas,
            "players": [],
            "matches": [],
            "champion": None
        }

        save_tournament(data)

        await interaction.response.send_message(
            embed=tournament_embed(data),
            view=TournamentView()
        )


    # ========================================================
    # /torneio-cancelar
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

            return await interaction.response.send_message(
                "❌ Apenas administradores podem cancelar o torneio.",
                ephemeral=True
            )

        data = load_tournament()

        if not data.get("active", False):

            return await interaction.response.send_message(
                "❌ Não existe nenhum torneio ativo.",
                ephemeral=True
            )

        data["active"] = False

        save_tournament(data)

        await interaction.response.send_message(
            "🛑 **Torneio cancelado.**"
        )


    # ========================================================
    # /torneio-status
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

            return await interaction.response.send_message(
                "❌ Não existe nenhum torneio ativo.",
                ephemeral=True
            )

        await interaction.response.send_message(
            embed=tournament_embed(data)
        )


    # ========================================================
    # /torneio-sortear
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

            return await interaction.response.send_message(
                "❌ Apenas administradores podem sortear os confrontos.",
                ephemeral=True
            )

        data = load_tournament()

        if not data.get("active", False):

            return await interaction.response.send_message(
                "❌ Não existe nenhum torneio ativo.",
                ephemeral=True
            )

        players = data.get(
            "players",
            []
        )

        if len(players) < 2:

            return await interaction.response.send_message(
                "❌ É necessário ter pelo menos 2 jogadores.",
                ephemeral=True
            )

        players = players.copy()

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
    # /torneio-encerrar
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

            return await interaction.response.send_message(
                "❌ Apenas administradores podem encerrar os torneios.",
                ephemeral=True
            )

        data = load_tournament()

        if not data.get("active", False):

            return await interaction.response.send_message(
                "❌ Não existe nenhum torneio ativo.",
                ephemeral=True
            )

        if vencedor.id not in data.get("players", []):

            return await interaction.response.send_message(
                "❌ Esse jogador não está inscrito no torneio.",
                ephemeral=True
            )

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

    setup_tournament_database()

    await bot.add_cog(
        Tournament(bot)
    )

    bot.add_view(
        TournamentView()
    )
