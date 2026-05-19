import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import json
import asyncio
from datetime import datetime, timedelta

CLAN_FILE = "database/clans.json"
WAR_FILE = "database/clan_wars.json"
PLAYERS_FILE = "database/players.json"

ANALISTA_ROLE_ID = 1399531186472226898

SLOT_PRICES = {
    6: 10,
    7: 15,
    8: 20,
    9: 25,
    10: 30
}

SHOP = {
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

# ================= ACTIVITY =================

def update_activity(clan):
    clan["last_activity"] = datetime.now().isoformat()
    clan["status"] = "🟢 Ativo"

# ================= EMBED =================

def clan_embed(nome, c):

    members = "\n".join([f"<@{m}>" for m in c["members"]])

    embed = discord.Embed(
        title=f"🏰 {nome}",
        color=discord.Color.red()
    )

    embed.add_field(
        name="👑 Líder",
        value=f"<@{c['leader']}>",
        inline=False
    )

    embed.add_field(
        name="🛡 Co-líder",
        value=f"<@{c['coleader']}>" if c["coleader"] else "Nenhum",
        inline=False
    )

    embed.add_field(
        name="👥 Membros",
        value=members if members else "Nenhum",
        inline=False
    )

    embed.add_field(name="🏆 Vitórias", value=c["wins"])
    embed.add_field(name="❌ Derrotas", value=c["losses"])
    embed.add_field(name="🏳️ Desistências", value=c["surrenders"])

    embed.add_field(name="📦 Slots", value=f"{len(c['members'])}/{c['max_slots']}")

    embed.add_field(name="💤 Status", value=c["status"])

    embed.add_field(
        name="🕒 Última atividade",
        value=c["last_activity"][:19]
    )

    return embed

# ================= PANEL UPDATE =================

async def update_panel(bot, guild, nome):

    clans = load(CLAN_FILE)

    c = clans[nome]

    try:

        channel = guild.get_channel(c["channel_id"])

        msg = await channel.fetch_message(c["panel_message"])

        await msg.edit(
            embed=clan_embed(nome, c)
        )

    except:
        pass

# ================= SETUP =================

def setup_clans(bot):

    # ================= CREATE CLAN =================

    @bot.command()
    async def criarclan(ctx, nome: str):

        clans = load(CLAN_FILE)
        players = load(PLAYERS_FILE)

        uid = str(ctx.author.id)

        if nome in clans:
            return await ctx.send("❌ clã já existe")

        if uid not in players:
            players[uid] = {
                "moedas": 0
            }

        if players[uid]["moedas"] < 1:
            return await ctx.send("❌ precisa 1 moeda")

        players[uid]["moedas"] -= 1

        save(PLAYERS_FILE, players)

        role = await ctx.guild.create_role(name=nome)

        category = discord.utils.get(
            ctx.guild.categories,
            name="⚔️・FAL CLANS"
        )

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            role: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await ctx.guild.create_text_channel(
            f"🏰-{nome}",
            overwrites=overwrites,
            category=category
        )

        await ctx.author.add_roles(role)

        clans[nome] = {
            "leader": uid,
            "coleader": None,
            "members": [uid],
            "wins": 0,
            "losses": 0,
            "surrenders": 0,
            "history": [],
            "status": "🟢 Ativo",
            "last_activity": datetime.now().isoformat(),
            "max_slots": 5,
            "role_id": role.id,
            "channel_id": channel.id,
            "panel_message": None,
            "logo": None,
            "cor": None,
            "destaque": False,
            "requests": [],
            "war_cooldown": None
        }

        embed = clan_embed(nome, clans[nome])

        msg = await channel.send(embed=embed)

        clans[nome]["panel_message"] = msg.id

        save(CLAN_FILE, clans)

        await ctx.send(f"🏰 Clã {nome} criado!")

    # ================= CLAN INFO =================

    @bot.command()
    async def clan(ctx, nome: str):

        clans = load(CLAN_FILE)

        if nome not in clans:
            return await ctx.send("❌ não existe")

        await ctx.send(
            embed=clan_embed(nome, clans[nome])
        )

    # ================= COLEADER =================

    @bot.command()
    async def setcolider(ctx, nome: str, member: discord.Member):

        clans = load(CLAN_FILE)

        c = clans[nome]

        if str(ctx.author.id) != c["leader"]:
            return await ctx.send("❌ apenas líder")

        c["coleader"] = str(member.id)

        update_activity(c)

        save(CLAN_FILE, clans)

        await update_panel(bot, ctx.guild, nome)

        await ctx.send("🛡 Co-líder definido")

    # ================= REQUEST =================

    @bot.command()
    async def solicitar(ctx, nome: str):

        clans = load(CLAN_FILE)

        if nome not in clans:
            return await ctx.send("❌ não existe")

        c = clans[nome]

        if len(c["members"]) >= c["max_slots"]:
            return await ctx.send("❌ clã cheio")

        if str(ctx.author.id) in c["requests"]:
            return await ctx.send("❌ já solicitou")

        c["requests"].append(str(ctx.author.id))

        update_activity(c)

        save(CLAN_FILE, clans)

        await ctx.send("📩 solicitação enviada")

    # ================= ACCEPT =================

    @bot.command()
    async def aceitar(ctx, nome: str, member: discord.Member):

        clans = load(CLAN_FILE)

        c = clans[nome]

        uid = str(ctx.author.id)

        if uid not in [c["leader"], c["coleader"]]:
            return await ctx.send("❌ sem permissão")

        if len(c["members"]) >= c["max_slots"]:
            return await ctx.send("❌ clã cheio")

        if str(member.id) not in c["requests"]:
            return await ctx.send("❌ sem solicitação")

        c["requests"].remove(str(member.id))

        c["members"].append(str(member.id))

        role = ctx.guild.get_role(c["role_id"])

        await member.add_roles(role)

        update_activity(c)

        save(CLAN_FILE, clans)

        await update_panel(bot, ctx.guild, nome)

        await ctx.send("✅ membro aprovado")

    # ================= REMOVE =================

    @bot.command()
    async def removermembro(ctx, nome: str, member: discord.Member):

        clans = load(CLAN_FILE)

        c = clans[nome]

        uid = str(ctx.author.id)

        if uid not in [c["leader"], c["coleader"]]:
            return await ctx.send("❌ sem permissão")

        if str(member.id) not in c["members"]:
            return await ctx.send("❌ não está")

        c["members"].remove(str(member.id))

        role = ctx.guild.get_role(c["role_id"])

        await member.remove_roles(role)

        update_activity(c)

        save(CLAN_FILE, clans)

        await update_panel(bot, ctx.guild, nome)

        await ctx.send("🚪 removido")

    # ================= SLOT UPGRADE =================

    @bot.command()
    async def upgradeslot(ctx, nome: str):

        clans = load(CLAN_FILE)
        players = load(PLAYERS_FILE)

        c = clans[nome]

        if str(ctx.author.id) != c["leader"]:
            return await ctx.send("❌ apenas líder")

        current = c["max_slots"]

        if current >= 10:
            return await ctx.send("❌ máximo")

        next_slot = current + 1

        price = SLOT_PRICES[next_slot]

        uid = str(ctx.author.id)

        if players[uid]["moedas"] < price:
            return await ctx.send("❌ moedas insuficientes")

        players[uid]["moedas"] -= price

        c["max_slots"] = next_slot

        update_activity(c)

        save(PLAYERS_FILE, players)
        save(CLAN_FILE, clans)

        await update_panel(bot, ctx.guild, nome)

        await ctx.send(f"📦 slot aumentado para {next_slot}")

    # ================= CLAN SHOP =================

    @bot.command()
    async def clancustom(ctx, nome: str, item: str, *, value=None):

        clans = load(CLAN_FILE)
        players = load(PLAYERS_FILE)

        c = clans[nome]

        if str(ctx.author.id) != c["leader"]:
            return await ctx.send("❌ apenas líder")

        if item not in SHOP:
            return await ctx.send("❌ item inválido")

        price = SHOP[item]

        uid = str(ctx.author.id)

        if players[uid]["moedas"] < price:
            return await ctx.send("❌ moedas insuficientes")

        players[uid]["moedas"] -= price

        c[item] = value if value else True

        update_activity(c)

        save(PLAYERS_FILE, players)
        save(CLAN_FILE, clans)

        await update_panel(bot, ctx.guild, nome)

        await ctx.send(f"✨ {item} atualizado")

    # ================= CLAN WAR =================

    @bot.command()
    async def clanwar(ctx, desafiante: str, alvo: str):

        clans = load(CLAN_FILE)
        wars = load(WAR_FILE)

        c1 = clans[desafiante]
        c2 = clans[alvo]

        if c1["war_cooldown"]:

            cooldown = datetime.fromisoformat(c1["war_cooldown"])

            if datetime.now() < cooldown:
                return await ctx.send("⏳ clanwar em cooldown")

        war_id = str(len(wars) + 1)

        wars[war_id] = {
            "challenger": desafiante,
            "enemy": alvo,
            "status": "pending",
            "created": datetime.now().isoformat()
        }

        save(WAR_FILE, wars)

        button_accept = Button(
            label="Aceitar",
            style=discord.ButtonStyle.green
        )

        button_decline = Button(
            label="Desistir",
            style=discord.ButtonStyle.red
        )

        view = View(timeout=None)

        view.add_item(button_accept)
        view.add_item(button_decline)

        async def accept(interaction):

            if str(interaction.user.id) not in [c2["leader"], c2["coleader"]]:
                return await interaction.response.send_message(
                    "❌ sem permissão",
                    ephemeral=True
                )

            analista = ctx.guild.get_role(ANALISTA_ROLE_ID)

            wars[war_id]["status"] = "accepted"

            c1["war_cooldown"] = (
                datetime.now() + timedelta(days=7)
            ).isoformat()

            save(WAR_FILE, wars)
            save(CLAN_FILE, clans)

            await interaction.response.edit_message(
                content=(
                    f"⚔️ WAR ACEITA\n"
                    f"<@&{c1['role_id']}> 🆚 <@&{c2['role_id']}>\n"
                    f"{analista.mention}"
                ),
                view=None
            )

        async def decline(interaction):

            if str(interaction.user.id) not in [c2["leader"], c2["coleader"]]:
                return await interaction.response.send_message(
                    "❌ sem permissão",
                    ephemeral=True
                )

            c2["surrenders"] += 1

            wars[war_id]["status"] = "declined"

            save(CLAN_FILE, clans)
            save(WAR_FILE, wars)

            await interaction.response.edit_message(
                content="❌ guerra recusada",
                view=None
            )

        button_accept.callback = accept
        button_decline.callback = decline

        await ctx.send(
            f"⚔️ {desafiante} desafiou {alvo}",
            view=view
        )

    # ================= RESULT =================

    @bot.command()
    async def resultadowar(ctx, war_id: str, vencedor: str, placar: str):

        clans = load(CLAN_FILE)
        wars = load(WAR_FILE)

        role_ids = [r.id for r in ctx.author.roles]

        if ANALISTA_ROLE_ID not in role_ids:
            return await ctx.send("❌ apenas Analista Técnico")

        if vencedor not in clans:
            return await ctx.send("❌ clã inválido")

        if war_id not in wars:
            return await ctx.send("❌ guerra inválida")

        war = wars[war_id]

        challenger = war["challenger"]
        enemy = war["enemy"]

        if vencedor == challenger:
            clans[challenger]["wins"] += 1
            clans[enemy]["losses"] += 1
        else:
            clans[enemy]["wins"] += 1
            clans[challenger]["losses"] += 1

        clans[vencedor]["history"].append(
            f"🏆 vitória ({placar})"
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
                f"🏆 {vencedor} venceu a guerra ({placar})"
            )

        await update_panel(bot, ctx.guild, challenger)
        await update_panel(bot, ctx.guild, enemy)

        await ctx.send("🏆 resultado registrado")

    # ================= CLAN LEADERBOARD =================

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

        for i, (nome, c) in enumerate(ranking[:10], start=1):

            embed.add_field(
                name=f"{i}º {nome}",
                value=f"🏆 {c['wins']} vitórias",
                inline=False
            )

        await ctx.send(embed=embed)

    # ================= INACTIVITY =================

    @tasks.loop(hours=24)
    async def inactivity_check():

        clans = load(CLAN_FILE)

        now = datetime.now()

        for nome, c in clans.items():

            last = datetime.fromisoformat(c["last_activity"])

            if now - last > timedelta(days=30):

                c["status"] = "💤 Inativo"

        save(CLAN_FILE, clans)

    @bot.event
async def on_ready():
    if not inactivity_check.is_running():
        inactivity_check.start()
