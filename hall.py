import discord
from discord.ext import commands
from datetime import datetime
import sqlite3
import json

conn = sqlite3.connect("database/database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS hall (
    id TEXT PRIMARY KEY,
    data TEXT
)
""")

conn.commit()

HALL_CHANNEL = 1461218594615459979

def load_hall():

    cursor.execute(
        "SELECT id, data FROM hall"
    )

    rows = cursor.fetchall()

    data = {}

    for uid, hall_data in rows:

        data[uid] = json.loads(hall_data)

    return data

def save_hall(data):

    cursor.execute(
        "DELETE FROM hall"
    )

    for uid, hall_data in data.items():

        cursor.execute(
            "INSERT INTO hall (id, data) VALUES (?, ?)",
            (
                uid,
                json.dumps(hall_data)
            )
        )

    conn.commit()

def setup_hall(bot):

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

        if str(member.id) not in data:

            data[str(member.id)] = []

        registro = {

            "season": season,
            "feito": feito,
            "data": datetime.now().strftime(
                "%d/%m/%Y"
            )
        }

        data[
            str(member.id)
        ].append(registro)

        save_hall(data)

        embed = discord.Embed(
            title="🏆 HALL DA FAMA",
            description=(
                f"{member.mention} "
                f"teve um novo registro."
            ),
            color=discord.Color.gold()
        )

        embed.add_field(
            name="🏁 Season",
            value=season
        )

        embed.add_field(
            name="📜 Feito",
            value=feito,
            inline=False
        )

        canal = bot.get_channel(
            HALL_CHANNEL
        )

        if canal:

            await canal.send(
                embed=embed
            )

        await ctx.send(
            "✅ Registro salvo."
        )

    @bot.command()
    async def halldafama(
        ctx,
        member: discord.Member=None
    ):

        if member is None:
            member = ctx.author

        data = load_hall()

        embed = discord.Embed(
            title=(
                f"🏆 Hall da Fama "
                f"{member.name}"
            ),
            color=discord.Color.gold()
        )

        texto = ""

        if str(member.id) in data:

            for item in data[
                str(member.id)
            ][-15:]:

                texto += (
                    f"🏁 {item['season']}\n"
                    f"🏆 {item['data']} ┊ "
                    f"{item['feito']}\n\n"
                )

        if texto == "":

            texto = (
                "❌ Nenhum desempenho "
                "registrado.\n"
                "📊 Este jogador ainda "
                "não possui registros."
            )

        embed.description = texto

        embed.set_footer(
            text=(
                "🧾 Registro validado "
                "pelo sistema competitivo."
            )
        )

        await ctx.send(embed=embed)
