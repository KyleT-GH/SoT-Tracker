# Sea of Thieves Tracker Bot #

This is a bot I decided to make during my free time. I sometimes play a game called ***Sea of thieves***, and recently got asked if it was possible to have a bot keep track of how many ships we sink during a session.

So I decided to "figure it out"

---

# About the Project #

I started my Cybersecurity journey about 6 months ago, and this is the first real project I’ve built from scratch.

I've never created anything like this before — but I wanted to challenge myself.

I used a mix of online resources, documentation, and AI to help build an outline, figure out commands, write code, and host the bot online. This project was a way for me to:

- Practice reading and writing Python
- Debug real code
- Learn to configure and run a Discord bot with security in mind
- Deploy something that runs 24/7 (Availability)

As of now, the bot has multiple working commands and is hosted online 24/7 using [Railway](https://railway.app). I’m excited to finally push it publicly.


# Note: as of now it stores data locally on a .json file. If hosted on Railway a redeploy could cause the data to reset #
---

# Features #

- `!setship <ship name> [@users]` – Assign users to a ship  
- `!sunk` – Log a ship kill (with anti-spam cooldown) 
- `!kill` - Add personal kill only (QoL for crew that doesnt have easy access to discord) 
- `!flag` - Add emissary flags turned in for your ship
- `!gold <amount>` - Add gold eanred for your ship 
- `!leaderboard` – View top ships and players  
- `!myship` – See your ship and personal kill stats
- `!crew` - See ALL crew on a ship  
- `!leave` – Remove yourself from a ship  
- `!resetleaderboard` – Admin-only leaderboard reset  
- `!removekill [number]` – Remove personal kill stats

---

- Setup -

# Requirements #
- Python 3.9+
- `discord.py`, `python-dotenv`

# Local Setup #
```bash 
git clone https://github.com/yourusername/SoT-Tracker.git
cd SoT-Tracker
pip install -r requirements.txt 
```

# Create [.env] file
```DISCORD_BOT_TOKEN=your_token_here```

# Run the bot
```python bot.py```
