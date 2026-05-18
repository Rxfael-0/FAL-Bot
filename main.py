import discord
from discord.ext import commands
import os
import json

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATABASE = "database/player.json"


# ================= DATABASE =================

def load_data():
    try:
        with open(DATABASE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)


def get_player(data, user_id):
    if str(user_id) not in data:
        data[str(user_id)] = {
            "trofeus": 0,
            "rank": "R1",
            "league": "L1",
            "medalhas": 0
        }
    return data[str(user_id)]


# ================= RANK SYSTEM =================

def get_rank(t):
    if t < 100:
        return "R1 | Ascendant L1"
    elif t < 300:
        return "R2 | Dominant L1"
    elif t < 500:
        return "R3 | Elite L1"
    elif t < 700:
        return "R4 | Supreme L1"
    elif t < 1000:
        return "R5 | Legendary L1"
    elif t < 1400:
        return "R6 | Mythic L2"
    elif t < 1900:
        return "R7 | Titan L2"
    elif t < 2400:
        return "R8 | Absolute L2"
    elif t < 3000:
        return "R9 | Diamond L2"
    elif t < 3700:
        return "R10 | Infinit L3 WWW"
    elif t < 4400:
        return "R11 | Sovereign L3"
    else:
        return "R12 | FAL BEAST L3"


def get_league(t):
    if t < 1000:
        return "L1"
    elif t < 3000:
        return "L2"
    else:
        return "L3"


# ================= EVENTS =================

@bot.event
async def on_ready():
    print(f"Bot ligado como {bot.user}")


# ================= PERFIL =================

@bot.command()
async def perfil(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    data = load_data()
    player = get_player(data, member.id)

    save_data(data)

    embed = discord.Embed(
        title=f"🏆 Perfil de {member.name}",
        description="Sistema Ranked Competitivo",
        color=discord.Color.red()
    )

    embed.add_field(name="🏆 Troféus", value=player["trofeus"], inline=False)
    embed.add_field(name="📊 Rank", value=player["rank"], inline=False)
    embed.add_field(name="⚔️ League", value=player["league"], inline=False)
    embed.add_field(name="🎖️ Medalhas", value=player["medalhas"], inline=False)

    await ctx.send(embed=embed)


# ================= TROFÉUS =================

@bot.command()
async def addtrofeu(ctx, quantidade: int, member: discord.Member):
    data = load_data()

    player = get_player(data, member.id)
    player["trofeus"] += quantidade

    player["rank"] = get_rank(player["trofeus"])
    player["league"] = get_league(player["trofeus"])

    if player["trofeus"] >= 5000:
        player["medalhas"] += 1

    save_data(data)

    await ctx.send(
        f"🏆 {member.mention} ganhou **{quantidade}** troféus!\n"
        f"📊 {player['rank']} | {player['league']}"
    )


@bot.command()
async def removetrofeu(ctx, quantidade: int, member: discord.Member):
    data = load_data()

    player = get_player(data, member.id)
    player["trofeus"] -= quantidade

    if player["trofeus"] < 0:
        player["trofeus"] = 0

    player["rank"] = get_rank(player["trofeus"])
    player["league"] = get_league(player["trofeus"])

    save_data(data)

    await ctx.send(
        f"📉 {member.mention} perdeu **{quantidade}** troféus!\n"
        f"📊 {player['rank']} | {player['league']}"
    )


# ================= INFO =================

@bot.command()
async def ranked(ctx):
    await ctx.send("""
💬 Bem-vindo ao ranked!

🏆 Sistema composto por ranks, ligas e troféus.

🪙 League 1 → R1 a R5 (0–999)
💎 League 2 → R6 a R9 (1000–2999)
👑 League 3 → R10 a R12 (3000–4999)

🎖️ 5000+ = Medalhas infinitas

⚔️ Matchmaking baseado em leagues
⏳ Season de 2 meses
🏁 Reset parcial ao final da season
""")

# ================= RUN =================

bot.run(os.getenv("TOKEN"))
