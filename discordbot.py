#from discord import Intents
import discord
import requests
import asyncio
import logging
import json
import signal
import sys

# Set up logging
# Set up logging for Twitch
twitch_logger = logging.getLogger('twitch')
twitch_logger.setLevel(logging.INFO)
twitch_encoding = 'utf-8'
twitch_handler = logging.FileHandler('twitch.log', encoding=twitch_encoding)
twitch_formatter = logging.Formatter('%(asctime)s - %(message)s')
twitch_handler.setFormatter(twitch_formatter)
twitch_logger.addHandler(twitch_handler)

# Set up logging for Discord
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
discord_encoding = 'utf-8'
discord_handler = logging.FileHandler('discord.log', encoding=discord_encoding)
discord_formatter = logging.Formatter('%(asctime)s - %(message)s')
discord_handler.setFormatter(discord_formatter)
discord_logger.addHandler(discord_handler)
#logging.basicConfig(filename='discord.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
#twitch_log = logging.basicConfig(filename='twitch.log', level=logging.INFO, encoding='utf-8', mode='a', format='%(asctime)s - %(message)s')

# Load secrets from secrets.json filelpipenpip
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

# Set initial stream state to offline
stream_online = False


# Function to check Twitch stream status
async def check_twitch_stream():
    global stream_online
    try:
        url = f'https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}'
        headers = {'Client-ID': TWITCH_CLIENT_ID, 'Authorization': f'Bearer {TWITCH_OAUTH_TOKEN}' }
        response = requests.get(url, headers=headers)
        data = response.json()
        print(f"Checking for streamer: {TWITCH_USERNAME}")
        twitch_logger.info(f"Checking for streamer: {TWITCH_USERNAME}")
        twitch_logger.info(data)
        if data['data']:
            stream_online=True
        else: 
            stream_online=False
        return data['data']  # If user is live, it will return data, otherwise empty list
    except Exception as e:
        raise Exception(f"Error checking Twitch stream: {e}")
        twitch_logger.error(f"Error checking Twitch stream: {e}")

# Function to send notification to Discord
async def send_discord_notification(message):
    global stream_online
    try:
        channel = client.get_channel(int(DISCORD_CHANNEL_ID))
        discord_logger.info(channel)
        discord_logger.info(int(DISCORD_CHANNEL_ID))
        if isinstance(channel, discord.TextChannel):
            await channel.send(str(message))
            discord_logger.info(str(message))
            stream_online = False
        else:
            discord_logger.error(f"Invalid channel ID: {DISCORD_CHANNEL_ID}")
    except Exception as e:
        discord_logger.error(f"Error sending Discord notification: {e}")

# Main function to run the bot
async def main():
    global stream_online
    try:
        await client.wait_until_ready()
        twitch_logger.info('Bot is running...')
        print('Bot is running...')
        while True:
            streams = await check_twitch_stream()
            if streams and stream_online:
                # User is live
                stream_title = streams[0]['title']
                stream_url = f"https://twitch.tv/{TWITCH_USERNAME}"
                message = f"<@{USER_TO_PING_ID}> {TWITCH_USERNAME} is live! Title: {stream_title}. Watch here: {stream_url}"
                await send_discord_notification(str(message))
                discord_logger.info(f"Notification sent.{message}")
                print(f"Notification Sent:{message}.{message}")
            elif not streams and stream_online:
                stream_online = False
            await asyncio.sleep(60)  # Check every minute
    except Exception as e:
        stream_online = False
        error_message = f" An error occurred: {e}. <@{USER_TO_PING_ID}> <@&{ROLE_TO_PING_ID}>"
        await send_discord_notification(error_message)
        twitch_logger.error(error_message)
        raise  # Reraise the exception to exit the program

# Discord event: Bot is ready
@client.event
async def on_ready():
    discord_logger.info(f'Logged in as {client.user}')
    print(f'Logged in as {client.user}')
    await main()
    #client.lopp.create_task(main())
# Start the bot
try:
    #client.loop.create_task(main())
    asyncio.run(client.start(DISCORD_TOKEN))
except Exception as e:
    discord_logger.error(f'An error occurred: {e}')

# Discord event: Reconnect attempt
@client.event
async def on_connect():
    logging.info('Attempting to reconnect to Discord...')

# Discord event: Reconnection failedw
@client.event
async def on_disconnect():
    logging.error('Disconnected from Discord. Reconnection attempt failed.')

# Define signal handler for graceful termination
def signal_handler(sig, frame):
    print("Received termination signal. Gracefully terminating...")
    client.loop.create_task(client.close())

# Register signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Register signal handler for SIGTERM (terminate signal)
signal.signal(signal.SIGTERM, signal_handler)

# Start the bot
try:
    asyncio.run(client.start(DISCORD_TOKEN))
except Exception as e:
    logging.error(f'An error occurred: {e}')
finally:
    logging.info('Bot is shutting down...')
    print('Bot is shutting down...')
    logging.shutdown()
    sys.exit(0)