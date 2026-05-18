import json

FILE = "database/players.json"

def load():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_player(data, uid):
    if str(uid) not in data:
        data[str(uid)] = {
            "trofeus": 0,
            "medalhas": 0,
            "moedas": 0,
            "itens": []
        }
    return data[str(uid)]

def setup_ranked(bot):

    @bot.command()
    async def perfil(ctx, member: discord.Member = None):

        if not member:
            member = ctx.author

        data = load()
        player = get_player(data, member.id)

        embed = discord.Embed(title=f"🏆 Perfil de {member.name}")

        embed.add_field(name="🏆 Troféus", value=player["trofeus"], inline=True)
        embed.add_field(name="🎖️ Medalhas", value=player["medalhas"], inline=True)
        embed.add_field(name="🪙 Moedas", value=player["moedas"], inline=False)

        await ctx.send(embed=embed)

    @bot.command()
    async def addtrofeu(ctx, qtd: int, member: discord.Member):

        data = load()
        player = get_player(data, member.id)

        player["trofeus"] += qtd

        if player["trofeus"] >= 5000:
            player["medalhas"] += 1

        save(data)

        await ctx.send(f"🏆 +{qtd} para {member.mention}")
