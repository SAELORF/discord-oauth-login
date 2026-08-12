import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready: {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm Lona, working fine")

bot.run(os.environ["DISCORD_TOKEN"])
