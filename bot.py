import discord
from discord.ext import commands
import aiohttp
import os

# Получаем токены из переменных окружения
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BM_TOKEN_FLAGS = os.getenv("BM_TOKEN_FLAGS")  # Используем токен, который показывает админов

# BattleMetrics ID ваших серверов (замени на свои)
SERVERS = [
    "31164311",
    "31164422",
    "31161609",
    "31162756",
]

# Настройка бота
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Бот запущен как {bot.user}')

@bot.command()
async def online(ctx):
    print("▶️ Команда /online вызвана")
    headers = {"Authorization": f"Bearer {BM_TOKEN_FLAGS}"}
    server_data = []

    async with aiohttp.ClientSession() as session:
        for server_id in SERVERS:
            url = f"https://api.battlemetrics.com/servers/{server_id}?include=player"
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        server_data.append(f"Ошибка при запросе сервера {server_id} (код {response.status})")
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

                    # Получаем список админов
                    admins = []
                    included_players = data.get("included", [])
                    for player in included_players:
                        if player.get("type") == "player":
                            metadata = player.get("attributes", {}).get("metadata", {})
                            if metadata.get("admin", False):
                                admins.append(player.get("attributes", {}).get("name", "Неизвестный"))

                    if not admins:
                        admins = ["нет админов"]

                    block = (
                        f"{name} (позиция в топе: {rank})\n"
                        f"Текущая карта: {current_map}\n"
                        f"Следующая карта: {next_map}\n"
                        f"Онлайн: {players}/{max_players} (очередь: {queue})\n"
                        f"Админы:\n" + "\n".join(admins) + "\n" + "—" * 16
                    )
                    server_data.append(block)

            except Exception as e:
                server_data.append(f"Ошибка при запросе сервера {server_id}:\n{str(e)}")

    result = "\n\n".join(server_data)
    await ctx.send(f"```\n{result}\n```")

bot.run(DISCORD_TOKEN)


