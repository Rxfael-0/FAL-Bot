import discord
from discord.ext import commands, tasks
import sqlite3

conn = sqlite3.connect("database/database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    data TEXT
)
""")

conn.commit()

VIP = 1460867416081825904
MEGAVIP = 1460867926948057202

def load_players():

    cursor.execute(
        "SELECT id, data FROM players"
    )

    rows = cursor.fetchall()

    data = {}

    for uid, player_data in rows:

        data[uid] = json.loads(player_data)

    return data

def save_players(data):

    cursor.execute(
        "DELETE FROM players"
    )

    for uid, player_data in data.items():

        cursor.execute(
            "INSERT INTO players (id, data) VALUES (?, ?)",
            (
                uid,
                json.dumps(player_data)
            )
        )

    conn.commit()

def create_player(data, uid):

    if str(uid) not in data:

        data[str(uid)] = {

            "trofeus": 0,
            "medalhas": 0,
            "coins": 0,
            "wins": 0,
            "losses": 0,
            "seasonwins": [],
            "medals": [],
            "hall": [],
            "partidas": []
        }

def setup_economy(bot):

    @bot.command()
    async def moedas(
        ctx,
        member: discord.Member=None
    ):

        if member is None:
            member = ctx.author

        data = load_players()

        create_player(
            data,
            member.id
        )

        embed = discord.Embed(
            title="🪙 Coins",
            description=(
                f"{member.mention} "
                f"possui "
                f"{data[str(member.id)]['coins']}🪙"
            ),
            color=discord.Color.gold()
        )

        await ctx.send(embed=embed)

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def addcoin(
        ctx,
        quantidade: int,
        member: discord.Member
    ):

        data = load_players()

        create_player(
            data,
            member.id
        )

        data[
            str(member.id)
        ]["coins"] += quantidade

        save_players(data)

        embed = discord.Embed(
            title="🪙 Coins adicionadas",
            description=(
                f"{member.mention} "
                f"recebeu "
                f"+{quantidade}🪙"
            ),
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

    @bot.command()
    async def prices(ctx):

        embed = discord.Embed(
            title="💸 Tabela Coins",
            color=discord.Color.gold()
        )

        embed.description = (

    "💰 ROBUX → MOEDAS\n\n"

    "50 Robux ➜ 20🪙\n"
    "100 Robux ➜ 50🪙\n"
    "150 Robux ➜ 85🪙\n"
    "200 Robux ➜ 120🪙\n"
    "300 Robux ➜ 190🪙\n"
    "400 Robux ➜ 260🪙\n"
    "600 Robux ➜ 420🪙\n"
    "800 Robux ➜ 600🪙\n\n"

    "💵 PIX → MOEDAS\n\n"

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

        await ctx.send(embed=embed)

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def mensal(ctx):

        data = load_players()

        for member in ctx.guild.members:

            create_player(
                data,
                member.id
            )

            if discord.utils.get(
                member.roles,
                id=MEGAVIP
            ):

                data[
                    str(member.id)
                ]["coins"] += 20

            elif discord.utils.get(
                member.roles,
                id=VIP
            ):

                data[
                    str(member.id)
                ]["coins"] += 4

        save_players(data)

        await ctx.send(
            "✅ Coins mensais entregues."
      )

@tasks.loop(hours=720)
async def mensal_auto(bot):

    guild = bot.guilds[0]

    data = load_players()

    for member in guild.members:

        create_player(
            data,
            member.id
        )

        if discord.utils.get(
            member.roles,
            id=MEGAVIP
        ):

            data[str(member.id)]["coins"] += 20

        elif discord.utils.get(
            member.roles,
            id=VIP
        ):

            data[str(member.id)]["coins"] += 4

    save_players(data)

    print("💎 Coins mensais entregues.")
