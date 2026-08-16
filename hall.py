import discord
from discord.ext import commands
from datetime import datetime
import sqlite3
import json

DATABASE = "database/database.db"

HALL_CHANNEL = 1461218594615459979


# =========================
# SQLITE
# =========================

def connect_db():
    return sqlite3.connect(DATABASE)


def load_hall():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, data FROM hall"
    )

    rows = cursor.fetchall()

    conn.close()

    data = {}

    for uid, hall_data in rows:

        try:
            data[uid] = json.loads(hall_data)

        except json.JSONDecodeError:
            data[uid] = []

    return data


def save_hall(data):

    conn = connect_db()
    cursor = conn.cursor()

    for uid, hall_data in data.items():

        cursor.execute(
            """
            INSERT OR REPLACE INTO hall
            (id, data)
            VALUES (?, ?)
            """,
            (
                str(uid),
                json.dumps(hall_data)
            )
        )

    conn.commit()
    conn.close()


# =========================
# SETUP
# =========================

def setup_hall(bot):

    # =========================
    # ADICIONAR REGISTRO
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def hall(
        ctx,
        member: discord.Member,
        season,
        *,
        feito
    ):

        data = load_hall()

        uid = str(member.id)

        if uid not in data:
            data[uid] = []

        registro = {

            "season": season,

            "feito": feito,

            "data": datetime.now().strftime(
                "%d/%m/%Y"
            )
        }

        data[uid].append(
            registro
        )

        save_hall(data)

        # =========================
        # EMBED
        # =========================

        embed = discord.Embed(
            title="🏆 HALL DA FAMA",
            description=(
                f"{member.mention} "
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
            name="📜 Conquista",
            value=feito,
            inline=False
        )

        embed.add_field(
            name="📅 Data",
            value=registro["data"],
            inline=True
        )

        if member.display_avatar:

            embed.set_thumbnail(
                url=member.display_avatar.url
            )

        embed.set_footer(
            text="FAL • Hall da Fama"
        )

        canal = bot.get_channel(
            HALL_CHANNEL
        )

        if canal:

            await canal.send(
                embed=embed
            )

        await ctx.send(
            "✅ Registro salvo no Hall da Fama."
        )


    # =========================
    # CONSULTAR HALL
    # =========================

    @bot.command()
    async def halldafama(
        ctx,
        member: discord.Member = None
    ):

        if member is None:
            member = ctx.author

        data = load_hall()

        uid = str(member.id)

        embed = discord.Embed(
            title=f"🏆 Hall da Fama",
            description=(
                f"Registros de "
                f"**{member.display_name}**"
            ),
            color=discord.Color.gold()
        )

        if member.display_avatar:

            embed.set_thumbnail(
                url=member.display_avatar.url
            )

        registros = data.get(
            uid,
            []
        )

        if not registros:

            embed.add_field(
                name="📜 Registros",
                value=(
                    "❌ Nenhum desempenho "
                    "registrado ainda."
                ),
                inline=False
            )

        else:

            texto = ""

            for item in registros[-15:]:

                texto += (
                    f"🏁 **{item['season']}**\n"
                    f"🏆 {item['feito']}\n"
                    f"📅 {item['data']}\n\n"
                )

            embed.add_field(
                name="📜 Conquistas",
                value=texto,
                inline=False
            )

        embed.set_footer(
            text=(
                "🧾 Registro validado "
                "pelo sistema competitivo."
            )
        )

        await ctx.send(
            embed=embed
        )
