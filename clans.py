```python
import discord
from discord.ext import commands, tasks
from discord.ui import View, button
from datetime import datetime
import sqlite3
import json

DATABASE = "database/database.db"

# =========================
# SQLITE
# =========================

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clans (
    name TEXT PRIMARY KEY,
    data TEXT
)
""")

conn.commit()


def load_clans():

    cursor.execute(
        "SELECT name, data FROM clans"
    )

    rows = cursor.fetchall()

    data = {}

    for name, clan_data in rows:
        data[name] = json.loads(clan_data)

    return data


def save_clans(data):

    cursor.execute(
        "DELETE FROM clans"
    )

    for name, clan_data in data.items():

        cursor.execute(
            "INSERT INTO clans (name, data) VALUES (?, ?)",
            (
                name,
                json.dumps(clan_data)
            )
        )

    conn.commit()


# =========================
# CANAIS
# =========================

INFO_CHANNEL = 1504652700921626716
CREATE_CHANNEL = 1504654261664092210
LIST_CHANNEL = 1504655151980609576
REQUEST_CHANNEL = 1504655236839768215
WAR_CHANNEL = 1504655296675577996
RESULT_CHANNEL = 1504655387415023656
INACTIVE_CHANNEL = 1504655449796902912

CLAN_CATEGORY = 1504651417229463613

# =========================
# CARGOS
# =========================

ANALISTA = 1399531186472226898
LEADER_ROLE = 1399181565162033243

MAX_MEMBERS = 5


# =========================
# ATUALIZAR PAINEL
# =========================

async def update_clan_panel(
    bot,
    guild,
    clan_name
):

    data = load_clans()

    if clan_name not in data:
        return

    clan = data[clan_name]

    channel = guild.get_channel(
        clan["panel_channel"]
    )

    if not channel:
        return

    try:

        mensagem = await channel.fetch_message(
            clan["panel_message"]
        )

    except Exception:

        return

    membros = ""

    for membro_id in clan["members"]:

        membro = guild.get_member(
            int(membro_id)
        )

        if membro:

            membros += (
                f"• {membro.mention}\n"
            )

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
        value=membros if membros else "Nenhum",
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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = load_clans()

        if self.clan_name not in data:

            return await interaction.response.send_message(
                "❌ Clã não existe.",
                ephemeral=True
            )

        clan = data[self.clan_name]

        if interaction.user.id not in [

            int(clan["leader"]),

            int(clan["coleader"])
            if clan["coleader"]
            else 0

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

        for c in data.values():

            if str(self.user_id) in c["members"]:

                return await interaction.response.send_message(
                    "❌ Usuário já está em um clã.",
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

        if not membro:

            return await interaction.response.send_message(
                "❌ Usuário não encontrado no servidor.",
                ephemeral=True
            )

        role = interaction.guild.get_role(
            clan["role_id"]
        )

        if role:

            await membro.add_roles(role)

        await update_clan_panel(
            interaction.client,
            interaction.guild,
            self.clan_name
        )

        await interaction.response.edit_message(
            content=(
                f"✅ {membro.mention} entrou no clã."
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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = load_clans()

        if self.clan1 not in data or self.clan2 not in data:

            return await interaction.response.send_message(
                "❌ Um dos clãs não existe mais.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="⚔️ CLANWAR ACEITA",
            description=(
                f"{self.clan1} 🆚 {self.clan2}"
            ),
            color=discord.Color.orange()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RegistrarResultadoView(
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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = load_clans()

        if self.clan2 in data:

            data[self.clan2]["surrenders"] += 1
            save_clans(data)

        await interaction.response.edit_message(
            content="❌ Clanwar recusada.",
            embed=None,
            view=None
        )


# =========================
# REGISTRAR RESULTADO
# =========================

class RegistrarResultadoView(View):

    def __init__(
        self,
        clan1,
        clan2
    ):

        super().__init__(timeout=None)

        self.clan1 = clan1
        self.clan2 = clan2

    @button(
        label="Registrar Resultado",
        style=discord.ButtonStyle.blurple
    )
    async def registrar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            view=ResultadoView(
                self.clan1,
                self.clan2
            )
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

        if vencedor not in data or perdedor not in data:

            return await interaction.response.send_message(
                "❌ Um dos clãs não existe mais.",
                ephemeral=True
            )

        data[vencedor]["wins"] += 1
        data[perdedor]["losses"] += 1

        historico = (
            f"{datetime.now().strftime('%d/%m/%Y')} "
            f"• {vencedor} venceu {perdedor}"
        )

        data[vencedor]["history"].append(
            historico
        )

        data[perdedor]["history"].append(
            historico
        )

        data[vencedor]["last_activity"] = datetime.now().strftime(
            "%d/%m/%Y"
        )

        data[perdedor]["last_activity"] = datetime.now().strftime(
            "%d/%m/%Y"
        )

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

        if canal:

            await canal.send(
                embed=embed
            )

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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not discord.utils.get(
            interaction.user.roles,
            id=ANALISTA
        ):

            return await interaction.response.send_message(
                "❌ Apenas analistas podem registrar.",
                ephemeral=True
            )

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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not discord.utils.get(
            interaction.user.roles,
            id=ANALISTA
        ):

            return await interaction.response.send_message(
                "❌ Apenas analistas podem registrar.",
                ephemeral=True
            )

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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not discord.utils.get(
            interaction.user.roles,
            id=ANALISTA
        ):

            return await interaction.response.send_message(
                "❌ Apenas analistas podem registrar.",
                ephemeral=True
            )

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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not discord.utils.get(
            interaction.user.roles,
            id=ANALISTA
        ):

            return await interaction.response.send_message(
                "❌ Apenas analistas podem registrar.",
                ephemeral=True
            )

        await self.finalizar(
            interaction,
            self.clan2,
            self.clan1
        )


# =========================
# SETUP
# =========================

def setup_clans(bot):

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
                view_channel=False
            ),

            role:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),

            ctx.author:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        categoria = discord.utils.get(
            ctx.guild.categories,
            id=CLAN_CATEGORY
        )

        canal = await ctx.guild.create_text_channel(
            name=f"🏰・{nome.lower()}",
            category=categoria,
            overwrites=overwrites
        )

        data[nome] = {

            "leader": str(ctx.author.id),
            "coleader": None,

            "members": [
                str(ctx.author.id)
            ],

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

        await ctx.author.add_roles(
            role
        )

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

        if not canal_lista:

            return await ctx.send(
                "⚠️ Clã criado, mas o canal de lista não foi encontrado."
            )

        msg = await canal_lista.send(
            embed=embed
        )

        data[nome]["panel_message"] = msg.id

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
    async def deletarcla(
        ctx,
        nome
    ):

        if not discord.utils.get(
            ctx.author.roles,
            id=LEADER_ROLE
        ):

            return await ctx.send(
                "❌ Sem permissão."
            )

        data = load_clans()

        clan_real = None

        for clan_nome in data:

            if clan_nome.lower() == nome.lower():

                clan_real = clan_nome
                break

        if not clan_real:

            return await ctx.send(
                "❌ Clã não encontrado."
            )

        guild = ctx.guild

        cargo = guild.get_role(
            data[clan_real]["role_id"]
        )

        canal = guild.get_channel(
            data[clan_real]["channel_id"]
        )

        if canal:

            await canal.delete()

        if cargo:

            await cargo.delete()

        del data[clan_real]

        save_clans(data)

        await ctx.send(
            f"🗑️ Clã {clan_real} deletado."
        )

    @bot.command()
    async def coleader(
        ctx,
        member: discord.Member
    ):

        data = load_clans()

        for clan_name, clan in data.items():

            if clan["leader"] == str(ctx.author.id):

                clan["coleader"] = str(member.id)

                save_clans(data)

                await update_clan_panel(
                    bot,
                    ctx.guild,
                    clan_name
                )

                return await ctx.send(
                    f"✅ {member.mention} virou co-líder."
                )

        await ctx.send(
            "❌ Você não é líder de nenhum clã."
        )

    @bot.command()
    async def solicitar(
        ctx,
        clan_name
    ):

        data = load_clans()

        clan_real = None

        for nome in data:

            if nome.lower() == clan_name.lower():

                clan_real = nome
                break

        if not clan_real:

            return await ctx.send(
                "❌ Clã não encontrado."
            )

        for clan in data.values():

            if str(ctx.author.id) in clan["members"]:

                return await ctx.send(
                    "❌ Você já está em um clã."
                )

        embed = discord.Embed(
            title="📩 Solicitação",
            description=(
                f"{ctx.author.mention} "
                f"quer entrar em {clan_real}"
            ),
            color=discord.Color.blurple()
        )

        canal = bot.get_channel(
            REQUEST_CHANNEL
        )

        if not canal:

            return await ctx.send(
                "❌ Canal de solicitações não encontrado."
            )

        await canal.send(
            content=(
                f"<@&{data[clan_real]['role_id']}>"
            ),
            embed=embed,
            view=RequestView(
                clan_real,
                ctx.author.id
            )
        )

        await ctx.send(
            "✅ Solicitação enviada."
        )

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
                break

        if not meu_cla:

            return await ctx.send(
                "❌ Você não possui clã."
            )

        clan_real = None

        for nome in data:

            if nome.lower() == clan_name.lower():

                clan_real = nome
                break

        if not clan_real:

            return await ctx.send(
                "❌ Clã não existe."
            )

        if meu_cla == clan_real:

            return await ctx.send(
                "❌ Você não pode desafiar seu próprio clã."
            )

        embed = discord.Embed(
            title="⚔️ CLANWAR",
            description=(
                f"<@&{data[meu_cla]['role_id']}> "
                f"desafiou "
                f"<@&{data[clan_real]['role_id']}>"
            ),
            color=discord.Color.red()
        )

        canal = bot.get_channel(
            WAR_CHANNEL
        )

        if not canal:

            return await ctx.send(
                "❌ Canal de ClanWar não encontrado."
            )

        await canal.send(
            embed=embed,
            view=WarView(
                meu_cla,
                clan_real
            )
        )

        await ctx.send(
            "✅ Desafio enviado."
        )

    @bot.command()
    async def topclans(ctx):

        data = load_clans()

        ranking = sorted(
            data.items(),
            key=lambda x: x[1]["wins"],
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

        if texto == "":

            texto = "❌ Nenhum clã criado."

        embed.description = texto

        await ctx.send(
            embed=embed
        )


# =========================
# CLÃS INATIVOS
# =========================

@tasks.loop(hours=24)
async def check_inactive():

    data = load_clans()

    alterado = False

    for nome, clan in data.items():

        try:

            ultima = datetime.strptime(
                clan["last_activity"],
                "%d/%m/%Y"
            )

        except (KeyError, ValueError):

            continue

        if (
            datetime.now() - ultima
        ).days >= 30:

            if clan["status"] != "💤 Inativo":

                clan["status"] = "💤 Inativo"
                alterado = True

    if alterado:

        save_clans(data)
```
