import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import asyncio

queue = []
cooldown = False
matches = {}

def setup_queue(bot):

    @bot.command()
    async def entrarfila(ctx):

        global queue, cooldown

        if cooldown:
            return await ctx.send("⏳ cooldown ativo")

        if ctx.author.id in queue:
            return await ctx.send("já está na fila")

        queue.append(ctx.author.id)

        await ctx.send(f"🎯 entrou na fila ({len(queue)}/4)")

        if len(queue) >= 4:
            await start_match(ctx)

    @bot.command()
    async def sairfila(ctx):
        if ctx.author.id in queue:
            queue.remove(ctx.author.id)

    async def start_match(ctx):
        global queue, cooldown, matches

        players = queue[:4]
        queue = []

        match_id = random.randint(1000, 9999)
        matches[match_id] = players

        mentions = [f"<@{p}>" for p in players]

        await ctx.send(
            f"⚔️ MATCH #{match_id}\n" +
            " VS ".join(mentions)
        )

        cooldown = True
        await asyncio.sleep(1200)
        cooldown = False

    @bot.command()
    async def resultado(ctx):

        global matches

        if not matches:
            return await ctx.send("sem partidas")

        match_id, players = matches.popitem()

        winner = random.choice(players)

        await ctx.send(f"🏁 vencedor: <@{winner}>")
