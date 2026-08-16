import discord
from discord.ext import commands


def setup_embed(bot):

    @bot.command(name="embed")
    @commands.has_permissions(administrator=True)
    async def embed(
        ctx,
        canal: discord.TextChannel,
        cor,
        titulo,
        url,
        *,
        mensagem
    ):

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
            cor.lower(),
            discord.Color.red()
        )

        emb = discord.Embed(
            title=titulo,
            description=mensagem,
            color=cor_escolhida
        )

        if ctx.guild.icon:

            emb.set_author(
                name="FAL Community",
                icon_url=ctx.guild.icon.url
            )

            emb.set_thumbnail(
                url=ctx.guild.icon.url
            )

        if url.lower() != "none":

            emb.set_image(
                url=url
            )

        if ctx.author.avatar:

            emb.set_footer(
                text=f"Enviado por {ctx.author}",
                icon_url=ctx.author.avatar.url
            )

        else:

            emb.set_footer(
                text=f"Enviado por {ctx.author}"
            )

        await canal.send(
            embed=emb
        )

        await ctx.message.add_reaction(
            "✅"
        )
