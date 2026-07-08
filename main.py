import discord
from discord.ext import commands
import random
import asyncio
import json
import os
import time

TOKEN = "MTUyNDI5NDQyMjQzMzYzMjMzNg.GZ5uCu.ceBNrLJUFDEU0RV7iv9n4ykafeyI1jCMW243ZI"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------ QUESTIONS ------------------

questions = [
    {"question": "What material is needed to craft a diamond pickaxe?", "answer": "diamond"},
    {"question": "What mob explodes when it gets close to players?", "answer": "creeper"},
    {"question": "How many hearts does a Minecraft player have?", "answer": "10"},
    {"question": "What dimension does the Ender Dragon live in?", "answer": "the end"},
    {"question": "What item do you need to make a Nether portal?", "answer": "obsidian"},
]

# ------------------ DATA ------------------

DATA_FILE = "data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        players = json.load(f)
else:
    players = {}


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(players, f, indent=4)


def get_player(user):
    uid = str(user.id)

    if uid not in players:
        players[uid] = {
            "name": user.name,
            "points": 0,
            "xp": 0,
            "level": 1,
            "coins": 0,
            "last_daily": 0
        }

    players[uid]["name"] = user.name
    return players[uid]


# ------------------ EVENTS ------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ------------------ QUIZ ------------------

@bot.command()
async def quiz(ctx):
    q = random.choice(questions)

    await ctx.send(
        f"🎮 **Minecraft Question**\n\n{q['question']}\n\n"
        "First correct answer wins!"
    )

    def check(message):
        return (
            message.channel == ctx.channel
            and not message.author.bot
            and message.content.lower().strip() == q["answer"]
        )

    try:
        winner = await bot.wait_for(
            "message",
            timeout=30,
            check=check
        )

        player = get_player(winner.author)

        player["points"] += 1
        player["xp"] += 10
        player["coins"] += 50

        level_up = False

        while player["xp"] >= player["level"] * 100:
            player["level"] += 1
            level_up = True

        save_data()

        msg = (
            f"🏆 {winner.author.mention} answered correctly!\n"
            f"+1 Point\n"
            f"+10 XP\n"
            f"+50 Coins"
        )

        if level_up:
            msg += f"\n\n🎉 LEVEL UP! You are now Level {player['level']}!"

        await ctx.send(msg)

    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up!\nAnswer: **{q['answer']}**")


# ------------------ LEADERBOARD ------------------

@bot.command()
async def leaderboard(ctx):

    if not players:
        await ctx.send("No scores yet!")
        return

    board = sorted(
        players.values(),
        key=lambda x: x["points"],
        reverse=True
    )

    text = "🏆 **Minecraft Quiz Leaderboard**\n\n"

    for i, p in enumerate(board[:10], 1):
        text += f"{i}. {p['name']} - {p['points']} pts\n"

    await ctx.send(text)


# ------------------ PROFILE ------------------

@bot.command()
async def profile(ctx, member: discord.Member = None):

    member = member or ctx.author

    p = get_player(member)

    xp_needed = p["level"] * 100

    await ctx.send(
        f"👤 **{member.name}**\n\n"
        f"⭐ Level: {p['level']}\n"
        f"📈 XP: {p['xp']}/{xp_needed}\n"
        f"🏆 Points: {p['points']}\n"
        f"💰 Coins: {p['coins']}"
    )


# ------------------ BALANCE ------------------

@bot.command()
async def balance(ctx):

    p = get_player(ctx.author)

    await ctx.send(
        f"💰 {ctx.author.mention}, you have **{p['coins']} coins**!"
    )


# ------------------ DAILY ------------------

@bot.command()
async def daily(ctx):

    p = get_player(ctx.author)

    now = int(time.time())

    if now - p["last_daily"] < 86400:

        remaining = 86400 - (now - p["last_daily"])
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        await ctx.send(
            f"⏳ You already claimed today's reward!\n"
            f"Come back in {hours}h {minutes}m."
        )
        return

    reward = random.randint(100, 300)

    p["coins"] += reward
    p["last_daily"] = now

    save_data()

    await ctx.send(
        f"🎁 Daily Reward!\n\n"
        f"You received **{reward} coins!** 💰"
    )


# ------------------ HELP ------------------

@bot.command()
async def helpme(ctx):

    await ctx.send(
        "**Commands**\n\n"
        "!quiz\n"
        "!leaderboard\n"
        "!profile\n"
        "!balance\n"
        "!daily"
    )


bot.run(TOKEN)