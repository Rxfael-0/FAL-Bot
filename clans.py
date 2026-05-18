import json
import discord
from datetime import datetime

FILE = "database/clans.json"

SLOT_PRICES = {
    6: 10,
    7: 15,
    8: 20,
    9: 25,
    10: 30
}

CLAN_SHOP = {
    "logo": 2,
    "nome": 3,
    "cor": 5,
    "destaque": 10
}

# ================= LOAD =================

def load():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================= SETUP =================

def setup_clans(bot):

    # ================= CREATE CLAN =================
    @bot.command()
    async def criarclan(ctx, name: str):

        from ranked import load, save, get_player

        players = load()
        player = get_player(players, ctx.author.id)

        if player["moedas"] < 1:
            return await ctx.send("❌ precisa 1 moeda")

        player["moedas"] -= 1
        save(players)

        data = load()

        if name in data:
            return await ctx.send("❌ já existe")

        data[name] = {
            "leader": str(ctx.author.id),
            "members": [str(ctx.author.id)],
            "max_slots": 5,
            "logo": None,
            "cor": None,
            "destaque": False,
            "created_at": str(datetime.now().strftime("%d/%m/%Y"))
        }

        save(data)

        await ctx.send(f"🏰 Clã {name} criado!")

    # ================= INFO =================
    @bot.command()
    async def clan(ctx, name: str):

        data = load()

        if name not in data:
            return await ctx.send("❌ não existe")

        c = data[name]

        embed = discord.Embed(title=f"🏰 {name}")

        embed.add_field(name="👑 Líder", value=f"<@{c['leader']}>", inline=False)
        embed.add_field(name="👥 Membros", value=len(c["members"]), inline=True)
        embed.add_field(name="📦 Slots", value=c.get("max_slots", 5), inline=True)
        embed.add_field(name="📌 Destaque", value=str(c["destaque"]), inline=True)

        await ctx.send(embed=embed)

    # ================= JOIN =================
    @bot.command()
    async def entrarclan(ctx, name: str):

        data = load()

        if name not in data:
            return await ctx.send("❌ não existe")

        c = data[name]
        uid = str(ctx.author.id)

        if uid in c["members"]:
            return await ctx.send("já está no clã")

        if len(c["members"]) >= c.get("max_slots", 5):
            return await ctx.send("❌ clã cheio")

        c["members"].append(uid)

        save(data)

        await ctx.send("✅ entrou no clã")

    # ================= UPGRADE SLOTS =================
    @bot.command()
    async def upgradarclan(ctx, name: str):

        from ranked import load as l, save as s, get_player

        data = load()

        if name not in data:
            return await ctx.send("❌ não existe")

        c = data[name]

        if str(ctx.author.id) != c["leader"]:
            return await ctx.send("❌ só líder")

        current = c.get("max_slots", 5)

        if current >= 10:
            return await ctx.send("máximo atingido")

        next_slot = current + 1
        price = SLOT_PRICES[next_slot]

        players = l()
        player = get_player(players, ctx.author.id)

        if player["moedas"] < price:
            return await ctx.send("❌ sem moedas")

        player["moedas"] -= price
        c["max_slots"] = next_slot

        s(players)
        save(data)

        await ctx.send(f"🏰 slots aumentados para {next_slot}")

    # ================= CLAN SHOP =================
    @bot.command()
    async def clancustom(ctx, name: str, item: str, *, value=None):

        from ranked import load as l, save as s, get_player

        data = load()

        if name not in data:
            return await ctx.send("❌ não existe")

        c = data[name]

        if str(ctx.author.id) != c["leader"]:
            return await ctx.send("❌ só líder")

        if item not in CLAN_SHOP:
            return await ctx.send("❌ item inválido")

        price = CLAN_SHOP[item]

        players = l()
        player = get_player(players, ctx.author.id)

        if player["moedas"] < price:
            return await ctx.send("❌ sem moedas")

        player["moedas"] -= price

        c[item] = value if value else True

        s(players)
        save(data)

        await ctx.send(f"✨ Clã atualizado: {item}")

    # ================= CLAN WAR =================
    @bot.command()
    async def clanwar(ctx, clan1: str, clan2: str):

        data = load()

        if clan1 not in data or clan2 not in data:
            return await ctx.send("❌ clã não existe")

        await ctx.send(
            f"⚔️ CLAN WAR!\n"
            f"{clan1} VS {clan2}\n\n"
            "Aguardando resultado manual..."
        )

    # ================= RESULT WAR =================
    @bot.command()
    async def warresult(ctx, winner: str):

        data = load()

        if winner not in data:
            return await ctx.send("❌ clã não existe")

        await ctx.send(f"🏆 {winner} venceu a guerra!")
