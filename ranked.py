import discord
from discord.ext import commands
from discord.ui import View, button
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import json
import asyncio
import sqlite3

# =========================
# DATABASES
# =========================

DATABASE = "database/database.db"

# =========================
# CANAIS
# =========================

HALL_CHANNEL = 1461218594615459979
TOP15_CHANNEL = 1462527038668673044

RANKED_L1 = 1460670873328550125
RANKED_L2 = 1460671197929935006
RANKED_L3 = 1460671365223940156

LOGS = 1506467756554584114

AMISTOSO_CHANNEL = 1468742231912480798

# =========================
# CARGOS
# =========================

RANKS = {

    "R1": 1460459242413752381,
    "R2": 1460460021564440666,
    "R3": 1460460328948338852,
    "R4": 1460460452810330249,
    "R5": 1460460767290724384,
    "R6": 1460510486075543685,
    "R7": 1460510898174300301,
    "R8": 1460511507124060212,
    "R9": 1460511975007326280,
    "R10": 1460513229997609024,
    "R11": 1460514685110718466,
    "R12": 1460515368069234729
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

WINNER_ROLE = None


# =========================
# SQLITE
# =========================

def connect_db():

    return sqlite3.connect(
        "database/database.db"
)

def setup_database():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        user_id TEXT PRIMARY KEY,
        trofeus INTEGER,
        medalhas INTEGER,
        coins INTEGER,
        wins INTEGER,
        losses INTEGER,
        seasonwins TEXT,
        medals TEXT,
        hall TEXT,
        partidas TEXT
    )
    """)

    conn.commit()
    conn.close()

def create_player(user_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (str(user_id),)
    )

    player = cursor.fetchone()

    if not player:

        cursor.execute("""
        INSERT INTO players VALUES (
            ?, 0, 0, 0, 0, 0,
            '[]', '[]', '[]', '[]'
        )
        """, (str(user_id),))

        conn.commit()

    conn.close()

def get_player(user_id):

    create_player(user_id)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (str(user_id),)
    )

    data = cursor.fetchone()

    conn.close()

    return {
        "trofeus": data[1],
        "medalhas": data[2],
        "coins": data[3],
        "wins": data[4],
        "losses": data[5],
        "seasonwins": json.loads(data[6]),
        "medals": json.loads(data[7]),
        "hall": json.loads(data[8]),
        "partidas": json.loads(data[9])
    }

def update_player(user_id, data):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players SET
    trofeus = ?,
    medalhas = ?,
    coins = ?,
    wins = ?,
    losses = ?,
    seasonwins = ?,
    medals = ?,
    hall = ?,
    partidas = ?
    WHERE user_id = ?
    """, (

        data["trofeus"],
        data["medalhas"],
        data["coins"],
        data["wins"],
        data["losses"],
        json.dumps(data["seasonwins"]),
        json.dumps(data["medals"]),
        json.dumps(data["hall"]),
        json.dumps(data["partidas"]),
        str(user_id)

    ))

    conn.commit()
    conn.close()

# =========================
# RANK SYSTEM
# =========================

def get_rank(t):

    if t <= 99:
        return "R1"

    elif t <= 299:
        return "R2"

    elif t <= 499:
        return "R3"

    elif t <= 699:
        return "R4"

    elif t <= 999:
        return "R5"

    elif t <= 1399:
        return "R6"

    elif t <= 1899:
        return "R7"

    elif t <= 2399:
        return "R8"

    elif t <= 2999:
        return "R9"

    elif t <= 3699:
        return "R10"

    elif t <= 4399:
        return "R11"

    return "R12"

def get_league(t):

    if t < 1000:
        return "L1"

    elif t < 3000:
        return "L2"

    return "L3"

# =========================
# UPDATE ROLES
# =========================

async def update_roles(member, trofeus):

    guild = member.guild

    rank = get_rank(trofeus)
    league = get_league(trofeus)

    for rid in RANKS.values():

        role = guild.get_role(rid)

        if role in member.roles:
            await member.remove_roles(role)

    for lid in LEAGUES.values():

        role = guild.get_role(lid)

        if role in member.roles:
            await member.remove_roles(role)

    await member.add_roles(
        guild.get_role(RANKS[rank])
    )

    await member.add_roles(
        guild.get_role(LEAGUES[league])
    )

