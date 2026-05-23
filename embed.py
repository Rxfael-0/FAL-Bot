import discord
from discord.ext import commands

class Embed(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="embed")
    @commands.has_permissions(administrator=True)
    async def embed(self, ctx, canal: discord.TextChannel, cor, titulo, *, mensagem):

        cores = {
            "vermelho": discord.Color.red(),
            "azul": discord.Color.blue(),
            "verde": discord.Color.green(),
            "roxo": discord.Color.purple(),
            "amarelo": discord.Color.gold(),
            "preto": discord.Color.dark_theme(),
            "branco": discord.Color.light_grey()
        }

        embed = discord.Embed(
            title=titulo,
            description=mensagem,
            color=cores.get(cor.lower(), discord.Color.red())
        )

        embed.set_author(
            name="FAL Community",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )

        embed.set_thumbnail(
            url=ctx.guild.icon.url if ctx.guild.icon else None
        )

        embed.set_footer(
            text=f"Enviado por {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )

        await canal.send(embed=embed)

        await ctx.message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(Embed(bot))
