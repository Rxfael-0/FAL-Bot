import json

FILE = "database/players.json"

def setup_economy(bot):

    def load():
        try:
            with open(FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def save(data):
        with open(FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get(data, uid):
        if str(uid) not in data:
            data[str(uid)] = {"moedas": 0}
        return data[str(uid)]

    @bot.command()
    async def addmoeda(ctx, qtd: int, member: discord.Member):

        data = load()
        player = get(data, member.id)

        player["moedas"] += qtd

        save(data)

        await ctx.send(f"🪙 {member.mention} +{qtd}")
