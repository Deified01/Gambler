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
import redis

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
r = redis.Redis(
    host='redis-18496.c285.us-west-2-2.ec2.redns.redis-cloud.com',
    port=18496,
    password='z8kTTjCIoHwxLAPDpRzycbVDB5z8eLwI'
)


@client.on(events.NewMessage(pattern='/set (\d+)([kmbt]?)'))
async def set_gamble_amount(event):
    amount_str = event.pattern_match.group(1)
    suffix = event.pattern_match.group(2)
    
    # Convert amount to integer
    if suffix == 'k':
        amount = int(amount_str) * 1000
    elif suffix == 'm':
        amount = int(amount_str) * 1000000
    elif suffix == 'b':
        amount = int(amount_str) * 1000000000
    elif suffix == 't':
        amount = int(amount_str) * 1000000000000
    else:
        amount = int(amount_str)

    # Store in Redis
    r.set('gamble_amount', amount)
    await event.respond(f"Gamble amount set to {amount}")

@client.on(events.NewMessage(pattern='/get (\d+)([kmbt]?)'))
async def get_number(event):
    amount_str = event.pattern_match.group(1)
    suffix = event.pattern_match.group(2)
    
    # Convert amount to integer
    if suffix == 'k':
        amount = int(amount_str) * 1000
    elif suffix == 'm':
        amount = int(amount_str) * 1000000
    elif suffix == 'b':
        amount = int(amount_str) * 1000000000
    elif suffix == 't':
        amount = int(amount_str) * 1000000000000
    else:
        amount = int(amount_str)

    # Delete the original message sent by the user
    await event.delete()
    
    # Respond with just the full numeric value
    await event.respond(str(amount))

@client.on(events.NewMessage(pattern=r'\.s (\d+)([kmbt]?) (h|t)'))
async def send_amount(event):
    amount_str = event.pattern_match.group(1)
    suffix = event.pattern_match.group(2)
    method = event.pattern_match.group(3)  # This will capture either 'h' or 't'

    # Convert amount to integer
    if suffix == 'k':
        amount = int(amount_str) * 1000
    elif suffix == 'm':
        amount = int(amount_str) * 1000000
    elif suffix == 'b':
        amount = int(amount_str) * 1000000000
    elif suffix == 't':
        amount = int(amount_str) * 1000000000000
    else:
        amount = int(amount_str)

    # Delete the original message sent by the user
    await event.delete()

    # Respond with the command format /sbet {amount} {method}
    response = f"/sbet {amount} {method}"
    await event.respond(response)

@client.on(events.NewMessage(pattern=r'\.p (\d+)([kmbt]?)'))
async def pay_amount(event):
    amount_str = event.pattern_match.group(1)
    suffix = event.pattern_match.group(2)

    # Convert amount to integer
    if suffix == 'k':
        amount = int(amount_str) * 1000
    elif suffix == 'm':
        amount = int(amount_str) * 1000000
    elif suffix == 'b':
        amount = int(amount_str) * 1000000000
    elif suffix == 't':
        amount = int(amount_str) * 1000000000000
    else:
        amount = int(amount_str)

    # Delete the original message sent by the user
    await event.delete()

    # Respond with the command format /pay {amount} to the user you replied to
    if event.is_reply:
        reply_to_id = event.reply_to_msg_id
        response = f"/pay {amount}"
        await client.send_message(event.chat_id, response, reply_to=reply_to_id)
    else:
        await event.respond("Please reply to a message to use the /pay command.")

@client.on(events.NewMessage(pattern=r'\.r (\d+)([kmbt]?)'))
async def rps_amount(event):
    amount_str = event.pattern_match.group(1)
    suffix = event.pattern_match.group(2)

    # Convert amount to integer
    if suffix == 'k':
        amount = int(amount_str) * 1000
    elif suffix == 'm':
        amount = int(amount_str) * 1000000
    elif suffix == 'b':
        amount = int(amount_str) * 1000000000
    elif suffix == 't':
        amount = int(amount_str) * 1000000000000
    else:
        amount = int(amount_str)

    # Delete the original message sent by the user
    await event.delete()

    # Respond with the command format /rps {amount} to the user you replied to
    if event.is_reply:
        reply_to_id = event.reply_to_msg_id
        response = f"/rps {amount}"
        await client.send_message(event.chat_id, response, reply_to=reply_to_id)
    else:
        await event.respond("Please reply to a message to use the /rps command.")

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
        # Retrieve the gamble amount from Redis, default to 10,000,000 if not set
        gamble_amount = r.get('gamble_amount')
        gamble_amount = int(gamble_amount) if gamble_amount else 10000000
        
        await client.send_message(f'@lustXcatcherrobot', f'/gamble {gamble_amount}')
        logger.info(f"Sent /gamble {gamble_amount}")
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
