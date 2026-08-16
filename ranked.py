import discord
from discord.ext import commands
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

    @bot.command()
    async def perfil(
        ctx,
        member: discord.Member = None
    ):

        if member is None:
            member = ctx.author

        player = get_player(
            member.id
        )

        if player is None:
            return await ctx.send(
                "❌ Não foi possível encontrar o jogador."
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

        if member.display_avatar:

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

        seasonwins = player[
            "seasonwins"
        ]

        if seasonwins:

            texto_seasons = "\n".join(
                f"🏁 {season}"
                for season in seasonwins[-10:]
            )

        else:

            texto_seasons = (
                "Nenhuma season vencida."
            )

        embed.add_field(
            name="🏁 Seasons",
            value=texto_seasons,
            inline=False
        )

        embed.set_footer(
            text="FAL • Ranked System"
        )

        await ctx.send(
            embed=embed
        )


    # =========================
    # ADICIONAR TROFÉUS
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def addtrofeus(
        ctx,
        member: discord.Member,
        quantidade: int
    ):

        player = get_player(
            member.id
        )

        player["trofeus"] += quantidade

        save_player(
            member.id,
            player
        )

        await ctx.send(
            f"🏆 {member.mention} recebeu "
            f"**{quantidade} troféus**."
        )


    # =========================
    # REMOVER TROFÉUS
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def removetrofeus(
        ctx,
        member: discord.Member,
        quantidade: int
    ):

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

        await ctx.send(
            f"🏆 Foram removidos "
            f"**{quantidade} troféus** de "
            f"{member.mention}."
        )


    # =========================
    # WIN
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def win(
        ctx,
        member: discord.Member
    ):

        player = get_player(
            member.id
        )

        player["wins"] += 1

        save_player(
            member.id,
            player
        )

        await ctx.send(
            f"🥇 Vitória registrada para "
            f"{member.mention}."
        )


    # =========================
    # LOSS
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def loss(
        ctx,
        member: discord.Member
    ):

        player = get_player(
            member.id
        )

        player["losses"] += 1

        save_player(
            member.id,
            player
        )

        await ctx.send(
            f"❌ Derrota registrada para "
            f"{member.mention}."
        )


    # =========================
    # ADICIONAR MEDALHA
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def add(
        ctx,
        member: discord.Member,
        medalha
    ):

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

            return await ctx.send(
                "❌ Este jogador já possui "
                "essa medalha."
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

        await ctx.send(
            f"✅ {member.mention} recebeu "
            f"a medalha {display}."
        )


    # =========================
    # REMOVER MEDALHA
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def removemedal(
        ctx,
        member: discord.Member,
        medalha
    ):

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

            return await ctx.send(
                "❌ Este jogador não possui "
                "essa medalha."
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

        await ctx.send(
            f"✅ Medalha removida de "
            f"{member.mention}."
        )


    # =========================
    # SEASON WIN
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def seasonwin(
        ctx,
        member: discord.Member,
        *,
        season
    ):

        player = get_player(
            member.id
        )

        if season in player["seasonwins"]:

            return await ctx.send(
                "❌ Esta season já está "
                "registrada."
            )

        player["seasonwins"].append(
            season
        )

        save_player(
            member.id,
            player
        )

        await ctx.send(
            f"🏆 {member.mention} venceu "
            f"a **{season}**!"
        )


    # =========================
    # PARTIDA
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def partida(
        ctx,
        vencedor: discord.Member,
        perdedor: discord.Member
    ):

        winner = get_player(
            vencedor.id
        )

        loser = get_player(
            perdedor.id
        )

        winner["wins"] += 1
        loser["losses"] += 1

        winner["partidas"].append({
            "resultado": "win",
            "adversario": perdedor.id,
            "data": datetime.now().strftime(
                "%d/%m/%Y"
            )
        })

        loser["partidas"].append({
            "resultado": "loss",
            "adversario": vencedor.id,
            "data": datetime.now().strftime(
                "%d/%m/%Y"
            )
        })

        save_player(
            vencedor.id,
            winner
        )

        save_player(
            perdedor.id,
            loser
        )

        await ctx.send(
            (
                f"🏆 Vitória: {vencedor.mention}\n"
                f"❌ Derrota: {perdedor.mention}"
            )
        )


    # =========================
    # PARTIDAS
    # =========================

    @bot.command()
    async def partidas(
        ctx,
        member: discord.Member = None
    ):

        if member is None:
            member = ctx.author

        player = get_player(
            member.id
        )

        registros = player[
            "partidas"
        ][-15:]

        embed = discord.Embed(
            title=(
                f"🎮 Partidas — "
                f"{member.display_name}"
            ),
            color=discord.Color.blurple()
        )

        if not registros:

            embed.description = (
                "❌ Nenhuma partida registrada."
            )

        else:

            texto = ""

            for partida_data in registros:

                if partida_data[
                    "resultado"
                ] == "win":

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

        await ctx.send(
            embed=embed
        )


    # =========================
    # LEADERBOARD
    # =========================

    @bot.command()
    async def leaderboard(ctx):

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

        await ctx.send(
            embed=embed
        )


    # =========================
    # TOP
    # =========================

    @bot.command()
    async def top(ctx):

        await leaderboard.callback(
            ctx
        )
