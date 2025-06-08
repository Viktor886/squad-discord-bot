import discord
from discord.ext import commands
import aiohttp
import os
from keep_alive import keep_alive

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
    result = ""

    async with aiohttp.ClientSession() as session:
        for server_id in SERVERS:
            url = f"https://api.battlemetrics.com/servers/{server_id}"
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        result += f"Ошибка при запросе сервера {server_id}\n"
                        continue

                    data = await response.json()
                    attr = data["data"]["attributes"]
                    name = attr["name"]
                    players = attr["players"]
                    max_players = attr["maxPlayers"]
                    current_map = attr["details"].get("map", "неизвестна")
                    next_map = attr["details"].get("nextMap", "неизвестна")
                    queue = attr["details"].get("queue", "0")
                    rank = attr["rank"]

                    result += (
                        f"{name} (Рейтинг: {rank})\n"
                        f"Карта: {current_map} → {next_map}\n"
                        f"Онлайн: {players}/{max_players} (Очередь: {queue})\n"
                        f"Админы: (проверка отключена)\n"
                        f"{'-'*20}\n"
                    )
            except Exception as e:
                result += f"❌ Ошибка при запросе: {e}\n"

    await ctx.send(f"```\n{result}\n```")

keep_alive()
bot.run(DISCORD_TOKEN)
