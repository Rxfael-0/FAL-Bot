import discord
from discord.ext import commands
import json
from datetime import datetime

PLAYERS = "database/players.json"
MATCHES = "database/matches.json"
HALL = "database/hall.json"

RANKS = {

    "R1": {
        "min": 0,
        "max": 99,
        "role": 1460459242413752381
    },

    "R2": {
        "min": 100,
        "max": 299,
        "role": 1460460021564440666
    },

    "R3": {
        "min": 300,
        "max": 499,
        "role": 1460460328948338852
    },

    "R4": {
        "min": 500,
        "max": 699,
        "role": 1460460452810330249
    },

    "R5": {
        "min": 700,
        "max": 999,
        "role": 1460460767290724384
    },

    "R6": {
        "min": 1000,
        "max": 1399,
        "role": 1460510486075543685
    },

    "R7": {
        "min": 1400,
        "max": 1899,
        "role": 1460510898174300301
    },

    "R8": {
        "min": 1900,
        "max": 2399,
        "role": 1460511507124060212
    },

    "R9": {
        "min": 2400,
        "max": 2999,
        "role": 1460511975007326280
    },

    "R10": {
        "min": 3000,
        "max": 3699,
        "role": 1460513229997609024
    },

    "R11": {
        "min": 3700,
        "max": 4399,
        "role": 1460514685110718466
    },

    "R12": {
        "min": 4400,
        "max": 4999,
        "role": 1460515368069234729
    }
}

LEAGUES = {

    "L1": 1460723355945795821,
    "L2": 1460723503971172403,
    "L3": 1460723621025681523
}

PROTECTION_ROLE = 1499609557138407424
BOOST_ROLE = 1499608761592053840
CURSE_ROLE = 1499609510623580190
SEASON_ROLE = 1499609960869400636

MEGAVIP = 1460867926948057202

def load_players():

    with open(PLAYERS, "r") as f:
        return json.load(f)

def save_players(data):

    with open(PLAYERS, "w") as f:
        json.dump(data, f, indent=4)

def load_matches():

    with open(MATCHES, "r") as f:
        return json.load(f)

def save_matches(data):

    with open(MATCHES, "w") as f:
        json.dump(data, f, indent=4)

def load_hall():

    with open(HALL, "r") as f:
        return json.load(f)

def create_player(user):

    players = load_players()

    if user not in players:

        players[user] = {

            "trofeus": 0,
            "medalhas": 0,
            "wins": 0,
            "losses": 0,
            "coins": 0,
            "seasonwins": [],
            "medals": [],
            "hall": []
        }

        save_players(players)

async def update_rank_roles(
    guild,
    member,
    trofeus
):

    for rank in RANKS.values():

        role = guild.get_role(
            rank["role"]
        )

        if role in member.roles:

            await member.remove_roles(role)

    for nome, rank in RANKS.items():

        if (
            trofeus >= rank["min"]
            and
            trofeus <= rank["max"]
        ):

            role = guild.get_role(
                rank["role"]
            )

            await member.add_roles(role)

    for role_id in LEAGUES.values():

        role = guild.get_role(role_id)

        if role in member.roles:

            await member.remove_roles(role)

    if trofeus < 1000:

        await member.add_roles(
            guild.get_role(
                LEAGUES["L1"]
            )
        )

    elif trofeus < 3000:

        await member.add_roles(
            guild.get_role(
                LEAGUES["L2"]
            )
        )

    else:

        await member.add_roles(
            guild.get_role(
                LEAGUES["L3"]
            )
        )

