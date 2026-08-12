import discord
from discord.ext import commands
import os
import threading
import requests
from fastapi import FastAPI
import uvicorn

# ---------- Discord Bot ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready: {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm Lona, working fine")

# ---------- Web Server (OAuth2) ----------
app = FastAPI()

CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI")

@app.get("/")
async def root():
    return {"status": "Lona is running"}

@app.get("/auth/callback")
async def callback(code: str = None):
    if not code:
        return {"error": "No code provided"}

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_res = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    token_json = token_res.json()

    access_token = token_json.get("access_token")
    if not access_token:
        return {"error": "Failed to get token", "details": token_json}

    user_res = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user = user_res.json()

    return {
        "message": "Login successful!",
        "username": user.get("username"),
        "id": user.get("id")
    }

# ---------- Run Both Together ----------
def run_web():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot.run(os.environ["DISCORD_TOKEN"])
