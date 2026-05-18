SHOP = {
    "boost": 4,
    "protecao": 3,
    "maldição": 2
}

def setup_shop(bot):

    @bot.command()
    async def loja(ctx):

        text = "🏪 LOJA\n\n"

        for k, v in SHOP.items():
            text += f"{k} - {v} 🪙\n"

        await ctx.send(text)
