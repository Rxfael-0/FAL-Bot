import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import View, button
from datetime import datetime
import sqlite3
import json

DATABASE = "database/database.db"


# ============================================================
# SQLITE
# ============================================================

def connect_db():
    return sqlite3.connect(DATABASE)


def setup_clan_database():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clans (
        name TEXT PRIMARY KEY,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()


def load_clans():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, data FROM clans"
    )

    rows = cursor.fetchall()

    conn.close()

    data = {}

    for name, clan_data in rows:
        try:
            data[name] = json.loads(clan_data)
        except json.JSONDecodeError:
            continue

    return data


def save_clans(data):

    conn = connect_db()
    cursor = conn.cursor()

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
    conn.close()


# ============================================================
# CANAIS
# ============================================================

INFO_CHANNEL = 1504652700921626716
CREATE_CHANNEL = 1504654261664092210
LIST_CHANNEL = 1504655151980609576
REQUEST_CHANNEL = 1504655236839768215
WAR_CHANNEL = 1504655296675577996
RESULT_CHANNEL = 1504655387415023656
INACTIVE_CHANNEL = 1504655449796902912

CLAN_CATEGORY = 1504651417229463613


# ============================================================
# CARGOS
# ============================================================

ANALISTA = 1399531186472226898
LEADER_ROLE = 1399181565162033243

MAX_MEMBERS = 5