def setup_ranked(bot):

    @bot.command()
    async def perfil(
        ctx,
        member: discord.Member=None
    ):

        if member is None:

            member = ctx.author

        players = load_players()
        hall = load_hall()

        user = str(member.id)

        create_player(user)

        players = load_players()

        data = players[user]

        trofeus = data["trofeus"]

        rank_name = "Unranked"

        for nome, rank in RANKS.items():

            if (
                trofeus >= rank["min"]
                and
                trofeus <= rank["max"]
            ):

                rank_name = nome

        embed = discord.Embed(
            title=f"🏆 Perfil • {member.name}",
            color=discord.Color.red()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="🏅 Rank",
            value=rank_name
        )

        embed.add_field(
            name="🏆 Troféus",
            value=data["trofeus"]
        )

        embed.add_field(
            name="🎖 Medalhas",
            value=data["medalhas"]
        )

        embed.add_field(
            name="🪙 Coins",
            value=data["coins"]
        )

        medals = " ".join(
            data["medals"]
        )

        if medals == "":
            medals = "Nenhuma"

        embed.add_field(
            name="🏅 Coleção",
            value=medals,
            inline=False
        )

        feitos = ""

        if user in hall:

            for item in hall[user]:

                feitos += (
                    f"🏆 {item['data']} "
                    f"┊ {item['feito']}\n"
                )

        if feitos == "":

            feitos = (
                "❌ Nenhum desempenho "
                "registrado."
            )

        embed.add_field(
            name="🏁 Hall da Fama",
            value=feitos,
            inline=False
        )

        embed.set_footer(
            text="🏆 Sistema Competitivo"
        )

        await ctx.send(embed=embed)

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def addtrofeu(
        ctx,
        quantidade: int,
        member: discord.Member
    ):

        players = load_players()

        user = str(member.id)

        create_player(user)

        players = load_players()

        ganho = quantidade

        if discord.utils.get(
            member.roles,
            id=MEGAVIP
        ):

            ganho = int(
                ganho * 1.05
            )

        if discord.utils.get(
            member.roles,
            id=BOOST_ROLE
        ):

            ganho *= 2

        players[user][
            "trofeus"
        ] += ganho

        if (
            players[user]["trofeus"]
            >= 5000
        ):

            players[user][
                "medalhas"
            ] += 1

        save_players(players)

        await update_rank_roles(
            ctx.guild,
            member,
            players[user]["trofeus"]
        )

        embed = discord.Embed(
            title="🏆 TROFÉUS ADICIONADOS",
            color=discord.Color.green()
        )

        embed.description = (
            f"{member.mention} "
            f"recebeu +{ganho}🏆"
        )

        await ctx.send(embed=embed)

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def removetrofeu(
        ctx,
        quantidade: int,
        member: discord.Member
    ):

        players = load_players()

        user = str(member.id)

        create_player(user)

        players = load_players()

        perda = quantidade

        if discord.utils.get(
            member.roles,
            id=PROTECTION_ROLE
        ):

            await ctx.send(
                "🛡 Proteção ativada."
            )

            await member.remove_roles(
                ctx.guild.get_role(
                    PROTECTION_ROLE
                )
            )

            return

        if discord.utils.get(
            member.roles,
            id=CURSE_ROLE
        ):

            perda = int(
                perda * 1.5
            )

        players[user][
            "trofeus"
        ] -= perda

        if (
            players[user]["trofeus"]
            < 0
        ):

            players[user][
                "trofeus"
            ] = 0

        save_players(players)

        await update_rank_roles(
            ctx.guild,
            member,
            players[user]["trofeus"]
        )

        embed = discord.Embed(
            title="❌ TROFÉUS REMOVIDOS",
            color=discord.Color.red()
        )

        embed.description = (
            f"{member.mention} "
            f"perdeu {perda}🏆"
        )

        await ctx.send(embed=embed)

    @bot.command()
    @commands.has_permissions(
        administrator=True
    )
    async def add(
        ctx,
        emoji,
        member: discord.Member
    ):

        players = load_players()

        user = str(member.id)

        create_player(user)

        players = load_players()

        players[user][
            "medals"
        ].append(emoji)

        save_players(players)

        embed = discord.Embed(
            title="🏅 MEDALHA ADICIONADA",
            color=discord.Color.gold()
        )

        embed.description = (
            f"{member.mention} "
            f"recebeu {emoji}"
        )

        await ctx.send(embed=embed)

    @bot.command()
    async def top(ctx):

        players = load_players()

        ranking = sorted(
            players.items(),
            key=lambda x: (
                x[1]["medalhas"],
                x[1]["trofeus"]
            ),
            reverse=True
        )

        embed = discord.Embed(
            title="🏆 TOP 3",
            color=discord.Color.gold()
        )

        pos = 1

        for user, data in ranking[:3]:

            membro = await bot.fetch_user(
                int(user)
            )

            embed.add_field(
                name=f"#{pos} {membro.name}",
                value=(
                    f"{data['trofeus']}🏆\n"
                    f"{data['medalhas']}🎖"
                ),
                inline=False
            )

            pos += 1

        await ctx.send(embed=embed)
