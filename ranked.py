import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import json
from datetime import datetime

DATABASE = "database/database.db"


# =========================
# SQLITE
# =========================

def connect_db():
    return sqlite3.connect(DATABASE)


def create_player(uid):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO players (
        user_id,
        trofeus,
        medalhas,
        coins,
        wins,
        losses,
        shop_week,
        seasonwins,
        medals,
        hall,
        partidas
    )
    VALUES (
        ?, 0, 0, 0, 0, 0, 0,
        '[]', '[]', '[]', '[]'
    )
    """, (int(uid),))

    conn.commit()
    conn.close()


def get_player(uid):

    create_player(uid)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        user_id,
        trofeus,
        medalhas,
        coins,
        wins,
        losses,
        shop_week,
        seasonwins,
        medals,
        hall,
        partidas

    FROM players

    WHERE user_id = ?
    """, (int(uid),))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "user_id": row[0],
        "trofeus": row[1],
        "medalhas": row[2],
        "coins": row[3],
        "wins": row[4],
        "losses": row[5],
        "shop_week": row[6],
        "seasonwins": json.loads(row[7] or "[]"),
        "medals": json.loads(row[8] or "[]"),
        "hall": json.loads(row[9] or "[]"),
        "partidas": json.loads(row[10] or "[]")
    }


