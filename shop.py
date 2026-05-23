import discord
from discord.ext import commands
import json

PLAYERS = "database/players.json"

SHOP_CHANNEL = 1506470884381167726

PROTECTION_ROLE = 1499609557138407424
BOOST_ROLE = 1499608761592053840
CURSE_ROLE = 1499609510623580190
SEASON_ROLE = 1499609960869400636

def load_players():

    with open(PLAYERS, "r") as f:
        return json.load(f)

def save_players(data):

    with open(PLAYERS, "w") as f:
        json.dump(data, f, indent=4)

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
            "partidas": [],
            "shop_week": 0
        }

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
    async def buy(
        ctx,
        item
    ):

        item = item.lower()

        if item not in LOJA:

            return await ctx.send(
                "❌ Item inválido."
            )

        data = load_players()

        create_player(
            data,
            ctx.author.id
        )

        if data[
            str(ctx.author.id)
        ]["shop_week"] >= 3:

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

        if data[
            str(ctx.author.id)
        ]["coins"] < preco:

            return await ctx.send(
                "❌ Coins insuficientes."
            )

        data[
            str(ctx.author.id)
        ]["coins"] -= preco

        data[
            str(ctx.author.id)
        ]["shop_week"] += 1

        save_players(data)

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
                f"{data[str(ctx.author.id)]['shop_week']}/3"
            ),
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def resetshop(ctx):

        data = load_players()

        for player in data:

            data[player]["shop_week"] = 0

        save_players(data)

        await ctx.send(
            "✅ Limite semanal resetado."
        )
