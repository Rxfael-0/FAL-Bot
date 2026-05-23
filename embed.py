import discord
from discord.ext import commands

def setup_embed(bot):

    @bot.command(name="embed")
    @commands.has_permissions(administrator=True)
    async def embed(ctx, canal: discord.TextChannel, cor, titulo, *, mensagem):

        cores = {
            "vermelho": discord.Color.red(),
            "azul": discord.Color.blue(),
            "verde": discord.Color.green(),
            "roxo": discord.Color.purple(),
            "amarelo": discord.Color.gold(),
            "preto": discord.Color.dark_theme(),
            "branco": discord.Color.light_grey()
        }

        emb = discord.Embed(
            title=titulo,
            description=mensagem,
            color=cores.get(cor.lower(), discord.Color.red())
        )

        emb.set_author(
            name="FAL Community",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )

        emb.set_thumbnail(
            url=ctx.guild.icon.url if ctx.guild.icon else None
        )

        emb.set_footer(
            text=f"Enviado por {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )

        await canal.send(embed=emb)

        await ctx.message.add_reaction("✅")
