import discord
from discord.ext import commands
import aiohttp
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BM_TOKEN = os.getenv("BM_TOKEN")

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
    headers = {"Authorization": f"Bearer {BM_TOKEN}"}
    server_data = []

    async with aiohttp.ClientSession() as session:
        for server_id in SERVERS:
            url = f"https://api.battlemetrics.com/servers/{server_id}"
            async with session.get(url, headers=headers) as response:
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
