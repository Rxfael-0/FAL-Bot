import discord
from discord import app_commands


# ============================================================
# CONFIGURAÇÃO
# ============================================================

def setup_embed(bot):

    # ========================================================
    # /embed
    # ========================================================

    @bot.tree.command(
        name="embed",
        description="Envia um embed personalizado em um canal."
    )
    @app_commands.describe(
        canal="Canal onde o embed será enviado.",
        cor="Cor do embed.",
        titulo="Título do embed.",
        url="URL da imagem ou 'none' para não usar imagem.",
        mensagem="Mensagem que aparecerá no embed."
    )
    @app_commands.choices(
        cor=[
            app_commands.Choice(
                name="🔴 Vermelho",
                value="vermelho"
            ),
            app_commands.Choice(
                name="🔵 Azul",
                value="azul"
            ),
            app_commands.Choice(
                name="🟢 Verde",
                value="verde"
            ),
            app_commands.Choice(
                name="🟣 Roxo",
                value="roxo"
            ),
            app_commands.Choice(
                name="🟡 Amarelo",
                value="amarelo"
            ),
            app_commands.Choice(
                name="⚫ Preto",
                value="preto"
            ),
            app_commands.Choice(
                name="⚪ Branco",
                value="branco"
            )
        ]
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def embed(
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        cor: app_commands.Choice[str],
        titulo: str,
        url: str,
        mensagem: str
    ):

        # ====================================================
        # PERMISSÃO
        # ====================================================

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Você precisa ser administrador para usar este comando.",
                ephemeral=True
            )

        # ====================================================
        # CORES
        # ====================================================

        cores = {
            "vermelho": discord.Color.red(),
            "azul": discord.Color.blue(),
            "verde": discord.Color.green(),
            "roxo": discord.Color.purple(),
            "amarelo": discord.Color.gold(),
            "preto": discord.Color.dark_theme(),
            "branco": discord.Color.light_grey()
        }

        cor_escolhida = cores.get(
            cor.value,
            discord.Color.red()
        )

        # ====================================================
        # EMBED
        # ====================================================

        emb = discord.Embed(
            title=titulo,
            description=mensagem,
            color=cor_escolhida
        )

        # ====================================================
        # ÍCONE DO SERVIDOR
        # ====================================================

        if interaction.guild and interaction.guild.icon:

            emb.set_author(
                name="FAL Community",
                icon_url=interaction.guild.icon.url
            )

            emb.set_thumbnail(
                url=interaction.guild.icon.url
            )

        # ====================================================
        # IMAGEM
        # ====================================================

        if url.lower() != "none":

            emb.set_image(
                url=url
            )

        # ====================================================
        # FOOTER
        # ====================================================

        if interaction.user.avatar:

            emb.set_footer(
                text=f"Enviado por {interaction.user}",
                icon_url=interaction.user.avatar.url
            )

        else:

            emb.set_footer(
                text=f"Enviado por {interaction.user}"
            )

        # ====================================================
        # ENVIAR
        # ====================================================

        try:

            await canal.send(
                embed=emb
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ Não tenho permissão para enviar mensagens ou embeds nesse canal.",
                ephemeral=True
            )

        except discord.HTTPException:

            return await interaction.response.send_message(
                "❌ Não foi possível enviar o embed. "
                "Verifique se a URL da imagem é válida.",
                ephemeral=True
            )

        # ====================================================
        # CONFIRMAÇÃO
        # ====================================================

        await interaction.response.send_message(
            f"✅ Embed enviado com sucesso em {canal.mention}.",
            ephemeral=True
        )
