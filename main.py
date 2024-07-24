import re
import asyncio
import logging
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from flask import Flask
import threading
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your API ID and hash
api_id = 28213805
api_hash = '8f80142dfef1a696bee7f6ab4f6ece34'

# Your StringSession
string_session = os.getenv("string")
gamble = os.getenv("wet")
# Create a Telegram client using StringSession
client = TelegramClient(StringSession(string_session), api_id, api_hash)

def to_alphanumeric(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s)

@client.on(events.NewMessage(incoming=True, from_users=['@lustXcatcherrobot']))
async def handle_message(event):
    # Check if the message is from a private chat
    if isinstance(event.chat, types.Chat):
        logger.info(f"Received a message from @lustXcatcherrobot in a group chat: {event.message.text}")
        return

    logger.info(f"Received a message from @lustXcatcherrobot in a private chat: {event.message.text}")

    # Get the message with buttons
    message = event.message

    # Check if the message has inline keyboard buttons
    if hasattr(message, 'reply_markup') and hasattr(message.reply_markup, 'rows'):
        tasks = []  # List to hold tasks for clicking buttons

        # Iterate over the rows of buttons
        for row in message.reply_markup.rows:
            # Iterate over the buttons in each row
            for button in row.buttons:
                # Create a task for each button click
                tasks.append(asyncio.create_task(client(GetBotCallbackAnswerRequest(
                    peer=event.chat_id,
                    msg_id=message.id,
                    data=button.data
                ))))

        # Execute all button click tasks concurrently
        if tasks:
            await asyncio.gather(*tasks)
            logger.info("Clicked all buttons successfully.")
        else:
            logger.info("No buttons to click.")

async def send_gamble_task():
    while True:
        await client.send_message(f'@lustXcatcherrobot', '/gamble {gamble}')
        logger.info("Sent /gamble 100")
        await asyncio.sleep(12.8)

async def send_lever_message():
    while True:
        await client.send_message('@lustXcatcherrobot', '/lever 01')
        await asyncio.sleep(612)

async def send_riddle_message():
    while True:
        await client.send_message('@lustXcatcherrobot', '/riddle')
        await asyncio.sleep(8)

async def send_gyamble_task():
    while True:
        await client.send_message('@lustsupport', '/tesure')
        logger.info("Sent /gamble 100")
        await asyncio.sleep(1820)


@client.on(events.NewMessage(from_users='@lustXcatcherrobot'))
async def handle_message(event):
    message = event.message.message
    alphanumeric_message = to_alphanumeric(message)
    if 'Pleasebetatleast7ofyourbalancewhichis' in alphanumeric_message:
        balance = alphanumeric_message.replace('Pleasebetatleast7ofyourbalancewhichis', '')
        await client.send_message('@lustXcatcherrobot', f'/lever {balance}')

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

def run_flask_app():
    app.run(host='0.0.0.0', port=10000)


# Start the client
async def main():
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    await client.start()
    logger.info("Client started. Listening for messages...")
    client.loop.create_task(send_gamble_task())
    client.loop.create_task(send_lever_message())
    client.loop.create_task(send_riddle_message())
    client.loop.create_task(send_gyamble_task())
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
