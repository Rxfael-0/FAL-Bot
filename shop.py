import discord
from discord import app_commands
import sqlite3

DATABASE = "database/database.db"

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

    if not data:
        return {
            "coins": 0,
            "shop_week": 0
        }

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

    @bot.tree.command(
        name="loja",
        description="Veja os itens disponíveis na loja Ranked."
    )
    async def loja(
        interaction: discord.Interaction
    ):

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
                "`/buy protection`\n"
                "`/buy boost`\n"
                "`/buy curse`\n"
                "`/buy season`"
            ),
            color=discord.Color.gold()
        )

        embed.set_footer(
            text="FAL • Ranked Shop"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # COMPRAR
    # =========================

    @bot.tree.command(
        name="buy",
        description="Compre um item da loja Ranked."
    )
    @app_commands.describe(
        item="Item que deseja comprar."
    )
    @app_commands.choices(
        item=[
            app_commands.Choice(
                name="🛡 Proteção Troféus",
                value="protection"
            ),
            app_commands.Choice(
                name="🧪 Boost x2",
                value="boost"
            ),
            app_commands.Choice(
                name="💀 Maldição Sombria",
                value="curse"
            ),
            app_commands.Choice(
                name="🧬 Proteção Season",
                value="season"
            )
        ]
    )
    async def buy(
        interaction: discord.Interaction,
        item: app_commands.Choice[str]
    ):

        item_key = item.value

        create_player(
            interaction.user.id
        )

        player = get_player(
            interaction.user.id
        )

        # =========================
        # LIMITE SEMANAL
        # =========================

        if player["shop_week"] >= 3:

            return await interaction.response.send_message(
                "❌ Você atingiu o limite semanal "
                "de compras. **(3/3)**",
                ephemeral=True
            )

        # =========================
        # CARGO
        # =========================

        cargo = interaction.guild.get_role(
            LOJA[item_key]["cargo"]
        )

        if cargo is None:

            return await interaction.response.send_message(
                "❌ O cargo deste item não foi encontrado.",
                ephemeral=True
            )

        if cargo in interaction.user.roles:

            return await interaction.response.send_message(
                "❌ Você já possui este item.",
                ephemeral=True
            )

        # =========================
        # PREÇO
        # =========================

        preco = LOJA[item_key]["preco"]

        if player["coins"] < preco:

            return await interaction.response.send_message(
                (
                    f"❌ Coins insuficientes.\n"
                    f"Você possui **{player['coins']}🪙** "
                    f"e precisa de **{preco}🪙**."
                ),
                ephemeral=True
            )

        # =========================
        # COMPRA
        # =========================

        player["coins"] -= preco
        player["shop_week"] += 1

        update_player(
            interaction.user.id,
            player["coins"],
            player["shop_week"]
        )

        try:

            await interaction.user.add_roles(
                cargo
            )

        except discord.Forbidden:

            # Reverte a compra caso o bot
            # não consiga adicionar o cargo.

            player["coins"] += preco
            player["shop_week"] -= 1

            update_player(
                interaction.user.id,
                player["coins"],
                player["shop_week"]
            )

            return await interaction.response.send_message(
                "❌ Não consegui adicionar o cargo. "
                "Verifique as permissões e a posição "
                "do cargo do bot.",
                ephemeral=True
            )

        # =========================
        # CONFIRMAÇÃO
        # =========================

        embed = discord.Embed(
            title="✅ Compra realizada!",
            description=(
                f"{interaction.user.mention} comprou "
                f"**{LOJA[item_key]['nome']}**."
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

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # RESET MANUAL
    # =========================

    @bot.tree.command(
        name="resetshop",
        description="Reseta o limite semanal da loja."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def resetshop(
        interaction: discord.Interaction
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Você precisa ser administrador.",
                ephemeral=True
            )

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE players
        SET shop_week = 0
        """)

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            "✅ Limite semanal da loja resetado."
        )
