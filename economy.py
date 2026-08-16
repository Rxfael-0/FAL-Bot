import discord
from discord.ext import commands, tasks
import sqlite3
import json

DATABASE = "database/database.db"

VIP = 1460867416081825904
MEGAVIP = 1460867926948057202


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


def get_coins(uid):

    create_player(uid)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT coins FROM players WHERE user_id = ?",
        (int(uid),)
    )

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return 0

    return result[0]


def add_coins(uid, quantidade):

    create_player(uid)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players

    SET coins = coins + ?

    WHERE user_id = ?
    """, (
        quantidade,
        int(uid)
    ))

    conn.commit()
    conn.close()


# =========================
# SETUP
# =========================

def setup_economy(bot):

    @bot.command()
    async def moedas(
        ctx,
        member: discord.Member = None
    ):

        if member is None:
            member = ctx.author

        coins = get_coins(
            member.id
        )

        embed = discord.Embed(
            title="🪙 Coins",
            description=(
                f"{member.mention} possui "
                f"**{coins}🪙**"
            ),
            color=discord.Color.gold()
        )

        await ctx.send(
            embed=embed
        )


    # =========================
    # ADD COIN
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def addcoin(
        ctx,
        quantidade: int,
        member: discord.Member
    ):

        if quantidade <= 0:

            return await ctx.send(
                "❌ A quantidade precisa ser maior que 0."
            )

        add_coins(
            member.id,
            quantidade
        )

        embed = discord.Embed(
            title="🪙 Coins adicionadas",
            description=(
                f"{member.mention} recebeu "
                f"**+{quantidade}🪙**"
            ),
            color=discord.Color.green()
        )

        await ctx.send(
            embed=embed
        )


    # =========================
    # PRICES
    # =========================

    @bot.command()
    async def prices(ctx):

        embed = discord.Embed(
            title="💸 Tabela Coins",
            color=discord.Color.gold()
        )

        embed.description = (

            "💰 **ROBUX → MOEDAS**\n\n"

            "50 Robux ➜ 20🪙\n"
            "100 Robux ➜ 50🪙\n"
            "150 Robux ➜ 85🪙\n"
            "200 Robux ➜ 120🪙\n"
            "300 Robux ➜ 190🪙\n"
            "400 Robux ➜ 260🪙\n"
            "600 Robux ➜ 420🪙\n"
            "800 Robux ➜ 600🪙\n\n"

            "💵 **PIX → MOEDAS**\n\n"

            "R$2 ➜ 50🪙\n"
            "R$5 ➜ 140🪙\n"
            "R$10 ➜ 320🪙\n"
            "R$15 ➜ 520🪙\n"
            "R$20 ➜ 760🪙\n"
            "R$30 ➜ 1200🪙\n"
            "R$40 ➜ 1700🪙\n"
            "R$50 ➜ 2300🪙\n\n"

            "✨ PIX possui melhor custo benefício."
        )

        await ctx.send(
            embed=embed
        )


    # =========================
    # MENSAL MANUAL
    # =========================

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def mensal(ctx):

        conn = connect_db()
        cursor = conn.cursor()

        entregues = 0

        for member in ctx.guild.members:

            if member.bot:
                continue

            create_player(
                member.id
            )

            if discord.utils.get(
                member.roles,
                id=MEGAVIP
            ):

                cursor.execute("""
                UPDATE players
                SET coins = coins + 20
                WHERE user_id = ?
                """, (member.id,))

                entregues += 20

            elif discord.utils.get(
                member.roles,
                id=VIP
            ):

                cursor.execute("""
                UPDATE players
                SET coins = coins + 4
                WHERE user_id = ?
                """, (member.id,))

                entregues += 4

        conn.commit()
        conn.close()

        await ctx.send(
            f"✅ Coins mensais entregues.\n"
            f"🪙 Total distribuído: {entregues}"
        )


# =========================
# MENSAL AUTOMÁTICO
# =========================

@tasks.loop(hours=720)
async def mensal_auto(bot):

    if not bot.guilds:
        return

    guild = bot.guilds[0]

    conn = connect_db()
    cursor = conn.cursor()

    entregues = 0

    for member in guild.members:

        if member.bot:
            continue

        create_player(
            member.id
        )

        if discord.utils.get(
            member.roles,
            id=MEGAVIP
        ):

            cursor.execute("""
            UPDATE players
            SET coins = coins + 20
            WHERE user_id = ?
            """, (member.id,))

            entregues += 20

        elif discord.utils.get(
            member.roles,
            id=VIP
        ):

            cursor.execute("""
            UPDATE players
            SET coins = coins + 4
            WHERE user_id = ?
            """, (member.id,))

            entregues += 4

    conn.commit()
    conn.close()

    print(
        f"💎 Coins mensais entregues: {entregues}"
    )
