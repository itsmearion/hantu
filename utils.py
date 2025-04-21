import json
import os
import asyncio
import logging

DATA_DIR = 'data'
MAPPINGS_FILE = os.path.join(DATA_DIR, 'mappings.json')

# Pastikan folder data ada
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def save_message_mapping(user_id, user_message_id, group_message_id):
    mappings = load_message_mappings()
    mappings[str(user_id)] = {
        "user_message_id": user_message_id,
        "group_message_id": group_message_id
    }
    with open(MAPPINGS_FILE, "w") as f:
        json.dump(mappings, f, indent=4)

def load_message_mappings():
    if not os.path.exists(MAPPINGS_FILE):
        return {}
    with open(MAPPINGS_FILE, "r") as f:
        return json.load(f)

async def delay_notice(client, group_id, group_message_id):
    await asyncio.sleep(300)  # 5 menit
    try:
        await client.send_message(
            group_id,
            f"ᯓ 𖤓 the stars hold their breath ~ admin is adrift beyond dreams ~ please wait kindly ᯓ",
            reply_to_message_id=group_message_id
        )
    except Exception as e:
        logging.error(f"Delay notice error: {e}")

async def check_sticker(client, sticker_id):
    try:
        test = await client.send_sticker("me", sticker_id)
        await asyncio.sleep(1)
        await test.delete()
        return True
    except Exception:
        return False