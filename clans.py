import discord
from discord.ext import commands, tasks
from discord.ui import View, button
from datetime import datetime, timedelta
import json
import asyncio

CLANS_FILE = "database/clans.json"
WARS_FILE = "database/clan_wars.json"

INFO_CHANNEL = 1504652700921626716
CREATE_CHANNEL = 1504654261664092210
LIST_CHANNEL = 1504655151980609576
REQUEST_CHANNEL = 1504655236839768215
WAR_CHANNEL = 1504655296675577996
RESULT_CHANNEL = 1504655387415023656
INACTIVE_CHANNEL = 1504655449796902912

ANALISTA = 1399531186472226898

MAX_MEMBERS = 5

# =========================
# JSON
# =========================

def load_clans():

    with open(CLANS_FILE, "r") as f:
        return json.load(f)

def save_clans(data):

    with open(CLANS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_wars():

    with open(WARS_FILE, "r") as f:
        return json.load(f)

def save_wars(data):

    with open(WARS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# CLÃ INCORPORADO
# =========================

async def update_clan_panel(bot, guild, clan_name):

    data = load_clans()

    clan = data[clan_name]

    channel = guild.get_channel(
        clan["panel_channel"]
    )

    try:

        mensagem = await canal.fetch_message(
            clan["panel_message"]
        )

    except:

        return

    membros = ""

    for m in clan["members"]:

        membro = guild.get_member(int(m))

        if membro:
            membros += f"• {membro.mention}\n"

    embed = discord.Embed(
        title=f"🏰 {clan_name}",
        color=discord.Color.red()
    )

    embed.add_field(
        name="👑 Líder",
        value=f"<@{clan['leader']}>"
    )

    embed.add_field(
        name="👑 Co-líder",
        value=(
            f"<@{clan['coleader']}>"
            if clan["coleader"]
            else "Nenhum"
        )
    )

    embed.add_field(
        name="👥 Membros",
        value=membros,
        inline=False
    )

    embed.add_field(
        name="🏆 Vitórias",
        value=clan["wins"]
    )

    embed.add_field(
        name="❌ Derrotas",
        value=clan["losses"]
    )

    embed.add_field(
        name="🏳 Desistências",
        value=clan["surrenders"]
    )

    embed.add_field(
        name="📊 Status",
        value=clan["status"]
    )

    embed.add_field(
        name="🕒 Última atividade",
        value=clan["last_activity"],
        inline=False
    )

    if clan["logo"]:

        embed.set_thumbnail(
            url=clan["logo"]
        )

    await mensagem.edit(
        embed=embed
    )

# =========================
# REQUEST VIEW
# =========================

class RequestView(View):

    def __init__(
        self,
        clan_name,
        user_id
    ):

        super().__init__(timeout=None)

        self.clan_name = clan_name
        self.user_id = user_id

    @button(
        label="Aceitar",
        style=discord.ButtonStyle.green
    )
    async def aceitar(
        self,
        interaction,
        button
    ):

        data = load_clans()

        clan = data[self.clan_name]

        if interaction.user.id not in [

            clan["leader"],
            clan["coleader"]

        ]:

            return await interaction.response.send_message(
                "❌ Apenas líder/co-líder.",
                ephemeral=True
            )

        if len(clan["members"]) >= MAX_MEMBERS:

            return await interaction.response.send_message(
                "❌ Clã lotado.",
                ephemeral=True
            )

        clan["members"].append(
            str(self.user_id)
        )

        clan["last_activity"] = datetime.now().strftime(
            "%d/%m/%Y"
        )

        save_clans(data)

        membro = interaction.guild.get_member(
            self.user_id
        )

        role = interaction.guild.get_role(
            clan["role_id"]
        )

        await membro.add_roles(role)

        await update_clan_panel(
            interaction.client,
            interaction.guild,
            self.clan_name
        )

        await interaction.response.edit_message(
            content=(
                f"✅ {membro.mention} "
                f"entrou no clã."
            ),
            embed=None,
            view=None
        )

    @button(
        label="Recusar",
        style=discord.ButtonStyle.red
    )
    async def recusar(
        self,
        interaction,
        button
    ):

        data = load_clans()

        clan = data[self.clan_name]

        if interaction.user.id not in [

            clan["leader"],
            clan["coleader"]

        ]:

            return

        await interaction.response.edit_message(
            content="❌ Solicitação recusada.",
            embed=None,
            view=None
        )

# =========================
# WAR VIEW
# =========================

class WarView(View):

    def __init__(
        self,
        clan1,
        clan2
    ):

        super().__init__(timeout=7200)

        self.clan1 = clan1
        self.clan2 = clan2

    @button(
        label="Aceitar",
        style=discord.ButtonStyle.green
    )
    async def aceitar(
        self,
        interaction,
        button
    ):

        data = load_clans()

        clan = data[self.clan2]

        if interaction.user.id not in [

            clan["leader"],
            clan["coleader"]

        ]:

            return await interaction.response.send_message(
                "❌ Apenas líder/co-líder.",
                ephemeral=True
            )

        analista = interaction.guild.get_role(
            ANALISTA
        )

        embed = discord.Embed(
            title="⚔️ CLANWAR ACEITA",
            description=(
                f"<@&{data[self.clan1]['role_id']}> "
                f"🆚 "
                f"<@&{data[self.clan2]['role_id']}>"
            ),
            color=discord.Color.orange()
        )

        embed.add_field(
            name="🎯 Analista",
            value=analista.mention
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ResultadoView(
                self.clan1,
                self.clan2
            )
        )

    @button(
        label="Desistir",
        style=discord.ButtonStyle.red
    )
    async def desistir(
        self,
        interaction,
        button
    ):

        data = load_clans()

        clan = data[self.clan2]

        if interaction.user.id not in [

            clan["leader"],
            clan["coleader"]

        ]:

            return

        data[self.clan2][
            "surrenders"
        ] += 1

        save_clans(data)

        await interaction.response.edit_message(
            content="❌ Clanwar recusada.",
            embed=None,
            view=None
        )

# =========================
# RESULTADO VIEW
# =========================

class ResultadoView(View):

    def __init__(
        self,
        clan1,
        clan2
    ):

        super().__init__(timeout=None)

        self.clan1 = clan1
        self.clan2 = clan2

    async def finalizar(
        self,
        interaction,
        vencedor,
        perdedor
    ):

        data = load_clans()

        data[vencedor][
            "wins"
        ] += 1

        data[perdedor][
            "losses"
        ] += 1

        historico = (

            f"{datetime.now().strftime('%d/%m/%Y')} "
            f"• {vencedor} venceu "
            f"{perdedor}"
        )

        data[vencedor][
            "history"
        ].append(historico)

        data[perdedor][
            "history"
        ].append(historico)

        save_clans(data)

        await update_clan_panel(
            interaction.client,
            interaction.guild,
            vencedor
        )

        await update_clan_panel(
            interaction.client,
            interaction.guild,
            perdedor
        )

        canal = interaction.guild.get_channel(
            RESULT_CHANNEL
        )

        embed = discord.Embed(
            title="🏆 RESULTADO",
            description=historico,
            color=discord.Color.gold()
        )

        await canal.send(embed=embed)

        await interaction.response.edit_message(
            content="✅ Resultado registrado.",
            embed=None,
            view=None
        )

    @button(
        label="2x0 desafiante",
        style=discord.ButtonStyle.green
    )
    async def r1(
        self,
        interaction,
        button
    ):

        if not discord.utils.get(
            interaction.user.roles,
            id=ANALISTA
        ):

            return

        await self.finalizar(
            interaction,
            self.clan1,
            self.clan2
        )

    @button(
        label="2x1 desafiante",
        style=discord.ButtonStyle.green
    )
    async def r2(
        self,
        interaction,
        button
    ):

        if not discord.utils.get(
            interaction.user.roles,
            id=ANALISTA
        ):

            return

        await self.finalizar(
            interaction,
            self.clan1,
            self.clan2
        )

    @button(
        label="2x0 adversário",
        style=discord.ButtonStyle.red
    )
    async def r3(
        self,
        interaction,
        button
    ):

        if not discord.utils.get(
            interaction.user.roles,
            id=ANALISTA
        ):

            return

        await self.finalizar(
            interaction,
            self.clan2,
            self.clan1
        )

    @button(
        label="2x1 adversário",
        style=discord.ButtonStyle.red
    )
    async def r4(
        self,
        interaction,
        button
    ):

        if not discord.utils.get(
            interaction.user.roles,
            id=ANALISTA
        ):

            return

        await self.finalizar(
            interaction,
            self.clan2,
            self.clan1
        )

# =========================
# SETUP
# =========================

def setup_clans(bot):

    # =========================
    # CREATE CLAN
    # =========================

    @bot.command()
    async def criarcla(
        ctx,
        nome
    ):

        if ctx.channel.id != CREATE_CHANNEL:

            return await ctx.send(
                "❌ Canal incorreto."
            )

        data = load_clans()

        for clan_nome in data:

            if clan_nome.lower() == nome.lower():

                return await ctx.send(
                    "❌ Clã já existe."
                )

        for clan in data.values():

            if str(ctx.author.id) in clan["members"]:

                return await ctx.send(
                    "❌ Você já está em um clã."
                )
        role = await ctx.guild.create_role(
            name=nome
        )

        overwrites = {

            ctx.guild.default_role:
            discord.PermissionOverwrite(
                read_messages=False
            ),

            role:
            discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True
            )
        }

        categoria = discord.utils.get(
            ctx.guild.categories,
            id=1504651417229463613
        )

        canal = await categoria.create_text_channel(

            name=f"🏰・{nome.lower()}",
            overwrites=overwrites
        )

        data[nome] = {

            "leader": str(ctx.author.id),
            "coleader": None,
            "members": [str(ctx.author.id)],
            "wins": 0,
            "losses": 0,
            "surrenders": 0,
            "history": [],
            "status": "🟢 Ativo",
            "last_activity": datetime.now().strftime(
                "%d/%m/%Y"
            ),
            "role_id": role.id,
            "channel_id": canal.id,
            "panel_channel": LIST_CHANNEL,
            "panel_message": None,
            "logo": None
        }

        save_clans(data)

        await ctx.author.add_roles(role)

        embed = discord.Embed(
            title=f"🏰 {nome}",
            description=(
                f"Clã criado por "
                f"{ctx.author.mention}"
            ),
            color=discord.Color.red()
        )

        canal_lista = bot.get_channel(
            LIST_CHANNEL
        )

        msg = await canal_lista.send(
            embed=embed
        )

        data[nome][
            "panel_message"
        ] = msg.id

        save_clans(data)

        await update_clan_panel(
            bot,
            ctx.guild,
            nome
        )

        await ctx.send(
            f"✅ Clã {nome} criado."
        )

    @bot.command()
    async def deletarcla(ctx):

        data = load_clans()

        autor_id = str(ctx.author.id)

        clan_nome = None

        for nome, clan in data.items():

            if clan["leader"] == autor_id:

                clan_nome = nome
                break

        if not clan_nome:

            return await ctx.send(
                "❌ Você não é líder de nenhum clã."
            )

        guild = ctx.guild

        cargo = discord.utils.get(
            guild.roles,
            name=clan_nome
        )

        canal = discord.utils.get(
            guild.channels,
            name=f"🏰・{clan_nome.lower()}"
        )

        if canal:

            await canal.delete()

        if cargo:

            await cargo.delete()

        del data[clan_nome]

        save_clans(data)

        await ctx.send(
            f"🗑️ Clã {clan_nome} deletado."
        )

    # =========================
    # SOLICITAR
    # =========================

    @bot.command()
    async def solicitar(
        ctx,
        clan_name
    ):

        data = load_clans()

        if clan_name not in data:

            return await ctx.send(
                "❌ Clã não encontrado."
            )

        embed = discord.Embed(
            title="📩 Solicitação",
            description=(
                f"{ctx.author.mention} "
                f"quer entrar em "
                f"{clan_name}"
            ),
            color=discord.Color.blurple()
        )

        canal = bot.get_channel(
            REQUEST_CHANNEL
        )

        await canal.send(
            embed=embed,
            view=RequestView(
                clan_name,
                ctx.author.id
            )
        )

        await ctx.send(
            "✅ Solicitação enviada."
        )

    # =========================
    # COLEADER
    # =========================

    @bot.command()
    async def coleader(
        ctx,
        member: discord.Member
    ):

        data = load_clans()

        for clan_name, clan in data.items():

            if clan["leader"] == ctx.author.id:

                clan["coleader"] = member.id

                save_clans(data)

                await update_clan_panel(
                    bot,
                    ctx.guild,
                    clan_name
                )

                return await ctx.send(
                    f"✅ {member.mention} "
                    f"virou co-líder."
                )

    # =========================
    # CLANWAR
    # =========================

    @bot.command()
    async def clanwar(
        ctx,
        clan_name
    ):

        data = load_clans()

        meu_cla = None

        for nome, clan in data.items():

            if str(ctx.author.id) in clan["members"]:

                meu_cla = nome

        if not meu_cla:

            return await ctx.send(
                "❌ Você não possui clã."
            )

        if clan_name not in data:

            return await ctx.send(
                "❌ Clã não existe."
            )

        embed = discord.Embed(
            title="⚔️ CLANWAR",
            description=(

                f"<@&{data[meu_cla]['role_id']}> "
                f"desafiou "
                f"<@&{data[clan_name]['role_id']}>"
            ),
            color=discord.Color.red()
        )

        canal = bot.get_channel(
            WAR_CHANNEL
        )

        await canal.send(
            embed=embed,
            view=WarView(
                meu_cla,
                clan_name
            )
        )

    # =========================
    # LEADERBOARD
    # =========================

    @bot.command()
    async def topclans(ctx):

        data = load_clans()

        ranking = sorted(

            data.items(),

            key=lambda x:
            x[1]["wins"],

            reverse=True
        )

        embed = discord.Embed(
            title="🏆 TOP CLANS",
            color=discord.Color.gold()
        )

        texto = ""

        pos = 1

        for nome, clan in ranking[:10]:

            texto += (

                f"#{pos} • {nome}\n"
                f"🏆 {clan['wins']} vitórias\n\n"
            )

            pos += 1

        embed.description = texto

        await ctx.send(embed=embed)

    # =========================
    # INATIVIDADE
    # =========================

@tasks.loop(hours=24)
async def check_inactive():

        data = load_clans()

        for nome, clan in data.items():

            ultima = datetime.strptime(
                clan["last_activity"],
                "%d/%m/%Y"
            )

            if (
                datetime.now() - ultima
            ).days >= 30:

                clan["status"] = "💤 Inativo"

                save_clans(data)

                canal = bot.get_channel(
                    INACTIVE_CHANNEL
                )

                await canal.send(
                    f"📦 Clã {nome} "
                    f"foi arquivado."
                )

    
