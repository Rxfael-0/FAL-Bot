# queue_system.py

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import time


# ============================================================
# CONFIGURAÇÕES
# ============================================================

MAX_PLAYERS = 4
COOLDOWN_SECONDS = 20 * 60  # 20 minutos

QUEUES = {
    "L1": [],
    "L2": [],
    "L3": []
}

# Guarda o horário em que cada jogador saiu/terminou uma fila
COOLDOWNS = {}

# Evita duas ações simultâneas na mesma fila
QUEUE_LOCK = asyncio.Lock()


# ============================================================
# EMBEDS
# ============================================================

def queue_embed(level: str):
    players = QUEUES[level]

    embed = discord.Embed(
        title=f"🎮 FILA {level}",
        description=(
            f"Entre na fila para encontrar jogadores do **{level}**.\n\n"
            f"👥 **Jogadores:** `{len(players)}/{MAX_PLAYERS}`\n\n"
            "Clique em **Entrar na fila** para participar.\n"
            "Clique em **Sair da fila** para sair."
        ),
        color=discord.Color.blurple()
    )

    if players:
        lista = []

        for i, user_id in enumerate(players, 1):
            lista.append(f"**{i}.** <@{user_id}>")

        embed.add_field(
            name="👤 Jogadores na fila",
            value="\n".join(lista),
            inline=False
        )
    else:
        embed.add_field(
            name="👤 Jogadores na fila",
            value="Ninguém está na fila.",
            inline=False
        )

    embed.set_footer(
        text="FAL-UP • Queue System"
    )

    return embed


# ============================================================
# COOLDOWN
# ============================================================

def get_cooldown(user_id: int):
    """Retorna quantos segundos faltam de cooldown."""

    if user_id not in COOLDOWNS:
        return 0

    remaining = COOLDOWNS[user_id] - time.time()

    if remaining <= 0:
        COOLDOWNS.pop(user_id, None)
        return 0

    return int(remaining)


def format_time(seconds: int):
    minutes = seconds // 60
    secs = seconds % 60

    if minutes > 0:
        return f"{minutes}m {secs}s"

    return f"{secs}s"


# ============================================================
# VIEW DA FILA
# ============================================================

