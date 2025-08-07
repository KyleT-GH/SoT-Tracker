import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
import time

# === Load token from .env === #
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# === File where data is saved === #
DATA_FILE = "ship_data.json"

# === Load or initialize data === #

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "users": {}, 
        "ships": {}, 
        "last_ship_kills": {}  # <-- track last ship kill timestamp #
    }
def ensure_ship(ship_name):
    if ship_name not in data["ships"]:
        data["ships"][ship_name] = {
            "kills": 0,
            "flags": 0,
            "gold": 0
        }

import asyncio
data_lock = asyncio.Lock()

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def safe_save():
    async with data_lock:
        save_data()


def ensure_user(user_id):
    if user_id not in data["users"]:
        data["users"][user_id] = {"kills": 0, "current_ship": None}

data = load_data()

# === Discord bot setup === #
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === Commands === #

@bot.command()
async def setship(ctx, ship_name: str, *members: discord.Member):
    """Assign yourself and optionally others to a ship."""
    user_ids = [ctx.author.id] + [member.id for member in members]

    for uid in user_ids:
        uid_str = str(uid)
        ensure_user(uid_str)
        data["users"][uid_str]["current_ship"] = ship_name

  
    ensure_ship(ship_name)
    await safe_save()

    names = [ctx.author.display_name] + [member.display_name for member in members]
    crew_list = ', '.join(f'**{name}**' for name in names)
    await ctx.send(f"🧭 Ahoy! Crew Formed {crew_list} To Ship **{ship_name}**.")

@bot.command()
async def sunk(ctx, number: int = 1):
    """Add kills for yourself and your current ship."""
    user_id = str(ctx.author.id)
    ensure_user(user_id)
    ship = data["users"][user_id]["current_ship"]

    if not ship:
        await ctx.send("⚠️ You're not assigned to a ship. Use `!setship <ship name>` first.")
        return

    ensure_ship(ship)
    data["users"][user_id]["kills"] += number

    # Check if the ship has already been credited recently
    now = time.time()
    cooldown = 300  # seconds

    last_time = data.get("last_ship_kills", {}).get(ship, 0)
    if now - last_time > cooldown:
        data["ships"][ship]["kills"] += 1
        data.setdefault("last_ship_kills", {})[ship] = now
        await safe_save()
        await ctx.send(f"💥 1 Ship Sent To Davy Jones' Locker! **{ship}** by {ctx.author.display_name}.")
    else:
        await safe_save()
        await ctx.send(f"🧍 {ctx.author.display_name} Sent A Pirate To The Ferry!, Ship Already At The Bottom Of The Sea.")

@bot.command()    
async def kill(ctx, number: int = 1):
    """
    Add personal kill(s) only. Does not affect ship stats or trigger cooldowns. <- QoL to !sunk 
    Usage: !kill [number]
    """
    user_id = str(ctx.author.id)
    ensure_user(user_id)

    if number < 1:
        await ctx.send("⚠️ You must add at least 1 kill.")
        return

    data["users"][user_id]["kills"] += number
    await safe_save()

    await ctx.send(f"💃 {ctx.author.display_name} Just Danced On {number} Pirate's Grave{'s' if number != 1 else ''}!")

@bot.command()
async def flag(ctx, number: int = 1):
    """Track emissary flags turned in for your current ship."""
    user_id = str(ctx.author.id)
    ensure_user(user_id)
    ship = data["users"][user_id]["current_ship"]

    if not ship:
        await ctx.send("⚠️ You're not assigned to a ship. Use `!setship <ship name>` first.")
        return

    ensure_ship(ship)
    data["ships"][ship]["flags"] += number
    await safe_save()
    await ctx.send(f"🚩 {number} Emissary flag{'s' if number != 1 else ''} Handed In For **{ship}**!")

@bot.command()
async def gold(ctx, amount: int):
    """Track gold earned for the ship."""
    user_id = str(ctx.author.id)
    ensure_user(user_id)
    ship = data["users"][user_id]["current_ship"]

    if not ship:
        await ctx.send("⚠️ You're not assigned to a ship. Use `!setship <ship name>` first.")
        return
     
    ensure_ship(ship)
    data["ships"][ship]["gold"] += amount
    await safe_save()
    await ctx.send(f"💰 {amount} Booty Added To **{ship}**'s Total Earning!")