# ============================================================
# ATUALIZAR PAINEL
# ============================================================

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
        value=str(clan["wins"])
    )

    embed.add_field(
        name="❌ Derrotas",
        value=str(clan["losses"])
    )

    embed.add_field(
        name="🏳 Desistências",
        value=str(clan["surrenders"])
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


# ============================================================
# REQUEST VIEW
# ============================================================

class RequestView(View):

    def __init__(
        self,
        clan_name,
        user_id
    ):

        super().__init__(
            timeout=None
        )

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

            try:
                await membro.add_roles(role)
            except discord.Forbidden:
                pass

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


# ============================================================
# WAR VIEW
# ============================================================

class WarView(View):

    def __init__(
        self,
        clan1,
        clan2
    ):

        super().__init__(
            timeout=7200
        )

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


# ============================================================
# REGISTRAR RESULTADO
# ============================================================

class RegistrarResultadoView(View):

    def __init__(
        self,
        clan1,
        clan2
    ):

        super().__init__(
            timeout=None
        )

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


# ============================================================
# RESULTADO VIEW
# ============================================================

class ResultadoView(View):

    def __init__(
        self,
        clan1,
        clan2
    ):

        super().__init__(
            timeout=None
        )

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

    def is_analista(
        self,
        interaction
    ):

        return discord.utils.get(
            interaction.user.roles,
            id=ANALISTA
        ) is not None

    @button(
        label="2x0 desafiante",
        style=discord.ButtonStyle.green
    )
    async def r1(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not self.is_analista(interaction):

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

        if not self.is_analista(interaction):

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

        if not self.is_analista(interaction):

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

        if not self.is_analista(interaction):

            return await interaction.response.send_message(
                "❌ Apenas analistas podem registrar.",
                ephemeral=True
            )

        await self.finalizar(
            interaction,
            self.clan2,
            self.clan1
        )


# ============================================================
# COG
# ============================================================

class Clans(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        setup_clan_database()

        if not check_inactive.is_running():

            check_inactive.start()


    # ========================================================
    # /criarcla
    # ========================================================

    @app_commands.command(
        name="criarcla",
        description="Cria um novo clã."
    )
    @app_commands.describe(
        nome="Nome do clã."
    )
    async def criarcla(
        self,
        interaction: discord.Interaction,
        nome: str
    ):

        if interaction.channel_id != CREATE_CHANNEL:

            return await interaction.response.send_message(
                "❌ Este comando só pode ser usado no canal correto.",
                ephemeral=True
            )

        nome = nome.strip()

        if not nome:

            return await interaction.response.send_message(
                "❌ Informe um nome válido.",
                ephemeral=True
            )

        if len(nome) > 30:

            return await interaction.response.send_message(
                "❌ O nome do clã pode ter no máximo 30 caracteres.",
                ephemeral=True
            )

        data = load_clans()

        for clan_nome in data:

            if clan_nome.lower() == nome.lower():

                return await interaction.response.send_message(
                    "❌ Clã já existe.",
                    ephemeral=True
                )

        for clan in data.values():

            if str(interaction.user.id) in clan["members"]:

                return await interaction.response.send_message(
                    "❌ Você já está em um clã.",
                    ephemeral=True
                )

        await interaction.response.defer()

        role = await interaction.guild.create_role(
            name=nome
        )

        overwrites = {

            interaction.guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),

            role:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),

            interaction.user:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        categoria = discord.utils.get(
            interaction.guild.categories,
            id=CLAN_CATEGORY
        )

        canal = await interaction.guild.create_text_channel(
            name=f"🏰・{nome.lower()}",
            category=categoria,
            overwrites=overwrites
        )

        data[nome] = {

            "leader": str(interaction.user.id),
            "coleader": None,

            "members": [
                str(interaction.user.id)
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

        try:
            await interaction.user.add_roles(role)
        except discord.Forbidden:
            pass

        embed = discord.Embed(
            title=f"🏰 {nome}",
            description=(
                f"Clã criado por "
                f"{interaction.user.mention}"
            ),
            color=discord.Color.red()
        )

        canal_lista = self.bot.get_channel(
            LIST_CHANNEL
        )

        if not canal_lista:

            return await interaction.followup.send(
                "⚠️ Clã criado, mas o canal de lista não foi encontrado."
            )

        msg = await canal_lista.send(
            embed=embed
        )

        data = load_clans()

        if nome in data:

            data[nome]["panel_message"] = msg.id

            save_clans(data)

        await update_clan_panel(
            self.bot,
            interaction.guild,
            nome
        )

        await interaction.followup.send(
            f"✅ Clã **{nome}** criado."
        )


    # ========================================================
    # /deletarcla
    # ========================================================

    @app_commands.command(
        name="deletarcla",
        description="Deleta um clã."
    )
    @app_commands.describe(
        nome="Nome do clã que deseja deletar."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def deletarcla(
        self,
        interaction: discord.Interaction,
        nome: str
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Você precisa ser administrador.",
                ephemeral=True
            )

        data = load_clans()

        clan_real = None

        for clan_nome in data:

            if clan_nome.lower() == nome.lower():

                clan_real = clan_nome
                break

        if not clan_real:

            return await interaction.response.send_message(
                "❌ Clã não encontrado.",
                ephemeral=True
            )

        guild = interaction.guild

        cargo = guild.get_role(
            data[clan_real]["role_id"]
        )

        canal = guild.get_channel(
            data[clan_real]["channel_id"]
        )

        if canal:

            try:
                await canal.delete()
            except discord.Forbidden:
                pass

        if cargo:

            try:
                await cargo.delete()
            except discord.Forbidden:
                pass

        del data[clan_real]

        save_clans(data)

        await interaction.response.send_message(
            f"🗑️ Clã **{clan_real}** deletado."
        )


    # ========================================================
    # /coleader
    # ========================================================

    @app_commands.command(
        name="coleader",
        description="Define o co-líder do seu clã."
    )
    @app_commands.describe(
        membro="Membro que será o co-líder."
    )
    async def coleader(
        self,
        interaction: discord.Interaction,
        membro: discord.Member
    ):

        data = load_clans()

        for clan_name, clan in data.items():

            if clan["leader"] == str(interaction.user.id):

                if str(membro.id) not in clan["members"]:

                    return await interaction.response.send_message(
                        "❌ O usuário precisa estar no seu clã.",
                        ephemeral=True
                    )

                clan["coleader"] = str(membro.id)

                save_clans(data)

                await update_clan_panel(
                    self.bot,
                    interaction.guild,
                    clan_name
                )

                return await interaction.response.send_message(
                    f"✅ {membro.mention} virou co-líder."
                )

        await interaction.response.send_message(
            "❌ Você não é líder de nenhum clã.",
            ephemeral=True
        )


    # ========================================================
    # /solicitar
    # ========================================================

    @app_commands.command(
        name="solicitar",
        description="Solicita entrada em um clã."
    )
    @app_commands.describe(
        clan="Nome do clã que deseja entrar."
    )
    async def solicitar(
        self,
        interaction: discord.Interaction,
        clan: str
    ):

        data = load_clans()

        clan_real = None

        for nome in data:

            if nome.lower() == clan.lower():

                clan_real = nome
                break

        if not clan_real:

            return await interaction.response.send_message(
                "❌ Clã não encontrado.",
                ephemeral=True
            )

        for clan_data in data.values():

            if str(interaction.user.id) in clan_data["members"]:

                return await interaction.response.send_message(
                    "❌ Você já está em um clã.",
                    ephemeral=True
                )

        if len(data[clan_real]["members"]) >= MAX_MEMBERS:

            return await interaction.response.send_message(
                "❌ Este clã já está cheio.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="📩 Solicitação",
            description=(
                f"{interaction.user.mention} "
                f"quer entrar em **{clan_real}**."
            ),
            color=discord.Color.blurple()
        )

        canal = self.bot.get_channel(
            REQUEST_CHANNEL
        )

        if not canal:

            return await interaction.response.send_message(
                "❌ Canal de solicitações não encontrado.",
                ephemeral=True
            )

        await canal.send(
            content=(
                f"<@&{data[clan_real]['role_id']}>"
            ),
            embed=embed,
            view=RequestView(
                clan_real,
                interaction.user.id
            )
        )

        await interaction.response.send_message(
            "✅ Solicitação enviada.",
            ephemeral=True
        )


    # ========================================================
    # /clanwar
    # ========================================================

    @app_commands.command(
        name="clanwar",
        description="Desafia outro clã para uma ClanWar."
    )
    @app_commands.describe(
        clan="Nome do clã que deseja desafiar."
    )
    async def clanwar(
        self,
        interaction: discord.Interaction,
        clan: str
    ):

        data = load_clans()

        meu_cla = None

        for nome, clan_data in data.items():

            if str(interaction.user.id) in clan_data["members"]:

                meu_cla = nome
                break

        if not meu_cla:

            return await interaction.response.send_message(
                "❌ Você não possui clã.",
                ephemeral=True
            )

        clan_real = None

        for nome in data:

            if nome.lower() == clan.lower():

                clan_real = nome
                break

        if not clan_real:

            return await interaction.response.send_message(
                "❌ Clã não existe.",
                ephemeral=True
            )

        if meu_cla == clan_real:

            return await interaction.response.send_message(
                "❌ Você não pode desafiar seu próprio clã.",
                ephemeral=True
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

        canal = self.bot.get_channel(
            WAR_CHANNEL
        )

        if not canal:

            return await interaction.response.send_message(
                "❌ Canal de ClanWar não encontrado.",
                ephemeral=True
            )

        await canal.send(
            embed=embed,
            view=WarView(
                meu_cla,
                clan_real
            )
        )

        await interaction.response.send_message(
            "✅ Desafio enviado.",
            ephemeral=True
        )


    # ========================================================
    # /topclans
    # ========================================================

    @app_commands.command(
        name="topclans",
        description="Mostra os melhores clãs."
    )
    async def topclans(
        self,
        interaction: discord.Interaction
    ):

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

        for pos, (nome, clan) in enumerate(
            ranking[:10],
            1
        ):

            texto += (
                f"**#{pos} • {nome}**\n"
                f"🏆 {clan['wins']} vitórias\n\n"
            )

        if texto == "":

            texto = "❌ Nenhum clã criado."

        embed.description = texto

        await interaction.response.send_message(
            embed=embed
        )


# ============================================================
# CLÃS INATIVOS
# ============================================================

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


# ============================================================
# SETUP
# ============================================================

async def setup_clans(bot):

    setup_clan_database()

    await bot.add_cog(
        Clans(bot)
    )
