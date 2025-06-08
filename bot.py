import discord
from discord.ext import commands
import aiohttp
import os
from keep_alive import keep_alive  # чтобы бот не отключался

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BM_TOKEN = os.getenv("BM_TOKEN")
BM_TOKEN_FLAGS = os.getenv("BM_TOKEN_FLAGS")

SERVERS = [
    "31164311",
    "31164422",
    "31161609",
    "31162756",
]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Бот запущен как {bot.user}')

@bot.command()
async def online(ctx):
    headers = {"Authorization": f"Bearer {BM_TOKEN_FLAGS or BM_TOKEN}"}
    result = []

    async with aiohttp.ClientSession() as session:
        for server_id in SERVERS:
            try:
                url = f"https://api.battlemetrics.com/servers/{server_id}?include=player"
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        result.append(f"❌ Ошибка при запросе сервера {server_id}")
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

                    # Получение админов
                    admins = []
                    included = data.get("included", [])
                    for player in included:
                        meta = player.get("attributes", {}).get("metadata", {})
                        if meta.get("admin", False):
                            admins.append(player["attributes"].get("name", "Неизвестно"))

                    if not admins:
                        admins = ["нет админов"]

                    block = (
                        f"**{name}** (топ: {rank})\n"
                        f"Карта: {current_map} → {next_map}\n"
                        f"Онлайн: {players}/{max_players} (очередь: {queue})\n"
                        f"Админы: {', '.join(admins)}\n" + "—" * 20
                    )
                    result.append(block)
            except Exception as e:
                result.append(f"⚠️ Ошибка: {e}")

    await ctx.send("\n".join(result))

# Запуск
keep_alive()
bot.run(DISCORD_TOKEN)


