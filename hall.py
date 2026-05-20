import discord
from discord.ext import commands
import json
from datetime import datetime

DATABASE = "database/hall.json"

def load_hall():

    with open(DATABASE, "r") as f:
        return json.load(f)

def save_hall(data):

    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)

def setup_hall(bot):

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def halldafama(
        ctx,
        member: discord.Member,
        season,
        *,
        feito
    ):

        data = load_hall()

        user = str(member.id)

        if user not in data:

            data[user] = []

        data[user].append({

            "season": season,
            "feito": feito,
            "data": datetime.now().strftime(
                "%d/%m/%Y"
            )
        })

        save_hall(data)

        embed = discord.Embed(
            title="🏆 HALL DA FAMA",
            description=(
                f"{member.mention} recebeu "
                f"um feito competitivo."
            ),
            color=discord.Color.gold()
        )

        embed.add_field(
            name="🏁 Season",
            value=season
        )

        embed.add_field(
            name="📜 Feito",
            value=feito,
            inline=False
        )

        await ctx.send(embed=embed)