def save_player(uid, player):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players

    SET
        trofeus = ?,
        medalhas = ?,
        coins = ?,
        wins = ?,
        losses = ?,
        shop_week = ?,
        seasonwins = ?,
        medals = ?,
        hall = ?,
        partidas = ?

    WHERE user_id = ?
    """, (
        player["trofeus"],
        player["medalhas"],
        player["coins"],
        player["wins"],
        player["losses"],
        player["shop_week"],
        json.dumps(player["seasonwins"]),
        json.dumps(player["medals"]),
        json.dumps(player["hall"]),
        json.dumps(player["partidas"]),
        int(uid)
    ))

    conn.commit()
    conn.close()


# =========================
# MEDALHAS
# =========================

MEDALS = {

    "1st": {
        "emoji": "🥇",
        "nome": "1st Place"
    },

    "2nd": {
        "emoji": "🥈",
        "nome": "2nd Place"
    },

    "3rd": {
        "emoji": "🥉",
        "nome": "3rd Place"
    },

    "champion": {
        "emoji": "🏆",
        "nome": "Champion"
    },

    "mvp": {
        "emoji": "⭐",
        "nome": "MVP"
    },

    "weekly": {
        "emoji": "🔥",
        "nome": "Weekly Winner"
    }
}


def format_medals(medals):

    if not medals:
        return "Nenhuma medalha conquistada ainda."

    linhas = []

    for medal in medals:

        medal_key = str(medal).lower()

        if medal_key in MEDALS:

            info = MEDALS[medal_key]

            linhas.append(
                f"{info['emoji']} **{info['nome']}**"
            )

        else:

            linhas.append(
                f"🏅 **{medal}**"
            )

    return "\n".join(linhas)


# =========================
# SETUP
# =========================

def setup_ranked(bot):

    # =========================
    # PERFIL
    # =========================

    @bot.tree.command(
        name="perfil",
        description="Veja o perfil Ranked de um jogador."
    )
    @app_commands.describe(
        member="Jogador que deseja consultar."
    )
    async def perfil(
        interaction: discord.Interaction,
        member: discord.Member = None
    ):

        if member is None:
            member = interaction.user

        player = get_player(
            member.id
        )

        if player is None:

            return await interaction.response.send_message(
                "❌ Não foi possível encontrar o jogador.",
                ephemeral=True
            )

        wins = player["wins"]
        losses = player["losses"]

        total_partidas = wins + losses

        if total_partidas > 0:

            winrate = (
                wins / total_partidas
            ) * 100

        else:

            winrate = 0

        embed = discord.Embed(
            title=f"🏆 Perfil — {member.display_name}",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        # =========================
        # RANKED
        # =========================

        embed.add_field(
            name="🏅 Ranked",
            value=(
                f"🏆 Troféus: **{player['trofeus']}**\n"
                f"🥇 Vitórias: **{wins}**\n"
                f"❌ Derrotas: **{losses}**\n"
                f"📊 Winrate: **{winrate:.1f}%**"
            ),
            inline=False
        )

        # =========================
        # ECONOMIA
        # =========================

        embed.add_field(
            name="🪙 Economia",
            value=(
                f"🪙 Coins: **{player['coins']}**"
            ),
            inline=True
        )

        # =========================
        # COLEÇÃO
        # =========================

        colecao = format_medals(
            player["medals"]
        )

        embed.add_field(
            name="🏅 COLEÇÃO DE MEDALHAS",
            value=colecao,
            inline=False
        )

        # =========================
        # SEASONS
        # =========================

        seasonwins = player["seasonwins"]

        if seasonwins:

            texto_seasons = "\n".join(
                f"🏁 {season}"
                for season in seasonwins[-10:]
            )

        else:

            texto_seasons = "Nenhuma season vencida."

        embed.add_field(
            name="🏁 Seasons",
            value=texto_seasons,
            inline=False
        )

        embed.set_footer(
            text="FAL • Ranked System"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # ADICIONAR TROFÉUS
    # =========================

    @bot.tree.command(
        name="addtrofeus",
        description="Adiciona troféus a um jogador."
    )
    @app_commands.describe(
        member="Jogador que receberá os troféus.",
        quantidade="Quantidade de troféus."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def addtrofeus(
        interaction: discord.Interaction,
        member: discord.Member,
        quantidade: int
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando.",
                ephemeral=True
            )

        if quantidade <= 0:

            return await interaction.response.send_message(
                "❌ A quantidade precisa ser maior que 0.",
                ephemeral=True
            )

        player = get_player(
            member.id
        )

        player["trofeus"] += quantidade

        save_player(
            member.id,
            player
        )

        await interaction.response.send_message(
            f"🏆 {member.mention} recebeu "
            f"**{quantidade} troféus**."
        )


    # =========================
    # REMOVER TROFÉUS
    # =========================

    @bot.tree.command(
        name="removetrofeus",
        description="Remove troféus de um jogador."
    )
    @app_commands.describe(
        member="Jogador que perderá os troféus.",
        quantidade="Quantidade de troféus."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def removetrofeus(
        interaction: discord.Interaction,
        member: discord.Member,
        quantidade: int
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando.",
                ephemeral=True
            )

        if quantidade <= 0:

            return await interaction.response.send_message(
                "❌ A quantidade precisa ser maior que 0.",
                ephemeral=True
            )

        player = get_player(
            member.id
        )

        player["trofeus"] = max(
            0,
            player["trofeus"] - quantidade
        )

        save_player(
            member.id,
            player
        )

        await interaction.response.send_message(
            f"🏆 Foram removidos "
            f"**{quantidade} troféus** de "
            f"{member.mention}."
        )


    # =========================
    # WIN
    # =========================

    @bot.tree.command(
        name="win",
        description="Registra uma vitória para um jogador."
    )
    @app_commands.describe(
        member="Jogador que venceu."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def win(
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando.",
                ephemeral=True
            )

        player = get_player(
            member.id
        )

        player["wins"] += 1

        save_player(
            member.id,
            player
        )

        await interaction.response.send_message(
            f"🥇 Vitória registrada para "
            f"{member.mention}."
        )


    # =========================
    # LOSS
    # =========================

    @bot.tree.command(
        name="loss",
        description="Registra uma derrota para um jogador."
    )
    @app_commands.describe(
        member="Jogador que perdeu."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def loss(
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando.",
                ephemeral=True
            )

        player = get_player(
            member.id
        )

        player["losses"] += 1

        save_player(
            member.id,
            player
        )

        await interaction.response.send_message(
            f"❌ Derrota registrada para "
            f"{member.mention}."
        )


    # =========================
    # ADICIONAR MEDALHA
    # =========================

    @bot.tree.command(
        name="addmedal",
        description="Adiciona uma medalha a um jogador."
    )
    @app_commands.describe(
        member="Jogador que receberá a medalha.",
        medalha="Nome ou tipo da medalha."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def addmedal(
        interaction: discord.Interaction,
        member: discord.Member,
        medalha: str
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando.",
                ephemeral=True
            )

        player = get_player(
            member.id
        )

        medalha = medalha.lower()

        if medalha in MEDALS:

            medal = MEDALS[
                medalha
            ]["nome"]

        else:

            medal = medalha

        if medal in player["medals"]:

            return await interaction.response.send_message(
                "❌ Este jogador já possui essa medalha.",
                ephemeral=True
            )

        player["medals"].append(
            medal
        )

        player["medalhas"] = len(
            player["medals"]
        )

        save_player(
            member.id,
            player
        )

        info = MEDALS.get(
            medalha
        )

        if info:

            display = (
                f"{info['emoji']} "
                f"**{info['nome']}**"
            )

        else:

            display = (
                f"🏅 **{medal}**"
            )

        await interaction.response.send_message(
            f"✅ {member.mention} recebeu "
            f"a medalha {display}."
        )


    # =========================
    # REMOVER MEDALHA
    # =========================

    @bot.tree.command(
        name="removemedal",
        description="Remove uma medalha de um jogador."
    )
    @app_commands.describe(
        member="Jogador que perderá a medalha.",
        medalha="Nome ou tipo da medalha."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def removemedal(
        interaction: discord.Interaction,
        member: discord.Member,
        medalha: str
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando.",
                ephemeral=True
            )

        player = get_player(
            member.id
        )

        medalha = medalha.lower()

        if medalha in MEDALS:

            medal = MEDALS[
                medalha
            ]["nome"]

        else:

            medal = medalha

        if medal not in player["medals"]:

            return await interaction.response.send_message(
                "❌ Este jogador não possui essa medalha.",
                ephemeral=True
            )

        player["medals"].remove(
            medal
        )

        player["medalhas"] = len(
            player["medals"]
        )

        save_player(
            member.id,
            player
        )

        await interaction.response.send_message(
            f"✅ Medalha removida de "
            f"{member.mention}."
        )


    # =========================
    # SEASON WIN
    # =========================

    @bot.tree.command(
        name="seasonwin",
        description="Registra uma season vencida por um jogador."
    )
    @app_commands.describe(
        member="Jogador que venceu a season.",
        season="Nome da season."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def seasonwin(
        interaction: discord.Interaction,
        member: discord.Member,
        season: str
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando.",
                ephemeral=True
            )

        player = get_player(
            member.id
        )

        if season in player["seasonwins"]:

            return await interaction.response.send_message(
                "❌ Esta season já está registrada.",
                ephemeral=True
            )

        player["seasonwins"].append(
            season
        )

        save_player(
            member.id,
            player
        )

        await interaction.response.send_message(
            f"🏆 {member.mention} venceu "
            f"a **{season}**!"
        )


    # =========================
    # PARTIDA
    # =========================

    @bot.tree.command(
        name="partida",
        description="Registra uma partida entre dois jogadores."
    )
    @app_commands.describe(
        vencedor="Jogador vencedor.",
        perdedor="Jogador perdedor."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def partida(
        interaction: discord.Interaction,
        vencedor: discord.Member,
        perdedor: discord.Member
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando.",
                ephemeral=True
            )

        if vencedor.id == perdedor.id:

            return await interaction.response.send_message(
                "❌ O vencedor e o perdedor não podem ser a mesma pessoa.",
                ephemeral=True
            )

        winner = get_player(
            vencedor.id
        )

        loser = get_player(
            perdedor.id
        )

        winner["wins"] += 1
        loser["losses"] += 1

        data = datetime.now().strftime(
            "%d/%m/%Y"
        )

        winner["partidas"].append({
            "resultado": "win",
            "adversario": perdedor.id,
            "data": data
        })

        loser["partidas"].append({
            "resultado": "loss",
            "adversario": vencedor.id,
            "data": data
        })

        save_player(
            vencedor.id,
            winner
        )

        save_player(
            perdedor.id,
            loser
        )

        await interaction.response.send_message(
            (
                f"🏆 Vitória: {vencedor.mention}\n"
                f"❌ Derrota: {perdedor.mention}"
            )
        )


    # =========================
    # PARTIDAS
    # =========================

    @bot.tree.command(
        name="partidas",
        description="Veja o histórico de partidas de um jogador."
    )
    @app_commands.describe(
        member="Jogador que deseja consultar."
    )
    async def partidas(
        interaction: discord.Interaction,
        member: discord.Member = None
    ):

        if member is None:
            member = interaction.user

        player = get_player(
            member.id
        )

        registros = player["partidas"][-15:]

        embed = discord.Embed(
            title=(
                f"🎮 Partidas — "
                f"{member.display_name}"
            ),
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        if not registros:

            embed.description = (
                "❌ Nenhuma partida registrada."
            )

        else:

            texto = ""

            for partida_data in registros:

                if partida_data["resultado"] == "win":

                    emoji = "🟢"

                else:

                    emoji = "🔴"

                texto += (
                    f"{emoji} "
                    f"**{partida_data['resultado'].upper()}** "
                    f"• <@{partida_data['adversario']}> "
                    f"• {partida_data['data']}\n"
                )

            embed.description = texto

        embed.set_footer(
            text="FAL • Ranked"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # LEADERBOARD
    # =========================

    @bot.tree.command(
        name="leaderboard",
        description="Veja o ranking dos jogadores por troféus."
    )
    async def leaderboard(
        interaction: discord.Interaction
    ):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT user_id, trofeus
        FROM players
        ORDER BY trofeus DESC
        LIMIT 15
        """)

        rows = cursor.fetchall()

        conn.close()

        embed = discord.Embed(
            title="🏆 LEADERBOARD",
            color=discord.Color.gold()
        )

        if not rows:

            embed.description = (
                "❌ Nenhum jogador registrado."
            )

        else:

            texto = ""

            for index, row in enumerate(
                rows,
                start=1
            ):

                uid = row[0]
                trofeus = row[1]

                if index == 1:

                    posicao = "🥇"

                elif index == 2:

                    posicao = "🥈"

                elif index == 3:

                    posicao = "🥉"

                else:

                    posicao = f"**{index}.**"

                texto += (
                    f"{posicao} <@{uid}> "
                    f"— 🏆 **{trofeus}**\n"
                )

            embed.description = texto

        embed.set_footer(
            text="FAL • Ranked"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # TOP
    # =========================

    @bot.tree.command(
        name="top",
        description="Veja o Top 15 do Ranked."
    )
    async def top(
        interaction: discord.Interaction
    ):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT user_id, trofeus
        FROM players
        ORDER BY trofeus DESC
        LIMIT 15
        """)

        rows = cursor.fetchall()

        conn.close()

        embed = discord.Embed(
            title="🏆 TOP 15 — FAL RANKED",
            color=discord.Color.gold()
        )

        if not rows:

            embed.description = (
                "❌ Nenhum jogador registrado."
            )

        else:

            texto = ""

            for index, row in enumerate(
                rows,
                start=1
            ):

                uid = row[0]
                trofeus = row[1]

                if index == 1:

                    posicao = "🥇"

                elif index == 2:

                    posicao = "🥈"

                elif index == 3:

                    posicao = "🥉"

                else:

                    posicao = f"**{index}.**"

                texto += (
                    f"{posicao} <@{uid}> "
                    f"— 🏆 **{trofeus}**\n"
                )

            embed.description = texto

        embed.set_footer(
            text="FAL • Ranked System"
        )

        await interaction.response.send_message(
            embed=embed
        )
