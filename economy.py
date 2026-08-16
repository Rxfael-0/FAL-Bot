import discord
from discord import app_commands
import sqlite3


DATABASE = "database/database.db"


# =========================
# CARGOS
# =========================

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

    cursor.execute("""
    SELECT coins
    FROM players
    WHERE user_id = ?
    """, (int(uid),))

    result = cursor.fetchone()

    conn.close()

    if not result:
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


def remove_coins(uid, quantidade):

    create_player(uid)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET coins = MAX(0, coins - ?)
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

    # =========================
    # MOEDAS
    # =========================

    @bot.tree.command(
        name="moedas",
        description="Veja a quantidade de coins de um jogador."
    )
    @app_commands.describe(
        membro="Jogador que deseja consultar."
    )
    async def moedas(
        interaction: discord.Interaction,
        membro: discord.Member = None
    ):

        if membro is None:
            membro = interaction.user

        coins = get_coins(membro.id)

        embed = discord.Embed(
            title="🪙 Coins",
            description=(
                f"{membro.mention} possui "
                f"**{coins}🪙**"
            ),
            color=discord.Color.gold()
        )

        embed.set_thumbnail(
            url=membro.display_avatar.url
        )

        embed.set_footer(
            text="FAL • Economy"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # ADDCOIN
    # =========================

    @bot.tree.command(
        name="addcoin",
        description="Adiciona coins a um jogador."
    )
    @app_commands.describe(
        membro="Jogador que receberá as coins.",
        quantidade="Quantidade de coins."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def addcoin(
        interaction: discord.Interaction,
        membro: discord.Member,
        quantidade: int
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Você precisa ser administrador para usar este comando.",
                ephemeral=True
            )

        if quantidade <= 0:

            return await interaction.response.send_message(
                "❌ A quantidade precisa ser maior que 0.",
                ephemeral=True
            )

        add_coins(
            membro.id,
            quantidade
        )

        novo_saldo = get_coins(
            membro.id
        )

        embed = discord.Embed(
            title="🪙 Coins adicionadas",
            description=(
                f"{membro.mention} recebeu "
                f"**+{quantidade}🪙**\n\n"
                f"💰 Novo saldo: **{novo_saldo}🪙**"
            ),
            color=discord.Color.green()
        )

        embed.set_footer(
            text=f"Adicionado por {interaction.user.display_name}"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # REMOVECOIN
    # =========================

    @bot.tree.command(
        name="removecoin",
        description="Remove coins de um jogador."
    )
    @app_commands.describe(
        membro="Jogador que perderá as coins.",
        quantidade="Quantidade de coins."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def removecoin(
        interaction: discord.Interaction,
        membro: discord.Member,
        quantidade: int
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Você precisa ser administrador para usar este comando.",
                ephemeral=True
            )

        if quantidade <= 0:

            return await interaction.response.send_message(
                "❌ A quantidade precisa ser maior que 0.",
                ephemeral=True
            )

        saldo_atual = get_coins(
            membro.id
        )

        if saldo_atual <= 0:

            return await interaction.response.send_message(
                f"❌ {membro.mention} não possui coins.",
                ephemeral=True
            )

        quantidade_real = min(
            quantidade,
            saldo_atual
        )

        remove_coins(
            membro.id,
            quantidade_real
        )

        novo_saldo = get_coins(
            membro.id
        )

        embed = discord.Embed(
            title="🪙 Coins removidas",
            description=(
                f"{membro.mention} perdeu "
                f"**-{quantidade_real}🪙**\n\n"
                f"💰 Novo saldo: **{novo_saldo}🪙**"
            ),
            color=discord.Color.red()
        )

        embed.set_footer(
            text=f"Removido por {interaction.user.display_name}"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # PAY
    # =========================

    @bot.tree.command(
        name="pay",
        description="Envie coins para outro jogador."
    )
    @app_commands.describe(
        membro="Jogador que receberá as coins.",
        quantidade="Quantidade de coins."
    )
    async def pay(
        interaction: discord.Interaction,
        membro: discord.Member,
        quantidade: int
    ):

        if membro.id == interaction.user.id:

            return await interaction.response.send_message(
                "❌ Você não pode enviar coins para si mesmo.",
                ephemeral=True
            )

        if membro.bot:

            return await interaction.response.send_message(
                "❌ Você não pode enviar coins para um bot.",
                ephemeral=True
            )

        if quantidade <= 0:

            return await interaction.response.send_message(
                "❌ A quantidade precisa ser maior que 0.",
                ephemeral=True
            )

        saldo = get_coins(
            interaction.user.id
        )

        if saldo < quantidade:

            return await interaction.response.send_message(
                (
                    "❌ Você não possui coins suficientes.\n\n"
                    f"💰 Seu saldo: **{saldo}🪙**"
                ),
                ephemeral=True
            )

        remove_coins(
            interaction.user.id,
            quantidade
        )

        add_coins(
            membro.id,
            quantidade
        )

        novo_saldo = get_coins(
            interaction.user.id
        )

        embed = discord.Embed(
            title="💸 Transferência realizada",
            description=(
                f"📤 {interaction.user.mention} enviou "
                f"**{quantidade}🪙** para {membro.mention}.\n\n"
                f"💰 Seu novo saldo: **{novo_saldo}🪙**"
            ),
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # PRICES
    # =========================

    @bot.tree.command(
        name="prices",
        description="Veja a tabela de conversão de Robux e PIX para coins."
    )
    async def prices(
        interaction: discord.Interaction
    ):

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

            "✨ **PIX possui melhor custo benefício.**"
        )

        embed.set_footer(
            text="FAL • Economy"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # MENSAL
    # =========================

    @bot.tree.command(
        name="mensal",
        description="Entrega as coins mensais para VIP e MEGAVIP."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def mensal(
        interaction: discord.Interaction
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Você precisa ser administrador para usar este comando.",
                ephemeral=True
            )

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando só pode ser usado em um servidor.",
                ephemeral=True
            )

        entregues_vip = 0
        entregues_megavip = 0

        for member in interaction.guild.members:

            # =========================
            # MEGAVIP
            # =========================

            if discord.utils.get(
                member.roles,
                id=MEGAVIP
            ):

                add_coins(
                    member.id,
                    20
                )

                entregues_megavip += 1

            # =========================
            # VIP
            # =========================

            elif discord.utils.get(
                member.roles,
                id=VIP
            ):

                add_coins(
                    member.id,
                    4
                )

                entregues_vip += 1

        embed = discord.Embed(
            title="💎 Coins mensais entregues",
            description=(
                "O pagamento mensal foi concluído.\n\n"
                f"💎 MEGAVIP: **{entregues_megavip}** membros\n"
                f"⭐ VIP: **{entregues_vip}** membros"
            ),
            color=discord.Color.green()
        )

        embed.set_footer(
            text="FAL • Economy"
        )

        await interaction.response.send_message(
            embed=embed
        )
