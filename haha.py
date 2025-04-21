import asyncio
import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw

# --- CONFIGURATION ---
API_ID = 12345678  # Ganti dengan API_ID kamu
API_HASH = "your_api_hash_here"  # Ganti dengan API_HASH kamu
BOT_TOKEN = "your_bot_token_here"  # Ganti dengan BOT_TOKEN kamu
ADMIN_GROUP_ID = -1001234567890  # Ganti dengan ID grup admin kamu (harus negatif)

ASSETS_DIR = 'assets'
HOURGLASS_PATH = os.path.join(ASSETS_DIR, 'hourglass.gif')
MAP_FILE = 'message_map.json'
PENDING_TASKS = {}

# --- INIT RELATION MAPPING ---
if not os.path.exists(MAP_FILE):
    with open(MAP_FILE, 'w') as f:
        json.dump({}, f)

def load_mapping():
    with open(MAP_FILE, 'r') as f:
        return json.load(f)

def save_mapping(mapping):
    with open(MAP_FILE, 'w') as f:
        json.dump(mapping, f)

message_map = load_mapping()

# --- AUTO GENERATE HOURGLASS GIF ---
def make_hourglass_gif():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    if not os.path.exists(HOURGLASS_PATH):
        frames = []
        width, height = 100, 150
        sand_color = (194, 178, 128)
        glass_color = (120, 120, 120)

        for i in range(20):
            frame = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(frame)

            draw.line([(50, 0), (90, 50)], fill=glass_color, width=3)
            draw.line([(50, 0), (10, 50)], fill=glass_color, width=3)
            draw.line([(10, 50), (50, 100)], fill=glass_color, width=3)
            draw.line([(90, 50), (50, 100)], fill=glass_color, width=3)
            draw.line([(50, 100), (90, 150)], fill=glass_color, width=3)
            draw.line([(50, 100), (10, 150)], fill=glass_color, width=3)

            upper_sand_height = int(40 * (1 - i/20))
            if upper_sand_height > 0:
                draw.polygon([
                    (50, 10),
                    (50 - upper_sand_height, 50),
                    (50 + upper_sand_height, 50)
                ], fill=sand_color)

            lower_sand_height = int(40 * (i/20))
            if lower_sand_height > 0:
                draw.polygon([
                    (10, 150 - lower_sand_height),
                    (90, 150 - lower_sand_height),
                    (50, 100)
                ], fill=sand_color)

            frames.append(frame)

        frames[0].save(HOURGLASS_PATH, save_all=True, append_images=frames[1:], optimize=False, duration=100, loop=0)

make_hourglass_gif()

# --- INIT BOT ---
app = Client(
    "blakeshley_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- START COMMAND ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    chat_id = message.chat.id

    msg = await message.reply_text("ᯓ ᡣ𐭩 Please hold on, the bot is awakening from its slumber... just a moment~")
    await asyncio.sleep(2)
    await msg.delete()

    sent_animation = await message.reply_animation(HOURGLASS_PATH)
    await asyncio.sleep(5)
    await sent_animation.delete()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Format Pesanan", callback_data="format")]
    ])
    await message.reply_text(
        "Choose an option:",
        reply_markup=keyboard
    )

# --- BUTTON FORMAT ORDER ---
@app.on_callback_query(filters.regex("format"))
async def format_button(client, callback_query):
    await callback_query.answer()

    username = callback_query.from_user.username or "username"
    text = (
        f"**Copy and Paste This:**\n\n"
        f"```\n"
        f"Salutations I'm @{username}, I’d like to place an order for catalog [t.me/blakeshley] listed at Blakeshley, "
        f"Using payment method [dana, gopay, qriss, spay, ovo, bank.] "
        f"The total comes to IDR [00.000] Inrush add 5k [yay/nay]. "
        f"Kindly process this, Thanks a bunch."
        f"\n```"
    )

    await client.send_chat_action(callback_query.message.chat.id, "typing")
    await asyncio.sleep(1)

    await callback_query.message.reply_text(text, parse_mode="Markdown")

# --- HANDLE USER MESSAGE ---
@app.on_message(filters.private & filters.text)
async def forward_user_message(client, message):
    username = message.from_user.username or "NoUsername"
    text = f"Incoming message from @{username}:\n\n{message.text}"

    sent = await client.send_message(ADMIN_GROUP_ID, text)

    # Save relation
    message_map[str(sent.id)] = message.from_user.id
    save_mapping(message_map)

    # Start delay task
    task = asyncio.create_task(delay_notice(client, message.from_user.id, sent.id))
    PENDING_TASKS[str(sent.id)] = task

async def delay_notice(client, user_id, message_id):
    try:
        await asyncio.sleep(300)  # 5 minutes
        await client.send_message(
            user_id,
            "ᯓ ᡣ𐭩 the stars are still — our admin is away for a moment...\nplease wait in the calm, your message will find its way ᡣ𐭩ᡣ𐭩"
        )
    except Exception as e:
        print(f"Failed to send reminder: {e}")

# --- HANDLE ADMIN REPLY ---
@app.on_message(filters.group & filters.reply & filters.text)
async def admin_reply(client, message):
    if str(message.reply_to_message.id) in message_map:
        user_id = message_map[str(message.reply_to_message.id)]
        try:
            await client.send_message(user_id, f"Admin Reply:\n\n{message.text}")
        except Exception as e:
            print(f"Failed to send message to user: {e}")

        # Cancel pending delay
        task = PENDING_TASKS.pop(str(message.reply_to_message.id), None)
        if task:
            task.cancel()

# --- RUN BOT ---
app.run()
