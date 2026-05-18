import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime, timedelta

CLAN_FILE = "database/clans.json"
WAR_FILE = "database/clan_wars.json"

ANALISTA_ROLE_ID = 000000000000

SLOT_PRICES = {
    6: 10,
    7: 15,
    8: 20,
    9: 25,
    10: 30
}

CUSTOM_PRICES = {
    "logo": 2,
    "nome": 3,
    "cor": 5,
    "destaque": 10
}

# ================= JSON =================

def load(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ================= EMBED =================

def clan_embed(name, clan):

    embed = discord.Embed(
        title=f"🏰 {name}",
        color=discord.Color.red()
    )

    embed.add_field(name="👑 Líder", value=f"<@{clan['leader']}>", inline=False)

    colider = clan.get("co_leader")

    embed.add_field(
        name="🛡️ Co-líder",
        value=f"<@{colider}>" if colider else "Nenhum",
        inline=False
    )

    members = "\n".join([f"<@{m}>" for m in clan["members"]])

    embed.add_field(name="👥 Membros", value=members, inline=False)

    embed.add_field(name="🏆 Vitórias", value=clan["wins"])
    embed.add_field(name="❌ Derrotas", value=clan["losses"])
    embed.add_field(name="🏳️ Desistências", value=clan["surrenders"])

    embed.add_field(name="📦 Slots", value=clan["max_slots"])

    embed.add_field(name="💤 Status", value=clan["status"])

    embed.add_field(name="🕒 Última atividade", value=clan["last_activity"])

    return embed

# ================= SETUP =================

def setup_clans(bot):

    # ================= CREATE =================
    @bot.command()
    async def criarclan(ctx, nome: str):

        clans = load(CLAN_FILE)

        if nome in clans:
            return await ctx.send("❌ Clã já existe.")

        role = await ctx.guild.create_role(name=nome)

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True)
        }

        channel = await ctx.guild.create_text_channel(
            f"🏰-{nome}",
            overwrites=overwrites
        )

        clans[nome] = {
            "leader": str(ctx.author.id),
            "co_leader": None,
            "members": [str(ctx.author.id)],
            "wins": 0,
            "losses": 0,
            "surrenders": 0,
            "history": [],
            "status": "🟢 Ativo",
            "last_activity": str(datetime.now().strftime("%d/%m/%Y")),
            "max_slots": 5,
            "role_id": role.id,
            "channel_id": channel.id,
            "message_id": None,
            "logo": None,
            "cor": None,
            "destaque": False,
            "war_cooldown": None
        }

        await ctx.author.add_roles(role)

        msg = await channel.send(
            embed=clan_embed(nome, clans[nome])
        )

        clans[nome]["message_id"] = msg.id

        save(CLAN_FILE, clans)

        await ctx.send(f"🏰 Clã {nome} criado!")

    # ================= UPDATE PANEL =================
    async def update_panel(guild, clan_name):

        clans = load(CLAN_FILE)

        clan = clans[clan_name]

        channel = guild.get_channel(clan["channel_id"])

        try:
            msg = await channel.fetch_message(clan["message_id"])

            await msg.edit(
                embed=clan_embed(clan_name, clan)
            )

        except:
            pass

    # ================= SET COLEADER =================
    @bot.command()
    async def setcolider(ctx, clan_name: str, member: discord.Member):

        clans = load(CLAN_FILE)

        clan = clans[clan_name]

        if str(ctx.author.id) != clan["leader"]:
            return await ctx.send("❌ Só líder.")

        clan["co_leader"] = str(member.id)

        save(CLAN_FILE, clans)

        await update_panel(ctx.guild, clan_name)

        await ctx.send("🛡️ Co-líder definido.")

    # ================= JOIN REQUEST =================
    @bot.command()
    async def solicitar(ctx, clan_name: str):

        clans = load(CLAN_FILE)

        clan = clans[clan_name]

        if "requests" not in clan:
            clan["requests"] = []

        clan["requests"].append(str(ctx.author.id))

        save(CLAN_FILE, clans)

        await ctx.send("📩 Solicitação enviada.")

    # ================= ACCEPT =================
    @bot.command()
    async def aceitar(ctx, clan_name: str, member: discord.Member):

        clans = load(CLAN_FILE)

        clan = clans[clan_name]

        uid = str(ctx.author.id)

        if uid not in [clan["leader"], clan.get("co_leader")]:
            return await ctx.send("❌ Sem permissão.")

        role = ctx.guild.get_role(clan["role_id"])

        await member.add_roles(role)

        clan["members"].append(str(member.id))

        if str(member.id) in clan["requests"]:
            clan["requests"].remove(str(member.id))

        save(CLAN_FILE, clans)

        await update_panel(ctx.guild, clan_name)

        await ctx.send("✅ Membro aprovado.")

    # ================= REMOVE =================
    @bot.command()
    async def removermembro(ctx, clan_name: str, member: discord.Member):

        clans = load(CLAN_FILE)

        clan = clans[clan_name]

        uid = str(ctx.author.id)

        if uid not in [clan["leader"], clan.get("co_leader")]:
            return await ctx.send("❌ Sem permissão.")

        role = ctx.guild.get_role(clan["role_id"])

        await member.remove_roles(role)

        clan["members"].remove(str(member.id))

        save(CLAN_FILE, clans)

        await update_panel(ctx.guild, clan_name)

        await ctx.send("❌ Membro removido.")

    # ================= CLAN WAR =================
    @bot.command()
    async def clanwar(ctx, desafiante: str, adversario: str):

        clans = load(CLAN_FILE)
        wars = load(WAR_FILE)

        if desafiante not in clans or adversario not in clans:
            return await ctx.send("❌ Clã não existe.")

        war_id = str(len(wars) + 1)

        wars[war_id] = {
            "challenger": desafiante,
            "enemy": adversario,
            "status": "pending",
            "created": str(datetime.now())
        }

        save(WAR_FILE, wars)

        role1 = ctx.guild.get_role(clans[desafiante]["role_id"])
        role2 = ctx.guild.get_role(clans[adversario]["role_id"])

        msg = await ctx.send(
            f"⚔️ {role1.mention} desafiou {role2.mention}\n"
            "✅ aceitar\n"
            "❌ desistir"
        )

        async def timer():

            await asyncio.sleep(3600)

            await ctx.send("⏳ 1h restante.")

            await asyncio.sleep(3000)

            await ctx.send("⚠️ 10 minutos restantes.")

            await asyncio.sleep(600)

            wars = load(WAR_FILE)

            if wars[war_id]["status"] == "pending":

                wars[war_id]["status"] = "surrender"

                clans[adversario]["surrenders"] += 1

                save(WAR_FILE, wars)
                save(CLAN_FILE, clans)

        bot.loop.create_task(timer())

    # ================= ACCEPT WAR =================
    @bot.command()
    async def aceitarwar(ctx, war_id: str):

        wars = load(WAR_FILE)

        if war_id not in wars:
            return await ctx.send("❌ guerra não existe")

        wars[war_id]["status"] = "accepted"

        save(WAR_FILE, wars)

        role = ctx.guild.get_role(ANALISTA_ROLE_ID)

        await ctx.send(
            f"✅ Guerra aceita!\n{role.mention}"
        )

    # ================= RESULT =================
    @bot.command()
    async def resultado(ctx, war_id: str, placar: str):

        if ANALISTA_ROLE_ID not in [r.id for r in ctx.author.roles]:
            return await ctx.send("❌ Apenas Analista Técnico.")

        clans = load(CLAN_FILE)
        wars = load(WAR_FILE)

        war = wars[war_id]

        challenger = war["challenger"]
        enemy = war["enemy"]

        if placar in ["2x0", "2x1"]:

            clans[challenger]["wins"] += 1
            clans[enemy]["losses"] += 1

            winner = challenger

        else:

            clans[enemy]["wins"] += 1
            clans[challenger]["losses"] += 1

            winner = enemy

        clans[winner]["history"].append(
            f"🏆 venceu guerra ({placar})"
        )

        wars[war_id]["status"] = "finished"

        save(CLAN_FILE, clans)
        save(WAR_FILE, wars)

        canal = discord.utils.get(
            ctx.guild.channels,
            name="🏆・resultados"
        )

        if canal:
            await canal.send(
                f"🏆 {winner} venceu a clan war ({placar})"
            )

        await update_panel(ctx.guild, challenger)
        await update_panel(ctx.guild, enemy)

        await ctx.send("🏆 Resultado registrado.")

    # ================= LEADERBOARD =================
    @bot.command()
    async def clanlb(ctx):

        clans = load(CLAN_FILE)

        ranking = sorted(
            clans.items(),
            key=lambda x: x[1]["wins"],
            reverse=True
        )

        embed = discord.Embed(
            title="🏆 Clan Leaderboard",
            color=discord.Color.gold()
        )

        for i, (name, c) in enumerate(ranking[:10], start=1):

            embed.add_field(
                name=f"{i}º {name}",
                value=f"🏆 {c['wins']} vitórias",
                inline=False
            )

        await ctx.send(embed=embed)
