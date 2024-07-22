import asyncio
import logging
import threading
from flask import Flask
from telethon import events, TelegramClient, types
from telethon.sessions import StringSession
import os
import uvloop

# Set the event loop policy to uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Flask application setup
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

def run_flask_app():
    app.run(host='0.0.0.0', port=10000)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Your API ID and hash
api_id = 28213805
api_hash = '8f80142dfef1a696bee7f6ab4f6ece34'

# Your StringSession
smtring_session = '1B9vLpwF6shu127rXyk2uRgpbRKEwHoIqLln3_khBr1reFGrXYj_dtr8c8NDRXw3RYnze5kcMIA0mxjNtbAnTxJ8rmTQmeG-qWuYo2JX6lp1VkfuxI64a1Jq_pKM62JVmyKn_E1hBRJg5KPs9-z-SmGTKsifibR9vBkc_21_URBGV8ajMuHgPdP8swhxhxIVhTMlrppwiy7ywMvMZ0w1OT9o6A9GtJHwP7IlP6vdCMAy6HOqQbXMW8RaK44tOTpF9OQd1hAUD8mUYbQsxSZq1udvWJrWN5hQMQeFFN-xRQNmyQN5cojhb1IZooItJwUZOjS6HYyWKktDHyuA='
string_session = os.getenv("string")
# Create a Telegram client using StringSession
client = TelegramClient(StringSession(string_session), api_id, api_hash)

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
                # Use button.click() to click the button
                tasks.append(asyncio.create_task(button.click(client)))
        
        # Execute all button click tasks concurrently
        if tasks:
            await asyncio.gather(*tasks)
            logger.info("Clicked all buttons successfully.")
        else:
            logger.info("No buttons to click.")

async def gamble_every_12_seconds():
    while True:
        logger.info("Gambling 100000000000...")
        await client.send_message('@lustXcatcherrobot', '/gamble 100000000000')
        await asyncio.sleep(11)

# Start the client and Flask app
async def main():
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True  # Daemonize thread
    flask_thread.start()

    await client.start()
    logger.info("Client started. Listening for messages...")
    
    # Run the gambling coroutine concurrently
    asyncio.create_task(gamble_every_12_seconds())
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
