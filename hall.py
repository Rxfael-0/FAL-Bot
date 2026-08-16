import discord
from discord import app_commands
import sqlite3
from datetime import datetime
import json

DATABASE = "database/database.db"

HALL_CHANNEL = 1461218594615459979


# =========================
# SQLITE
# =========================

def connect_db():
    return sqlite3.connect(DATABASE)


def load_hall(user_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT hall
        FROM players
        WHERE user_id = ?
        """,
        (int(user_id),)
    )

    result = cursor.fetchone()

    conn.close()

    if not result:
        return []

    try:
        return json.loads(result[0] or "[]")
    except (json.JSONDecodeError, TypeError):
        return []


def save_hall(user_id, data):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
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
        """,
        (int(user_id),)
    )

    cursor.execute(
        """
        UPDATE players
        SET hall = ?
        WHERE user_id = ?
        """,
        (
            json.dumps(data, ensure_ascii=False),
            int(user_id)
        )
    )

    conn.commit()
    conn.close()


# =========================
# SETUP
# =========================

def setup_hall(bot):

    # =========================
    # ADICIONAR HALL
    # =========================

    @bot.tree.command(
        name="hall",
        description="Adiciona um registro ao Hall da Fama."
    )
    @app_commands.describe(
        membro="Jogador que receberá o registro.",
        season="Season do feito.",
        feito="Feito realizado pelo jogador."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def hall(
        interaction: discord.Interaction,
        membro: discord.Member,
        season: str,
        feito: str
    ):

        data = load_hall(
            membro.id
        )

        registro = {
            "season": season,
            "feito": feito,
            "data": datetime.now().strftime(
                "%d/%m/%Y"
            )
        }

        data.append(
            registro
        )

        save_hall(
            membro.id,
            data
        )

        embed = discord.Embed(
            title="🏆 HALL DA FAMA",
            description=(
                f"{membro.mention} "
                "teve um novo registro!"
            ),
            color=discord.Color.gold()
        )

        embed.add_field(
            name="🏁 Season",
            value=season,
            inline=True
        )

        embed.add_field(
            name="📜 Feito",
            value=feito,
            inline=False
        )

        embed.add_field(
            name="📅 Data",
            value=registro["data"],
            inline=True
        )

        embed.set_thumbnail(
            url=membro.display_avatar.url
        )

        embed.set_footer(
            text="FAL • Hall da Fama"
        )

        canal = interaction.guild.get_channel(
            HALL_CHANNEL
        )

        if canal:

            await canal.send(
                embed=embed
            )

        await interaction.response.send_message(
            "✅ Registro salvo no Hall da Fama.",
            ephemeral=True
        )


    # =========================
    # VER HALL DA FAMA
    # =========================

    @bot.tree.command(
        name="halldafama",
        description="Veja os registros do Hall da Fama de um jogador."
    )
    @app_commands.describe(
        membro="Jogador que deseja consultar."
    )
    async def halldafama(
        interaction: discord.Interaction,
        membro: discord.Member = None
    ):

        if membro is None:
            membro = interaction.user

        data = load_hall(
            membro.id
        )

        embed = discord.Embed(
            title=f"🏆 Hall da Fama — {membro.display_name}",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(
            url=membro.display_avatar.url
        )

        if not data:

            embed.description = (
                "❌ **Nenhum desempenho registrado.**\n\n"
                "📊 Este jogador ainda não possui "
                "registros no Hall da Fama."
            )

        else:

            texto = ""

            # Últimos 15 registros
            for item in data[-15:]:

                texto += (
                    f"🏁 **{item.get('season', 'N/A')}**\n"
                    f"🏆 {item.get('data', 'N/A')} ┊ "
                    f"{item.get('feito', 'N/A')}\n\n"
                )

            embed.description = texto

            embed.set_footer(
                text=(
                    f"🧾 {len(data)} registro(s) • "
                    "FAL Hall da Fama"
                )
            )

        await interaction.response.send_message(
            embed=embed
        )
