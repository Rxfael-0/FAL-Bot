import discord
from discord.ext import commands
import os
import json

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
            "trofeus": 0
        }

    return data[str(user_id)]


# ================= EVENTS =================

@bot.event
async def on_ready():
    print(f'Bot ligado como {bot.user}')


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
        color=discord.Color.red()
    )

    embed.add_field(name="🏆 Troféus", value=player["trofeus"], inline=False)

    await ctx.send(embed=embed)


# ================= TROFÉUS =================

@bot.command()
async def addtrofeu(ctx, quantidade: int, member: discord.Member):
    data = load_data()

    player = get_player(data, member.id)
    player["trofeus"] += quantidade

    save_data(data)

    await ctx.send(f"🏆 {member.mention} ganhou **{quantidade}** troféus!")


@bot.command()
async def removetrofeu(ctx, quantidade: int, member: discord.Member):
    data = load_data()

    player = get_player(data, member.id)
    player["trofeus"] -= quantidade

    if player["trofeus"] < 0:
        player["trofeus"] = 0

    save_data(data)

    await ctx.send(f"📉 {member.mention} perdeu **{quantidade}** troféus!")


# ================= RUN =================

bot.run(os.getenv("TOKEN"))