class QueueView(discord.ui.View):

    def __init__(self, level: str):
        super().__init__(timeout=None)
        self.level = level

    # --------------------------------------------------------
    # ENTRAR
    # --------------------------------------------------------

    @discord.ui.button(
        label="Entrar na fila",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="fal_queue_join"
    )
    async def join_queue(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        user_id = interaction.user.id

        async with QUEUE_LOCK:

            # Verifica se já está em alguma fila
            for queue_name, players in QUEUES.items():

                if user_id in players:

                    await interaction.response.send_message(
                        f"❌ Você já está na fila **{queue_name}**.",
                        ephemeral=True
                    )
                    return

            # Verifica cooldown
            cooldown = get_cooldown(user_id)

            if cooldown > 0:

                await interaction.response.send_message(
                    "⏳ Você está em cooldown.\n"
                    f"Tente novamente em **{format_time(cooldown)}**.",
                    ephemeral=True
                )
                return

            # Verifica limite
            if len(QUEUES[self.level]) >= MAX_PLAYERS:

                await interaction.response.send_message(
                    f"❌ A fila **{self.level}** está cheia.",
                    ephemeral=True
                )
                return

            # Adiciona
            QUEUES[self.level].append(user_id)

        # Atualiza painel
        try:
            await interaction.message.edit(
                embed=queue_embed(self.level),
                view=QueueView(self.level)
            )
        except Exception:
            pass

        await interaction.response.send_message(
            f"✅ Você entrou na fila **{self.level}**!",
            ephemeral=True
        )

        # Verifica se completou
        if len(QUEUES[self.level]) >= MAX_PLAYERS:

            await start_match(interaction.guild, self.level)


    # --------------------------------------------------------
    # SAIR
    # --------------------------------------------------------

    @discord.ui.button(
        label="Sair da fila",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        custom_id="fal_queue_leave"
    )
    async def leave_queue(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        user_id = interaction.user.id

        async with QUEUE_LOCK:

            if user_id not in QUEUES[self.level]:

                await interaction.response.send_message(
                    "❌ Você não está nessa fila.",
                    ephemeral=True
                )
                return

            QUEUES[self.level].remove(user_id)

            # Cooldown de saída
            COOLDOWNS[user_id] = time.time() + COOLDOWN_SECONDS

        try:
            await interaction.message.edit(
                embed=queue_embed(self.level),
                view=QueueView(self.level)
            )
        except Exception:
            pass

        await interaction.response.send_message(
            f"👋 Você saiu da fila **{self.level}**.\n"
            f"⏳ Cooldown: **20 minutos**.",
            ephemeral=True
        )


# ============================================================
# INICIAR PARTIDA
# ============================================================

async def start_match(guild: discord.Guild, level: str):

    if guild is None:
        return

    async with QUEUE_LOCK:

        if len(QUEUES[level]) < MAX_PLAYERS:
            return

        players = QUEUES[level][:MAX_PLAYERS]

        # Limpa a fila
        QUEUES[level].clear()

    # --------------------------------------------------------
    # Busca cargo Analista
    # --------------------------------------------------------

    analyst_role = discord.utils.find(
        lambda role: role.name.lower() == "analista",
        guild.roles
    )

    # --------------------------------------------------------
    # Canal de anúncios
    # --------------------------------------------------------

    announcement_channel = None

    possible_names = [
        "fila",
        "filas",
        "queue",
        "queues",
        "ranked",
        "ranked-queue"
    ]

    for channel in guild.text_channels:

        if channel.name.lower() in possible_names:
            announcement_channel = channel
            break

    # Se não encontrou, tenta o primeiro canal onde o bot consegue enviar
    if announcement_channel is None:

        for channel in guild.text_channels:

            permissions = channel.permissions_for(guild.me)

            if permissions.send_messages:

                announcement_channel = channel
                break

    if announcement_channel is None:
        return

    # --------------------------------------------------------
    # Embed da partida
    # --------------------------------------------------------

    mentions = " ".join(f"<@{user_id}>" for user_id in players)

    embed = discord.Embed(
        title="🔥 PARTIDA ENCONTRADA!",
        description=(
            f"A fila **{level}** foi completada!\n\n"
            f"👥 **Jogadores:**\n"
            f"{mentions}\n\n"
            "A partida está pronta para começar."
        ),
        color=discord.Color.green()
    )

    embed.add_field(
        name="🎮 Fila",
        value=level,
        inline=True
    )

    embed.add_field(
        name="👥 Jogadores",
        value=f"{len(players)}/{MAX_PLAYERS}",
        inline=True
    )

    embed.set_footer(
        text="FAL-UP • Ranked Queue"
    )

    content = None

    if analyst_role:
        content = analyst_role.mention

    await announcement_channel.send(
        content=content,
        embed=embed
    )


# ============================================================
# COG
# ============================================================

class QueueSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # /fila
    # ========================================================

    @app_commands.command(
        name="fila",
        description="Mostra ou cria o painel de uma fila."
    )
    @app_commands.describe(
        nivel="Escolha a fila."
    )
    @app_commands.choices(
        nivel=[
            app_commands.Choice(
                name="L1",
                value="L1"
            ),
            app_commands.Choice(
                name="L2",
                value="L2"
            ),
            app_commands.Choice(
                name="L3",
                value="L3"
            )
        ]
    )
    async def fila(
        self,
        interaction: discord.Interaction,
        nivel: app_commands.Choice[str]
    ):

        level = nivel.value

        # ----------------------------------------------------
        # Cargo Analista
        # ----------------------------------------------------

        analyst_role = discord.utils.find(
            lambda role: role.name.lower() == "analista",
            interaction.guild.roles
        )

        # Apenas Analista pode criar o painel
        if analyst_role and analyst_role not in interaction.user.roles:

            await interaction.response.send_message(
                "❌ Você precisa do cargo **Analista** para criar o painel da fila.",
                ephemeral=True
            )
            return

        embed = queue_embed(level)

        await interaction.response.send_message(
            embed=embed,
            view=QueueView(level)
        )


    # ========================================================
    # /filastatus
    # ========================================================

    @app_commands.command(
        name="filastatus",
        description="Mostra o status de todas as filas."
    )
    async def filastatus(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="📊 STATUS DAS FILAS",
            description="Confira o estado atual das filas ranked.",
            color=discord.Color.blurple()
        )

        for level in ["L1", "L2", "L3"]:

            players = QUEUES[level]

            if players:

                lista = "\n".join(
                    f"<@{user_id}>"
                    for user_id in players
                )

            else:
                lista = "Ninguém"

            embed.add_field(
                name=f"🎮 {level} • {len(players)}/{MAX_PLAYERS}",
                value=lista,
                inline=False
            )

        embed.set_footer(
            text="FAL-UP • Queue System"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # ========================================================
    # /sairfila
    # ========================================================

    @app_commands.command(
        name="sairfila",
        description="Sai da fila em que você está."
    )
    async def sairfila(
        self,
        interaction: discord.Interaction
    ):

        user_id = interaction.user.id

        async with QUEUE_LOCK:

            current_queue = None

            for level, players in QUEUES.items():

                if user_id in players:
                    current_queue = level
                    players.remove(user_id)
                    break

            if current_queue is None:

                await interaction.response.send_message(
                    "❌ Você não está em nenhuma fila.",
                    ephemeral=True
                )
                return

            COOLDOWNS[user_id] = time.time() + COOLDOWN_SECONDS

        await interaction.response.send_message(
            f"👋 Você saiu da fila **{current_queue}**.\n"
            "⏳ Você ficará **20 minutos** em cooldown.",
            ephemeral=True
        )


    # ========================================================
    # /minhafila
    # ========================================================

    @app_commands.command(
        name="minhafila",
        description="Mostra a fila em que você está."
    )
    async def minhafila(
        self,
        interaction: discord.Interaction
    ):

        user_id = interaction.user.id

        for level, players in QUEUES.items():

            if user_id in players:

                position = players.index(user_id) + 1

                await interaction.response.send_message(
                    f"🎮 Você está na fila **{level}**.\n"
                    f"📍 Sua posição: **{position}/{MAX_PLAYERS}**.",
                    ephemeral=True
                )
                return

        cooldown = get_cooldown(user_id)

        if cooldown > 0:

            await interaction.response.send_message(
                "❌ Você não está em uma fila.\n"
                f"⏳ Cooldown restante: **{format_time(cooldown)}**.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "❌ Você não está em nenhuma fila.",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

def setup_queue(bot):

    async def setup():

        await bot.add_cog(
            QueueSystem(bot)
        )

        # Registra os botões persistentes
        bot.add_view(QueueView("L1"))
        bot.add_view(QueueView("L2"))
        bot.add_view(QueueView("L3"))

    return setup
