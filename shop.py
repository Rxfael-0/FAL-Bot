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
        coins,
        shop_week
    FROM players
    WHERE user_id = ?
    """, (int(uid),))

    data = cursor.fetchone()

    conn.close()

    return {
        "coins": data[0],
        "shop_week": data[1]
    }


def update_player(uid, coins, shop_week):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players

    SET
        coins = ?,
        shop_week = ?

    WHERE user_id = ?
    """, (
        coins,
        shop_week,
        int(uid)
    ))

    conn.commit()
    conn.close()


# =========================
# LOJA
# =========================

LOJA = {

    "protection": {
        "nome": "🛡 Proteção Troféus",
        "preco": 3,
        "cargo": PROTECTION_ROLE
    },

    "boost": {
        "nome": "🧪 Boost x2",
        "preco": 4,
        "cargo": BOOST_ROLE
    },

    "curse": {
        "nome": "💀 Maldição Sombria",
        "preco": 2,
        "cargo": CURSE_ROLE
    },

    "season": {
        "nome": "🧬 Proteção Season",
        "preco": 7,
        "cargo": SEASON_ROLE
    }
}


# =========================
# SETUP
# =========================

def setup_shop(bot):

    # =========================
    # LOJA
    # =========================

    @bot.command()
    async def loja(ctx):

        embed = discord.Embed(
            title="🛒 LOJA RANKED",
            description=(
                "🛡 **Proteção Troféus** — `3🪙`\n"
                "Impede perda de troféus em derrotas.\n\n"

                "🧪 **Boost x2** — `4🪙`\n"
                "Dobra os troféus recebidos.\n\n"

                "💀 **Maldição Sombria** — `2🪙`\n"
                "Aumenta a perda de troféus do adversário.\n\n"

                "🧬 **Proteção Season** — `7🪙`\n"
                "Protege parte do progresso da season.\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n\n"

                "📌 **Limite semanal:**\n"
                "3 compras por semana.\n\n"

                "📌 **Como comprar:**\n"
                "`!buy protection`\n"
                "`!buy boost`\n"
                "`!buy curse`\n"
                "`!buy season`"
            ),
            color=discord.Color.gold()
        )

        embed.set_footer(
            text="FAL • Ranked Shop"
        )

        await ctx.send(
            embed=embed
        )


    # =========================
    # COMPRAR
    # =========================

    @bot.command()
    async def buy(ctx, item=None):

        if item is None:

            return await ctx.send(
                "❌ Informe o item que deseja comprar.\n"
                "Exemplo: `!buy protection`"
            )

        item = item.lower()

        if item not in LOJA:

            return await ctx.send(
                "❌ Item inválido.\n"
                "Use: `protection`, `boost`, `curse` ou `season`."
            )

        create_player(
            ctx.author.id
        )

        player = get_player(
            ctx.author.id
        )

        # =========================
        # LIMITE SEMANAL
        # =========================

        if player["shop_week"] >= 3:

            return await ctx.send(
                "❌ Você atingiu o limite semanal "
                "de compras. **(3/3)**"
            )

        # =========================
        # CARGO
        # =========================

        cargo = ctx.guild.get_role(
            LOJA[item]["cargo"]
        )

        if cargo is None:

            return await ctx.send(
                "❌ O cargo deste item não foi encontrado."
            )

        if cargo in ctx.author.roles:

            return await ctx.send(
                "❌ Você já possui este item."
            )

        # =========================
        # PREÇO
        # =========================

        preco = LOJA[item]["preco"]

        if player["coins"] < preco:

            return await ctx.send(
                (
                    f"❌ Coins insuficientes.\n"
                    f"Você possui **{player['coins']}🪙** "
                    f"e precisa de **{preco}🪙**."
                )
            )

        # =========================
        # COMPRA
        # =========================

        player["coins"] -= preco
        player["shop_week"] += 1

        update_player(
            ctx.author.id,
            player["coins"],
            player["shop_week"]
        )

        try:

            await ctx.author.add_roles(
                cargo
            )

        except discord.Forbidden:

            # Reverte a compra caso o bot
            # não consiga adicionar o cargo.

            player["coins"] += preco
            player["shop_week"] -= 1

            update_player(
                ctx.author.id,
                player["coins"],
                player["shop_week"]
            )

            return await ctx.send(
                "❌ Não consegui adicionar o cargo. "
                "Verifique as permissões do bot."
            )

        # =========================
        # CONFIRMAÇÃO
        # =========================

        embed = discord.Embed(
            title="✅ Compra realizada!",
            description=(
                f"{ctx.author.mention} comprou "
                f"**{LOJA[item]['nome']}**."
            ),
            color=discord.Color.green()
        )

        embed.add_field(
            name="🪙 Saldo restante",
            value=f"**{player['coins']}🪙**",
            inline=True
        )

        embed.add_field(
            name="🛒 Compras semanais",
            value=f"**{player['shop_week']}/3**",
            inline=True
        )

        embed.set_footer(
            text="FAL • Ranked Shop"
        )

        await ctx.send(
            embed=embed
        )


    # =========================
    # RESET MANUAL
    # =========================

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
            "✅ Limite semanal da loja resetado."
        )


# =========================
# RESET AUTOMÁTICO
# =========================

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

    print(
        "🛒 Limite semanal da loja resetado."
    )
