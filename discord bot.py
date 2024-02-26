
from discord import Intents
import discord
import requests
import asyncio
import logging
import json

# Set up logging
# Set up logging for Twitch
twitch_logger = logging.getLogger('twitch')
twitch_logger.setLevel(logging.INFO)
twitch_handler = logging.FileHandler('twitch.log')
twitch_formatter = logging.Formatter('%(asctime)s - %(message)s')
twitch_handler.setFormatter(twitch_formatter)
twitch_logger.addHandler(twitch_handler)

# Set up logging for Discord
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.DEBUG)
discord_handler = logging.FileHandler('discord.log')
discord_formatter = logging.Formatter('%(asctime)s - %(message)s')
discord_handler.setFormatter(discord_formatter)
discord_logger.addHandler(discord_handler)
#logging.basicConfig(filename='discord.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
#twitch_log = logging.basicConfig(filename='twitch.log', level=logging.INFO, encoding='utf-8', mode='a', format='%(asctime)s - %(message)s')

# Load secrets from secrets.json file
with open('secrets.json', 'r') as f:
    secrets = json.load(f)

# Initialize variables with secrets
TWITCH_CLIENT_ID = secrets.get('TWITCH_CLIENT_ID', '')
TWITCH_USERNAME = secrets.get('TWITCH_USERNAME', '')
TWITCH_OAUTH_TOKEN = secrets.get('TWITCH_OAUTH_TOKEN', '')
TWITCH_USERNAME = secrets.get('TWITCH_USERNAME', '')
DISCORD_TOKEN = secrets.get('DISCORD_TOKEN', '')
DISCORD_CHANNEL_ID = secrets.get('DISCORD_CHANNEL_ID', '')
USER_TO_PING_ID = secrets.get('USER_TO_PING_ID', '')
ROLE_TO_PING_ID = secrets.get('ROLE_TO_PING_ID', '')

# Initialize Discord client with intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True  # You might want to enable this depending on your bot's functionality
client = discord.Client(intents=intents)
#client.run(token, log_handler=None)
# Function to check Twitch stream status
async def check_twitch_stream():
    try:
        url = f'https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}'
        headers = {'Client-ID': TWITCH_CLIENT_ID, 'Authorization': f'Bearer {TWITCH_OAUTH_TOKEN}' }
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['data']  # If user is live, it will return data, otherwise empty list
    except Exception as e:
        raise Exception(f"Error checking Twitch stream: {e}")
        twitch_logger.error(f"Error checking Twitch stream: {e}")

# Function to send notification to Discord
async def send_discord_notification(message):
    try:
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        print(channel)
        if isinstance(channel, discord.TextChannel):
            await channel.send(message)
        else:
            discord_logger.error(f"Invalid channel ID: {DISCORD_CHANNEL_ID}")
    except Exception as e:
        discord_logger.error(f"Error sending Discord notification: {e}")

# Main function to run the bot
async def main():
    try:
        await client.wait_until_ready()
        twitch_logger.info('Bot is running...')
        print('Bot is running...')
        while True:
            streams = await check_twitch_stream()
            if streams:
                # User is live
                stream_title = streams[0]['title']
                stream_url = f"https://twitch.tv/{TWITCH_USERNAME}"
                message = f"<@{USER_TO_PING_ID}> {TWITCH_USERNAME} is live! Title: {stream_title}. Watch here: {stream_url}"
                await send_discord_notification(message)
                discord_logger.info('discord: Notification sent.')
            await asyncio.sleep(60)  # Check every minute
    except Exception as e:
        error_message = f" An error occurred: {e}. <@{USER_TO_PING_ID}> <@&{ROLE_TO_PING_ID}>"
        await send_discord_notification(error_message)
        twitch_logger.error(error_message)
        raise  # Reraise the exception to exit the program

# Discord event: Bot is ready
@client.event
async def on_ready():
    discord_logger.info(f'Discord: Logged in as {client.user}')
    print(f'Logged in as {client.user}')
    await main()
    #client.lopp.create_task(main())
# Start the bot
try:
    #client.loop.create_task(main())
    asyncio.run(client.start(DISCORD_TOKEN))
except Exception as e:
    discord_logger.error(f'Discord: An error occurred: {e}')
