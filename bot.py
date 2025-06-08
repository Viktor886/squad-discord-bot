import os
import discord
from discord.ext import commands
from keep_alive import keep_alive
import aiohttp

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BM_TOKEN = os.getenv("BM_TOKEN")  # BattleMetrics API token

intents = discord.Intents.default()
intents.message_content = True  # Важно для slash-команд
bot = commands.Bot(command_prefix="/", intents=intents)

SERVERS = [
    "31164311",
    "31164422",
    "31161609",
    "31162756",
]

@bot.event
async def on_ready():
    print(f"✅ Бот запущен как {bot.user}")

@bot.command()
async def online(ctx):
    headers = {"Authorization": f"Bearer {BM_TOKEN}"}
    server_data = []

    async with aiohttp.ClientSession() as session:
        for server_id in SERVERS:
            url = f"https://api.battlemetrics.com/servers/{server_id}"
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        server_data.append(f"❌ Ошибка при запросе сервера {server_id}")
                        continue

                    data = await response.json()
                    attributes = data["data"]["attributes"]
                    name = attributes["name"]
                    players = attributes["players"]
                    max_players = attributes["maxPlayers"]
                    current_map = attributes["details"].get("map", "неизвестна")
                    next_map = attributes["details"].get("nextMap", "неизвестна")
                    queue = attributes["details"].get("queue", "-")
                    rank = attributes["rank"]

                    admins = []
                    for player in attributes.get("playersList", []):
                        if player.get("metadata", {}).get("admin"):
                            admins.append(player["name"])
                    if not admins:
                        admins = ["нет админов"]

                    block = (
                        f"**{name}** (Топ: {rank})\n"
                        f"Карта: {current_map} ➜ {next_map}\n"
                        f"Онлайн: {players}/{max_players} (Очередь: {queue})\n"
                        f"Админы:\n" + "\n".join(admins) + "\n" + "—" * 16
                    )
                    server_data.append(block)
            except Exception as e:
                server_data.append(f"❌ Ошибка при запросе сервера {server_id}: {str(e)}")

    result = "\n\n".join(server_data)
    await ctx.send(f"```\n{result}\n```")

# Запуск keep-alive сервера (Railway/Render)
keep_alive()

# Запуск Discord бота
bot.run(DISCORD_TOKEN)

