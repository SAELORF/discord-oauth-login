import discord
from discord.ext import commands
import os
import threading
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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
    await ctx.send("Hello! I'm Lion, working fine")

# ---------- Web Server ----------
app = FastAPI()

CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI")

LOGIN_URL = (
    f"https://discord.com/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=identify%20guilds"
)

@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lion Bot</title>
        <style>
            body {{
                background: #0f0f14;
                color: white;
                font-family: 'Segoe UI', Tahoma, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                text-align: center;
                padding: 20px;
            }}
            h1 {{
                font-size: 2.2rem;
                margin-bottom: 10px;
            }}
            p {{
                color: #aaa;
                margin-bottom: 30px;
            }}
            a.login-btn {{
                background: #5865F2;
                color: white;
                padding: 15px 35px;
                border-radius: 12px;
                text-decoration: none;
                font-size: 1.1rem;
                font-weight: bold;
                transition: 0.2s;
            }}
            a.login-btn:hover {{
                background: #4752c4;
            }}
        </style>
    </head>
    <body>
        <h1>🦁 Lion Bot</h1>
        <p>بوت ديسكورد بسيط للتجربة والتعلم</p>
        <a class="login-btn" href="{LOGIN_URL}">تسجيل الدخول عبر ديسكورد</a>
    </body>
    </html>
    """

@app.get("/auth/callback", response_class=HTMLResponse)
async def callback(code: str = None):
    if not code:
        return "<h2>خطأ: ما وصل كود من ديسكورد</h2>"

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
        return f"<h2>فشل تسجيل الدخول</h2><pre>{token_json}</pre>"

    user_res = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user = user_res.json()
    username = user.get("username", "مستخدم")
    avatar = user.get("avatar")
    user_id = user.get("id")
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png" if avatar else ""

    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تم تسجيل الدخول</title>
        <style>
            body {{
                background: #0f0f14;
                color: white;
                font-family: 'Segoe UI', Tahoma, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                text-align: center;
            }}
            img {{
                width: 90px;
                height: 90px;
                border-radius: 50%;
                margin-bottom: 15px;
            }}
            h2 {{ color: #57F287; }}
        </style>
    </head>
    <body>
        {f'<img src="{avatar_url}">' if avatar_url else ''}
        <h2>✅ تم تسجيل الدخول بنجاح</h2>
        <p>أهلاً {username}!</p>
    </body>
    </html>
    """

# ---------- Run Both Together ----------
def run_web():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot.run(os.environ["DISCORD_TOKEN"])