@bot.command()
async def leaderboard(ctx):
    """Show top ships and top players."""
    users = data["users"]
    ships = data["ships"]

    if not users and not ships:
        await ctx.send("No data yet.")
        return

    leaderboard_text = "**🚢 Ship Leaderboard**\n"
    sorted_ships = sorted(ships.items(), key=lambda x: x[1]["kills"], reverse=True)
    for i, (ship, info) in enumerate(sorted_ships[:5], 1):
        leaderboard_text += f"{i}. **{ship}** – {info['kills']} kills, {info['flags']} flags, {info['gold']} gold\n"

    leaderboard_text += "\n**🏴‍☠️ Player Leaderboard**\n"
    sorted_users = sorted(users.items(), key=lambda x: x[1]["kills"], reverse=True)
    for i, (user_id, info) in enumerate(sorted_users[:5], 1):
        try:
            user = await bot.fetch_user(int(user_id))
            name = user.display_name
        except:
            name = "Unknown"
        leaderboard_text += f"{i}. {name} – {info['kills']} kills\n"

    await ctx.send(leaderboard_text)




@bot.command()
async def myship(ctx):
    """Show your current ship and personal kills."""
    user_id = str(ctx.author.id)
    ensure_user(user_id)
    info = data["users"][user_id]
    await ctx.send(f"⛵ You’re on **{info['current_ship'] or 'no ship'}** with **{info['kills']}** total kills.")

@bot.command()
async def crew(ctx, *, ship_name: str):
    """List all users currently assigned to a ship."""
    members = [uid for uid, info in data["users"].items() if info["current_ship"] == ship_name]

    if not members:
        await ctx.send(f"🛳️ No one is currently assigned to **{ship_name}**.")
        return

    names = []
    for uid in members:
        try:
            user = await bot.fetch_user(int(uid))
            names.append(user.display_name)
        except:
            names.append("Unknown")

    crew_list = ', '.join(f'**{name}**' for name in names)
    await ctx.send(f"👥 Crew on **{ship_name}**: {crew_list}")

@bot.command()
async def leave(ctx):
    """Leave your current ship assignment."""
    user_id = str(ctx.author.id)
    ensure_user(user_id)
    data["users"][user_id]["current_ship"] = None
    await safe_save()
    await ctx.send("🚪 You’ve Abandoned Ship!.")

@bot.command()
@commands.has_permissions(administrator=True)
async def resetleaderboard(ctx, scope: str = "all"):
    """
    Reset leaderboard data.
    Usage: !resetleaderboard [all|ships|players]
    """
    global data

    if scope == "all":
        data = {
            "users": {},
            "ships": {},
            "last_ship_kills": {}
        }
        await safe_save()
        await ctx.send("🔄 All leaderboard data has been reset.")
    elif scope == "ships":
        data["ships"] = {}
        data["last_ship_kills"] = {}
        await safe_save()
        await ctx.send("🚢 Ship leaderboard data has been reset.")
    elif scope == "players":
        for user in data["users"].values():
            user["kills"] = 0
        await safe_save()
        await ctx.send("🏴‍☠️ Player kill counts have been reset.")
    else:
        await ctx.send("⚠️ Invalid scope. Use `all`, `ships`, or `players`.")

@bot.command()
async def removekill(ctx, number: int = 1):
    """
    Remove kills from your personal stats (not from ship).
    Usage: !removekill [number]
    """
    user_id = str(ctx.author.id)
    ensure_user(user_id)

    if number < 1:
        await ctx.send("⚠️ You must remove at least 1 kill.")
        return

    current_kills = data["users"][user_id]["kills"]

    if current_kills == 0:
        await ctx.send("🧍 You don't have any kills to remove.")
        return

    removed = min(current_kills, number)
    data["users"][user_id]["kills"] -= removed
    await safe_save()

    await ctx.send(f"❌ Removed {removed} kill(s) from your total. New total: **{data['users'][user_id]['kills']}**")





# === Run the bot === #

bot.run(TOKEN)
