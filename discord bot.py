import discord
import requests
import asyncio
import logging
import json

# Set up logging
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Load secrets from secrets.json file
with open('secrets.json', 'r') as f:
    secrets = json.load(f)

# Initialize variables with secrets
TWITCH_CLIENT_ID = secrets.get('TWITCH_CLIENT_ID', '')
TWITCH_USERNAME = secrets.get('TWITCH_USERNAME', '')
DISCORD_TOKEN = secrets.get('DISCORD_TOKEN', '')
DISCORD_CHANNEL_ID = secrets.get('DISCORD_CHANNEL_ID', '')
USER_TO_PING_ID = secrets.get('USER_TO_PING_ID', '')
ROLE_TO_PING_ID = secrets.get('ROLE_TO_PING_ID', '')

# Initialize Discord client
client = discord.Client()

# Function to check Twitch stream status
async def check_twitch_stream():
    try:
        url = f'https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}'
        headers = {'Client-ID': TWITCH_CLIENT_ID}
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['data']  # If user is live, it will return data, otherwise empty list
    except Exception as e:
        raise Exception(f"Error checking Twitch stream: {e}")

# Function to send notification to Discord
async def send_discord_notification(message):
    try:
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        if isinstance(channel, discord.TextChannel):
            await channel.send(message)
        else:
            logging.error(f"Invalid channel ID: {DISCORD_CHANNEL_ID}")
    except Exception as e:
        raise Exception(f"Error sending Discord notification: {e}")

# Main function to run the bot
async def main():
    try:
        await client.wait_until_ready()
        logging.info('Bot is running...')
        print('Bot is running...')
        while True:
            streams = await check_twitch_stream()
            if streams:
                # User is live
                stream_title = streams[0]['title']
                stream_url = f"https://twitch.tv/{TWITCH_USERNAME}"
                message = f"<@{USER_TO_PING_ID}> {TWITCH_USERNAME} is live! Title: {stream_title}. Watch here: {stream_url}"
                await send_discord_notification(message)
                logging.info('Notification sent.')
            await asyncio.sleep(60)  # Check every minute
    except Exception as e:
        error_message = f"An error occurred: {e}. <@{USER_TO_PING_ID}> <@&{ROLE_TO_PING_ID}>"
        await send_discord_notification(error_message)
        logging.error(error_message)
        raise  # Reraise the exception to exit the program

# Discord event: Bot is ready
@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')
    print(f'Logged in as {client.user}')

# Start the bot
try:
    client.loop.create_task(main())
    client.run(DISCORD_TOKEN)
except Exception as e:
    logging.error(f'An error occurred: {e}')
