import discord
from discord.ext import commands
import os
import json
import random
import asyncio

from modules.logs import add_match_log
from modules.leaderboard import create_leaderboard_image

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= DATABASE =================

DATABASE = "database/player.json"

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
            "medalhas": 0
        }
    return data[str(user_id)]

# ================= MATCH =================

queue = []
cooldown = False
active_matches = {}

# ================= RANK =================

def get_rank(t):
    if t < 100: return "R1"
    elif t < 300: return "R2"
    elif t < 500: return "R3"
    elif t < 700: return "R4"
    elif t < 1000: return "R5"
    elif t < 1400: return "R6"
    elif t < 1900: return "R7"
    elif t < 2400: return "R8"
    elif t < 3000: return "R9"
    elif t < 3700: return "R10"
    elif t < 4400: return "R11"
    return "R12"

def get_league(t):
    if t < 1000: return "L1"
    elif t < 3000: return "L2"
    return "L3"

# ================= EVENTS =================

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

# ================= FILA =================

@bot.command()
async def entrarfila(ctx):
    global queue, cooldown

    if cooldown:
        return await ctx.send("⏳ Cooldown ativo.")

    if ctx.author.id in queue:
        return await ctx.send("⚠️ Já está na fila.")

    queue.append(ctx.author.id)

    await ctx.send(f"🎯 {ctx.author.mention} entrou na fila ({len(queue)}/4)")

    if len(queue) >= 4:
        await start_match(ctx)

@bot.command()
async def sairfila(ctx):
    if ctx.author.id in queue:
        queue.remove(ctx.author.id)
        await ctx.send("🚪 Saiu da fila.")

# ================= MATCH =================

async def start_match(ctx):
    global queue, cooldown, active_matches

    players = queue[:4]
    queue = []

    match_id = random.randint(1000, 9999)
    active_matches[match_id] = players

    mentions = [f"<@{p}>" for p in players]

    await ctx.send(
        f"⚔️ MATCH #{match_id}\n" +
        " VS ".join(mentions) +
        "\n🏁 Use !resultado para finalizar"
    )

    cooldown = True
    await asyncio.sleep(1200)
    cooldown = False

# ================= RESULTADO =================

@bot.command()
async def resultado(ctx):
    global active_matches

    if not active_matches:
        return await ctx.send("❌ Nenhuma partida ativa.")

    match_id, players = active_matches.popitem()

    winner = random.choice(players)

    data = load_data()

    logs_players = []

    for p in players:
        player = get_player(data, p)

        if p == winner:
            player["trofeus"] += 50
        else:
            player["trofeus"] -= 25
            if player["trofeus"] < 0:
                player["trofeus"] = 0

        player["medalhas"] = 1 if player["trofeus"] >= 5000 else player["medalhas"]

        logs_players.append(p)

    save_data(data)

    add_match_log(match_id, "L1", logs_players, winner)

    await ctx.send(f"🏁 Match finalizada! Winner: <@{winner}>")

# ================= LEADERBOARD =================

@bot.command()
async def leaderboard(ctx):
    data = load_data()

    sorted_players = sorted(
        data.items(),
        key=lambda x: x[1]["trofeus"],
        reverse=True
    )[:15]

    users = []

    for user_id, p in sorted_players:
        user = await bot.fetch_user(int(user_id))
        users.append((user, p))

    image = create_leaderboard_image(users)

    await ctx.send(file=discord.File(image, "leaderboard.png"))

# ================= RUN =================

bot.run(os.getenv("TOKEN"))
