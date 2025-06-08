import discord
from discord.ext import commands
import aiohttp
import os

# Получаем токены из переменных окружения
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BM_TOKEN = os.getenv("BM_TOKEN_FLAGS")  # Используем токен с флагами

# BattleMetrics ID ваших серверов
SERVERS = [
    "31164311",
    "31164422",
    "31161609",
    "31162756",
]

# Настройка бота
intents = discord.Intents.default()
intents.message_content = True  # Это нужно для работы команд
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Бот запущен как {bot.user}')

@bot.command()
async def online(ctx):
    print("▶️ Команда /online вызвана")  # Для отладки
    headers = {"Authorization": f"Bearer {BM_TOKEN}"}
    server_data = []

    async with aiohttp.ClientSession() as session:
        for server_id in SERVERS:
            url = f"https://api.battlemetrics.com/servers/{server_id}?include=player"
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    server_data.append(f"Ошибка при запросе сервера {server_id}")
                    continue

                data = await response.json()
                attributes = data["data"]["attributes"]
                name = attributes["name"]
                players = attributes["players"]
                max_players = attributes["maxPlayers"]
                current_map = attributes["details"].get("map", "неизвестна")
                next_map = attributes["details"].get("nextMap", "неизвестна")
                queue = attributes["details"].get("queue", "-")
                rank = attributes.get("rank", "-")

                # Ищем админов среди включённых игроков
                admins = []
                included = data.get("included", [])
                for player in included:
                    if player.get("type") == "player":
                        name = player["attributes"]["name"]
                        is_admin = player["attributes"]["metadata"].get("admin", False)
                        if is_admin:
                            admins.append(name)

                if not admins:
                    admins = ["нет админов"]

                block = (
                    f"{name} (позиция в топе: {rank})\n"
                    f"Текущая карта: {current_map}\n"
                    f"Следующая карта: {next_map}\n"
                    f"Онлайн: {players} (очередь: {queue})\n"
                    f"Админы:\n" + "\n".join(admins) + "\n" + "—" * 16
                )
                server_data.append(block)

    result = "\n\n".join(server_data)
    await ctx.send(f"```\n{result}\n```")

bot.run(DISCORD_TOKEN)


