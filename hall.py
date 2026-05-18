import discord
from discord.ext import commands
import json

FILE = "database/hall.json"

def setup_hall(bot):

    @bot.command()
    async def halldafama(ctx, member: discord.Member, *, text: str):

        try:
            with open(FILE, "r") as f:
                data = json.load(f)
        except:
            data = []

        data.append({
            "user": member.id,
            "feito": text
        })

        with open(FILE, "w") as f:
            json.dump(data, f, indent=4)

        await ctx.send("🏆 registrado no Hall da Fama")
