import discord
from discord.ext import commands, tasks
import sqlite3

DATABASE = "database/database.db"

SHOP_CHANNEL = 1506470884381167726

PROTECTION_ROLE = 1499609557138407424
BOOST_ROLE = 1499608761592053840
CURSE_ROLE = 1499609510623580190
SEASON_ROLE = 1499609960869400636

# =========================
# SQLITE
# =========================

def connect_db():

    return sqlite3.connect(DATABASE)

def create_player(uid):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        user_id TEXT PRIMARY KEY,
        trofeus INTEGER,
        medalhas INTEGER,
        coins INTEGER,
        wins INTEGER,
        losses INTEGER,
        seasonwins TEXT,
        medals TEXT,
        hall TEXT,
        partidas TEXT,
        shop_week INTEGER
    )
    """)

    cursor.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (str(uid),)
    )

    player = cursor.fetchone()

    if not player:

        cursor.execute("""
        INSERT INTO players VALUES (
            ?, 0, 0, 0, 0, 0,
            '[]', '[]', '[]', '[]', 0
        )
        """, (str(uid),))

    conn.commit()
    conn.close()

def get_player(uid):

    create_player(uid)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (str(uid),)
    )

    data = cursor.fetchone()

    conn.close()

    return {
        "coins": data[3],
        "shop_week": data[10]
    }

def update_player(uid, coins, shop_week):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET coins = ?, shop_week = ?
    WHERE user_id = ?
    """, (
        coins,
        shop_week,
        str(uid)
    ))

    conn.commit()
    conn.close()

# =========================
# LOJA
# =========================

LOJA = {

    "protection": {

        "nome": "🛡 Proteção troféus",
        "preco": 3,
        "cargo": PROTECTION_ROLE
    },

    "boost": {

        "nome": "🧪 Boost x2",
        "preco": 4,
        "cargo": BOOST_ROLE
    },

    "curse": {

        "nome": "💀 Maldição sombria",
        "preco": 2,
        "cargo": CURSE_ROLE
    },

    "season": {

        "nome": "🧬 Proteção season",
        "preco": 7,
        "cargo": SEASON_ROLE
    }
}

# =========================
# SETUP
# =========================

def setup_shop(bot):

    @bot.command()
    async def loja(ctx):

        embed = discord.Embed(
            title="🛒 LOJA RANKED",
            color=discord.Color.gold()
        )

        embed.description = (

            "🛡 **Proteção Troféus** — 3🪙\n"
            "Impede perda de troféus em derrotas.\n\n"

            "🧪 **Boost x2** — 4🪙\n"
            "Dobra os troféus recebidos.\n\n"

            "💀 **Maldição Sombria** — 2🪙\n"
            "Aumenta a perda de troféus do adversário.\n\n"

            "🧬 **Proteção Season** — 7🪙\n"
            "Protege parte do progresso da season.\n\n"

            "📌 Limite semanal:\n"
            "3 compras por semana.\n\n"

            "📌 Use:\n"
            "`!buy protection`\n"
            "`!buy boost`\n"
            "`!buy curse`\n"
            "`!buy season`"
        )

        await ctx.send(embed=embed)

    @bot.command()
    async def buy(ctx, item):

        item = item.lower()

        if item not in LOJA:

            return await ctx.send(
                "❌ Item inválido."
            )

        create_player(ctx.author.id)

        player = get_player(ctx.author.id)

        if player["shop_week"] >= 3:

            return await ctx.send(
                "❌ Você atingiu o limite semanal de compras. (3/3)"
            )

        cargo = ctx.guild.get_role(
            LOJA[item]["cargo"]
        )

        if cargo in ctx.author.roles:

            return await ctx.send(
                "❌ Você já possui este item."
            )

        preco = LOJA[item]["preco"]

        if player["coins"] < preco:

            return await ctx.send(
                "❌ Coins insuficientes."
            )

        player["coins"] -= preco
        player["shop_week"] += 1

        update_player(
            ctx.author.id,
            player["coins"],
            player["shop_week"]
        )

        await ctx.author.add_roles(
            cargo
        )

        embed = discord.Embed(
            title="✅ Compra realizada",
            description=(

                f"{ctx.author.mention} "
                f"comprou "
                f"{LOJA[item]['nome']}\n\n"

                f"🛒 Compras semanais: "
                f"{player['shop_week']}/3"
            ),
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def resetshop(ctx):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE players
        SET shop_week = 0
        """)

        conn.commit()
        conn.close()

        await ctx.send(
            "✅ Limite semanal resetado."
        )

@tasks.loop(hours=168)
async def reset_shop_limits():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET shop_week = 0
    """)

    conn.commit()
    conn.close()

    print("🛒 Loja semanal resetada.")
