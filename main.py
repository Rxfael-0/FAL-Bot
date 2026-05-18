import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot ligado como {bot.user}')

@bot.command()
async def perfil(ctx):
    await ctx.send(f'{ctx.author.mention} seu perfil funcionou.')

bot.run(os.getenv("TOKEN"))
