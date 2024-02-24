const Discord = require('discord.js');
const fetch = require('node-fetch');
const { setInterval } = require('timers');

// Set up logging
const fs = require('fs');
const logStream = fs.createWriteStream('bot.log', { flags: 'a' });

const logger = (message) => {
  const timestamp = new Date().toISOString();
  console.log(`${timestamp} - ${message}`);
  logStream.write(`${timestamp} - ${message}\n`);
};

// Set up your Twitch credentials
const TWITCH_CLIENT_ID = 'YOUR_TWITCH_CLIENT_ID';
const TWITCH_USERNAME = 'YOUR_TWITCH_USERNAME';

// Set up your Discord bot token, the user ID to ping, and the role ID to ping
const DISCORD_TOKEN = 'YOUR_DISCORD_BOT_TOKEN';
const DISCORD_CHANNEL_ID = 'YOUR_DISCORD_CHANNEL_ID';  // The channel where you want to send notifications
const USER_TO_PING_ID = 'USER_ID_TO_PING';
const ROLE_TO_PING_ID = 'ROLE_ID_TO_PING';

// Initialize Discord client
const client = new Discord.Client();

// Function to check Twitch stream status
const checkTwitchStream = async () => {
  try {
    const url = `https://api.twitch.tv/helix/streams?user_login=${TWITCH_USERNAME}`;
    const headers = { 'Client-ID': TWITCH_CLIENT_ID };
    const response = await fetch(url, { headers });
    const data = await response.json();
    return data.data; // If user is live, it will return data, otherwise empty array
  } catch (error) {
    throw new Error(`Error checking Twitch stream: ${error}`);
  }
};

// Function to send notification to Discord
const sendDiscordNotification = async (message) => {
  try {
    const channel = await client.channels.fetch(DISCORD_CHANNEL_ID);
    await channel.send(message);
  } catch (error) {
    throw new Error(`Error sending Discord notification: ${error}`);
  }
};

// Main function to run the bot
const main = async () => {
  try {
    await client.login(DISCORD_TOKEN);
    logger('Bot is running...');
    setInterval(async () => {
      const streams = await checkTwitchStream();
      if (streams && streams.length > 0) {
        // User is live
        const streamTitle = streams[0].title;
        const streamUrl = `https://twitch.tv/${TWITCH_USERNAME}`;
        const message = `<@${USER_TO_PING_ID}> ${TWITCH_USERNAME} is live! Title: ${streamTitle}. Watch here: ${streamUrl}`;
        await sendDiscordNotification(message);
        logger('Notification sent.');
      }
    }, 60000); // Check every minute
  } catch (error) {
    const errorMessage = `An error occurred: ${error}. <@${USER_TO_PING_ID}> <@&${ROLE_TO_PING_ID}>`;
    await sendDiscordNotification(errorMessage);
    logger(errorMessage);
    throw error;
  }
};

// Discord event: Bot is ready
client.once('ready', () => {
  logger(`Logged in as ${client.user.tag}`);
});

// Start the bot
main().catch((error) => {
  logger(`An error occurred: ${error}`);
  process.exit(1); // Exit with error code
});
