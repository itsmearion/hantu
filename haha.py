import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import save_message_mapping, load_message_mappings, delay_notice, check_sticker
import logging

# Konfigurasi Bot
API_ID = int("23710720")
API_HASH = "6dee0b9148b607f8a9868dc180d219cc"
BOT_TOKEN = "7955360080:AAGjqYkBIshyrTYd1xWHIFgeqsIncnO6r3s"
TARGET_GROUP_ID = -1002311076740  # ID grup tujuan
STICKER_ID = "CAACAgIAAxkBAAE0Ak5oBoV9UOnECM09QrJsJZzlnau_9wAC0wADlp-MDhtJv7qBP3auNgQ"  # ID Sticker aesthetic

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Inisialisasi Client
app = Client(
    "blakeshley_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- Start Command ---
@app.on_message(filters.command("start"))
async def start(client, message):
    chat_id = message.chat.id
    awakening = await message.reply_text("ᯓ ᡣ𐭩 shhh... the winds are whispering ~ please wait, little soul...")
    await asyncio.sleep(2)
    await awakening.delete()

    # --- Kirim Sticker dan efek bunga, feather
    if await check_sticker(client, STICKER_ID):
        await client.send_sticker(chat_id, STICKER_ID)
    else:
        await message.reply_text("⚠️ the magic faltered... sticker could not be sent ~")

    await asyncio.sleep(1)
    await message.reply_text("༄❀ delicate petals drift around you... ᯓ༄")

    await asyncio.sleep(1)
    await message.reply_text("༄ feathers of dreams flutter in the twilight ~ ❀༄")

    # --- Inline Button Format
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᯓ ✎ format your wishes ✎", callback_data="format")]
    ])
    await message.reply_text(
        "𖤓 pick your charm, dear traveller ~",
        reply_markup=keyboard
    )

# --- Callback Button Format ---
@app.on_callback_query(filters.regex("format"))
async def format_button(client, callback_query):
    try:
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
        await callback_query.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error sending format: {e}")

# --- Handle Kirim Order dari User ---
@app.on_message(filters.private & filters.text)
async def handle_user_message(client, message):
    try:
        if "Salutations I'm @" in message.text:
            sent = await client.send_message(
                TARGET_GROUP_ID,
                f"ᯓ 𖤓 a new wish has flown into the skies ~\n\n{message.text}"
            )
            save_message_mapping(message.from_user.id, message.id, sent.id)
            await message.reply_text("༄ your wish has been carried away into the starlit winds ~ ༄")

            asyncio.create_task(delay_notice(client, TARGET_GROUP_ID, sent.id))
    except Exception as e:
        logging.error(f"Error handling user message: {e}")

# --- Handle Balasan Admin ---
@app.on_message(filters.group & filters.reply)
async def handle_admin_reply(client, message):
    try:
        mappings = load_message_mappings()
        for user_id, ids in mappings.items():
            if ids["group_message_id"] == message.reply_to_message.id:
                await client.send_message(
                    user_id,
                    f"༄ a reply floats toward you on soft moonlight ~ ༄\n\n{message.text}"
                )
                break
    except Exception as e:
        logging.error(f"Error handling admin reply: {e}")

# --- Run Bot ---
app.run()