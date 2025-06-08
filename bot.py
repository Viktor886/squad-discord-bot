import os
import discord
import aiohttp
from discord.ext import tasks
from keep_alive import keep_alive

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BM_TOKEN = os.getenv("BM_TOKEN_FLAGS") or os.getenv("BM_TOKEN")

SERVERS = [
    "31164311",
    "31164422",
    "31161609",
    "31162756",
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Бот запущен как {client.user}")

@tree.command(name="online", description="Показать информацию о серверах")
async def online_command(interaction: discord.Interaction):
    headers = {"Authorization": f"Bearer {BM_TOKEN}"}
    server_data = []

    async with aiohttp.ClientSession() as session:
        for server_id in SERVERS:
            url = f"https://api.battlemetrics.com/servers/{server_id}"
            try:
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
                    rank = attributes["rank"]

                    admins = ["нет админов"]  # Здесь можно улучшить, если знаем как искать админов

                    block = (
                        f"{name} (топ: {rank})\n"
                        f"Карта: {current_map} → {next_map}\n"
                        f"Онлайн: {players}/{max_players} (очередь: {queue})\n"
                        f"Админы:\n" + "\n".join(admins) + "\n" + "—" * 16
                    )
                    server_data.append(block)

            except Exception as e:
                server_data.append(f"Ошибка при запросе сервера {server_id}: {str(e)}")

    result = "\n\n".join(server_data)
    await interaction.response.send_message(f"```\n{result}\n```")

keep_alive()
client.run(DISCORD_TOKEN)