# =========================
# LOGS
# =========================

async def send_log(guild, text):

    canal = guild.get_channel(LOGS)

    if canal:

        await canal.send(text)

# =========================
# SETUP
# =========================

def setup_ranked(bot):
    setup_database()


    # =========================
    # PERFIL
    # =========================
    
    @bot.command()
async def perfil(
    ctx,
    member: discord.Member=None
):

    if member is None:
        member = ctx.author

    p = get_player(member.id)

    rank = get_rank(
        p["trofeus"]
    )

    league = get_league(
        p["trofeus"]
    )

    medals = ""

    for medal in p["medals"]:

        medals += f"{medal} "

    if medals == "":
        medals = "Nenhuma."

    hall = ""

    for item in p["hall"][-5:]:

        hall += (
            f"🏆 {item['data']} ┊ "
            f"{item['feito']}\n"
        )

    if hall == "":
        hall = (
            "❌ Nenhum desempenho "
            "registrado."
        )

    embed = discord.Embed(
        title=f"🏆 Perfil de {member.name}",
        color=discord.Color.red()
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.add_field(
        name="🏅 Rank",
        value=f"{rank}"
    )

    embed.add_field(
        name="🏆 Troféus",
        value=f"{p['trofeus']}"
    )

    embed.add_field(
        name="🎖 Medalhas",
        value=f"{p['medalhas']}"
    )

    embed.add_field(
        name="🛡 League",
        value=league
    )

    embed.add_field(
        name="🪙 Coins",
        value=p["coins"]
    )

    embed.add_field(
        name="🏅 Coleção",
        value=medals,
        inline=False
    )

    embed.add_field(
        name="🏁 Hall da fama",
        value=hall,
        inline=False
    )

    await ctx.send(embed=embed)

    # =========================
    # ADD TROFÉU
    # =========================

    @bot.command()
@commands.has_permissions(
    administrator=True
)
async def addtrofeu(
    ctx,
    quantidade: int,
    member: discord.Member
):

    player = get_player(member.id)

    ganhou = quantidade

    if discord.utils.get(
        member.roles,
        id=BOOST_ROLE
    ):

        ganhou *= 2

    player["trofeus"] += ganhou

    if player["trofeus"] >= 5000:

        player["medalhas"] += 1

    player["partidas"].append({

        "resultado": f"+{ganhou}🏆",
        "data": datetime.now().strftime(
            "%d/%m/%Y"
        ),
        "staff": ctx.author.name
    })

    update_player(
        member.id,
        player
    )

    await update_roles(
        member,
        player["trofeus"]
    )

    embed = discord.Embed(
        title="🏆 TROFÉUS ADICIONADOS",
        description=(
            f"{member.mention} "
            f"ganhou +{ganhou}🏆"
        ),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

    await send_log(
        ctx.guild,
        (
            f"➕ {ctx.author} adicionou "
            f"{ganhou}🏆 para "
            f"{member}"
        )
    )
    
    # =========================
    # REMOVE TROFÉU
    # =========================

    @bot.command()
@commands.has_permissions(
    administrator=True
)
async def removetrofeu(
    ctx,
    quantidade: int,
    member: discord.Member
):

    player = get_player(member.id)

    perda = quantidade

    if discord.utils.get(
        member.roles,
        id=PROTECTION_ROLE
    ):

        await ctx.send(
            "🛡 Proteção ativada."
        )

        return

    if discord.utils.get(
        member.roles,
        id=CURSE_ROLE
    ):

        perda *= 2

    player["trofeus"] -= perda

    player["partidas"].append({

        "resultado": f"-{perda}🏆",
        "data": datetime.now().strftime(
            "%d/%m/%Y"
        ),
        "staff": ctx.author.name
    })

    update_player(
        member.id,
        player
    )

    await update_roles(
        member,
        player["trofeus"]
    )

    embed = discord.Embed(
        title="❌ TROFÉUS REMOVIDOS",
        description=(
            f"{member.mention} "
            f"perdeu -{perda}🏆"
        ),
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)

    await send_log(
        ctx.guild,
        (
            f"➖ {ctx.author} removeu "
            f"{perda}🏆 de "
            f"{member}"
        )
    )

    # =========================
    # PARTIDAS
    # =========================

    @bot.command()
async def partidas(
    ctx,
    member: discord.Member=None
):

    if member is None:
        member = ctx.author

    player = get_player(member.id)

    partidas = player["partidas"]

    embed = discord.Embed(
        title="📜 Histórico",
        color=discord.Color.blurple()
    )

    texto = ""

    for p in partidas[-15:]:

        texto += (
            f"{p['resultado']} • "
            f"{p['data']}\n"
        )

    if texto == "":
        texto = "Nenhuma."

    embed.description = texto

    await ctx.send(embed=embed)

    # =========================
    # TOP
    # =========================

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

        img = Image.new(
            "RGB",
            (900, 700),
            color=(15,15,15)
        )

        draw = ImageDraw.Draw(img)

        titulo = ImageFont.truetype(
            "arial.ttf",
            40
        )

        fonte = ImageFont.truetype(
            "arial.ttf",
            28
        )

        draw.text(
            (250,40),
            "🏆 TOP RANKED",
            font=titulo,
            fill=(255,215,0)
        )

        y = 140

        pos = 1

        for user, data in ranking[:10]:

            membro = await bot.fetch_user(
                int(user)
            )

            texto = (
                f"#{pos} "
                f"{membro.name} | "
                f"{data['trofeus']}🏆 | "
                f"{data['medalhas']}🎖"
            )

            draw.text(
                (70,y),
                texto,
                font=fonte,
                fill=(255,255,255)
            )

            y += 50
            pos += 1

        caminho = "leaderboard.png"

        img.save(caminho)

        await ctx.send(
            file=discord.File(caminho)
        )

    # =========================
    # MEDALHAS
    # =========================

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

        create_player(
            players,
            member.id
        )

        players[
            str(member.id)
        ]["medals"].append(
            emoji
        )

        save_players(players)

        await ctx.send(
            f"🏅 Medalha adicionada "
            f"para {member.mention}"
        )

    # =========================
    # AMISTOSO
    # =========================

    amistoso_cooldowns = {}
    amistoso_accept = {}

    class ResultadoView(View):

        def __init__(
            self,
            desafiante,
            desafiado,
            valor
        ):

            super().__init__(timeout=None)

            self.desafiante = desafiante
            self.desafiado = desafiado
            self.valor = valor

            self.votos = {}

        async def verificar(
            self,
            interaction
        ):

            if len(self.votos) < 2:
                return

            votos = list(
                self.votos.values()
            )

            if votos[0] != votos[1]:

                return await interaction.channel.send(
                    "❌ Resultados diferentes."
                )

            vencedor = None
            perdedor = None

            if votos[0] == "desafiante":

                vencedor = self.desafiante
                perdedor = self.desafiado

            else:

                vencedor = self.desafiado
                perdedor = self.desafiante

            players = load_players()

            players[
                str(vencedor.id)
            ]["trofeus"] += self.valor

            players[
                str(perdedor.id)
            ]["trofeus"] -= self.valor

            save_players(players)

            await update_roles(
                vencedor,
                players[
                    str(vencedor.id)
                ]["trofeus"]
            )

            await update_roles(
                perdedor,
                players[
                    str(perdedor.id)
                ]["trofeus"]
            )

            embed = discord.Embed(
                title="🏆 AMISTOSO FINALIZADO",
                description=(
                    f"{vencedor.mention} "
                    f"ganhou +{self.valor}🏆\n\n"
                    f"{perdedor.mention} "
                    f"perdeu -{self.valor}🏆"
                ),
                color=discord.Color.green()
            )

            msg = await interaction.channel.send(
                embed=embed
            )

            await asyncio.sleep(86400)

            try:
                await msg.delete()
            except:
                pass

        @button(
            label="2x0 desafiante",
            style=discord.ButtonStyle.green
        )
        async def r1(
            self,
            interaction,
            button
        ):

            self.votos[
                interaction.user.id
            ] = "desafiante"

            await interaction.response.send_message(
                "✅ Resultado enviado.",
                ephemeral=True
            )

            await self.verificar(
                interaction
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

            self.votos[
                interaction.user.id
            ] = "desafiante"

            await interaction.response.send_message(
                "✅ Resultado enviado.",
                ephemeral=True
            )

            await self.verificar(
                interaction
            )

        @button(
            label="2x0 desafiado",
            style=discord.ButtonStyle.red
        )
        async def r3(
            self,
            interaction,
            button
        ):

            self.votos[
                interaction.user.id
            ] = "desafiado"

            await interaction.response.send_message(
                "✅ Resultado enviado.",
                ephemeral=True
            )

            await self.verificar(
                interaction
            )

        @button(
            label="2x1 desafiado",
            style=discord.ButtonStyle.red
        )
        async def r4(
            self,
            interaction,
            button
        ):

            self.votos[
                interaction.user.id
            ] = "desafiado"

            await interaction.response.send_message(
                "✅ Resultado enviado.",
                ephemeral=True
            )

            await self.verificar(
                interaction
            )

    class AceitarView(View):

        def __init__(
            self,
            desafiante,
            desafiado,
            valor
        ):

            super().__init__(timeout=None)

            self.desafiante = desafiante
            self.desafiado = desafiado
            self.valor = valor

@bot.command()
async def top(ctx):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_id, trofeus, medalhas
    FROM players
    ORDER BY medalhas DESC, trofeus DESC
    LIMIT 10
    """)

    ranking = cursor.fetchall()

    conn.close()

    img = Image.new(
        "RGB",
        (900, 700),
        color=(15,15,15)
    )

    draw = ImageDraw.Draw(img)

    titulo = ImageFont.truetype(
        "arial.ttf",
        40
    )

    fonte = ImageFont.truetype(
        "arial.ttf",
        28
    )

    draw.text(
        (250,40),
        "🏆 TOP RANKED",
        font=titulo,
        fill=(255,215,0)
    )

    y = 140
    pos = 1

    for user_id, trofeus, medalhas in ranking:

        membro = await bot.fetch_user(
            int(user_id)
        )

        texto = (
            f"#{pos} "
            f"{membro.name} | "
            f"{trofeus}🏆 | "
            f"{medalhas}🎖"
        )

        draw.text(
            (70,y),
            texto,
            font=fonte,
            fill=(255,255,255)
        )

        y += 50
        pos += 1

    caminho = "leaderboard.png"

    img.save(caminho)

    await ctx.send(
        file=discord.File(caminho)
    )

# =========================
# MEDALHAS
# =========================

@bot.command()
@commands.has_permissions(
    administrator=True
)
async def add(
    ctx,
    emoji,
    member: discord.Member
):

    player = get_player(member.id)

    player["medals"].append(
        emoji
    )

    update_player(
        member.id,
        player
    )

    await ctx.send(
        f"🏅 Medalha adicionada "
        f"para {member.mention}"
    )

# =========================
# AMISTOSO
# =========================

amistoso_cooldowns = {}
amistoso_accept = {}

class ResultadoView(View):

    def __init__(
        self,
        desafiante,
        desafiado,
        valor
    ):

        super().__init__(timeout=None)

        self.desafiante = desafiante
        self.desafiado = desafiado
        self.valor = valor

        self.votos = {}

    async def verificar(
        self,
        interaction
    ):

        if len(self.votos) < 2:
            return

        votos = list(
            self.votos.values()
        )

        if votos[0] != votos[1]:

            return await interaction.channel.send(
                "❌ Resultados diferentes."
            )

        vencedor = None
        perdedor = None

        if votos[0] == "desafiante":

            vencedor = self.desafiante
            perdedor = self.desafiado

        else:

            vencedor = self.desafiado
            perdedor = self.desafiante

        vencedor_player = get_player(
            vencedor.id
        )

        perdedor_player = get_player(
            perdedor.id
        )

        vencedor_player[
            "trofeus"
        ] += self.valor

        perdedor_player[
            "trofeus"
        ] -= self.valor

        update_player(
            vencedor.id,
            vencedor_player
        )

        update_player(
            perdedor.id,
            perdedor_player
        )

        await update_roles(
            vencedor,
            vencedor_player["trofeus"]
        )

        await update_roles(
            perdedor,
            perdedor_player["trofeus"]
        )

        embed = discord.Embed(
            title="🏆 AMISTOSO FINALIZADO",
            description=(
                f"{vencedor.mention} "
                f"ganhou +{self.valor}🏆\n\n"
                f"{perdedor.mention} "
                f"perdeu -{self.valor}🏆"
            ),
            color=discord.Color.green()
        )

        msg = await interaction.channel.send(
            embed=embed
        )

        await asyncio.sleep(86400)

        try:
            await msg.delete()
        except:
            pass

    @button(
        label="2x0 desafiante",
        style=discord.ButtonStyle.green
    )
    async def r1(
        self,
        interaction,
        button
    ):

        self.votos[
            interaction.user.id
        ] = "desafiante"

        await interaction.response.send_message(
            "✅ Resultado enviado.",
            ephemeral=True
        )

        await self.verificar(
            interaction
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

        self.votos[
            interaction.user.id
        ] = "desafiante"

        await interaction.response.send_message(
            "✅ Resultado enviado.",
            ephemeral=True
        )

        await self.verificar(
            interaction
        )

    @button(
        label="2x0 desafiado",
        style=discord.ButtonStyle.red
    )
    async def r3(
        self,
        interaction,
        button
    ):

        self.votos[
            interaction.user.id
        ] = "desafiado"

        await interaction.response.send_message(
            "✅ Resultado enviado.",
            ephemeral=True
        )

        await self.verificar(
            interaction
        )

    @button(
        label="2x1 desafiado",
        style=discord.ButtonStyle.red
    )
    async def r4(
        self,
        interaction,
        button
    ):

        self.votos[
            interaction.user.id
        ] = "desafiado"

        await interaction.response.send_message(
            "✅ Resultado enviado.",
            ephemeral=True
        )

        await self.verificar(
            interaction
        )

class AceitarView(View):

    def __init__(
        self,
        desafiante,
        desafiado,
        valor
    ):

        super().__init__(timeout=None)

        self.desafiante = desafiante
        self.desafiado = desafiado
        self.valor = valor

    @button(
        label="Aceitar",
        style=discord.ButtonStyle.green
    )
    async def aceitar(
        self,
        interaction,
        button
    ):

        if interaction.user != self.desafiado:
            return

        embed = discord.Embed(
            title="⚔️ AMISTOSO",
            description=(
                f"{self.desafiante.mention} "
                f"🆚 "
                f"{self.desafiado.mention}"
            ),
            color=discord.Color.orange()
        )

        embed.add_field(
            name="🏆 Valor",
            value=f"{self.valor}🏆"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ResultadoView(
                self.desafiante,
                self.desafiado,
                self.valor
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

        if interaction.user != self.desafiado:
            return

        await interaction.response.edit_message(
            content="❌ Amistoso recusado.",
            embed=None,
            view=None
        )

class DesafioView(View):

    def __init__(self):

        super().__init__(timeout=None)

    @button(
        label="Desafiar",
        style=discord.ButtonStyle.blurple
    )
    async def desafiar(
        self,
        interaction,
        button
    ):

        class Modal(
            discord.ui.Modal,
            title="⚔️ Desafio"
        ):

            player = discord.ui.TextInput(
                label="ID do player"
            )

            valor = discord.ui.TextInput(
                label="Valor 10-100"
            )

            async def on_submit(
                self,
                interaction2
            ):

                membro = interaction.guild.get_member(
                    int(self.player.value)
                )

                valor = int(
                    self.valor.value
                )

                embed = discord.Embed(
                    title="⚔️ PROPOSTA",
                    description=(
                        f"{interaction.user.mention} "
                        f"desafiou "
                        f"{membro.mention}"
                    ),
                    color=discord.Color.red()
                )

                embed.add_field(
                    name="🏆 Valor",
                    value=f"{valor}🏆"
                )

                await interaction2.response.send_message(
                    embed=embed,
                    view=AceitarView(
                        interaction.user,
                        membro,
                        valor
                    )
                )

        await interaction.response.send_modal(
            Modal()
        )

@bot.command()
async def amistoso(ctx):

    if ctx.channel.id != AMISTOSO_CHANNEL:

        return await ctx.send(
            "❌ Canal incorreto."
        )

    embed = discord.Embed(
        title="⚔️ SISTEMA AMISTOSO",
        description=(
            "Clique abaixo "
            "para desafiar."
        ),
        color=discord.Color.blurple()
    )

    await ctx.send(
        embed=embed,
        view=DesafioView()
)
