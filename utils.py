import json
import os
import asyncio

DATA_DIR = 'data'
MESSAGE_MAP_FILE = os.path.join(DATA_DIR, 'message_map.json')

# Bikin folder data kalau belum ada
os.makedirs(DATA_DIR, exist_ok=True)

# --- Save relasi pesan ---
def save_message_mapping(user_id, user_message_id, group_message_id):
    try:
        if not os.path.exists(MESSAGE_MAP_FILE):
            data = {}
        else:
            with open(MESSAGE_MAP_FILE, 'r') as f:
                data = json.load(f)
        data[str(user_id)] = {
            "user_message_id": user_message_id,
            "group_message_id": group_message_id
        }
        with open(MESSAGE_MAP_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error save mapping: {e}")

# --- Load semua relasi ---
def load_message_mappings():
    if not os.path.exists(MESSAGE_MAP_FILE):
        return {}
    with open(MESSAGE_MAP_FILE, 'r') as f:
        return json.load(f)

# --- Delay notice jika admin ga bales ---
async def delay_notice(client, chat_id, original_message_id):
    try:
        await asyncio.sleep(300)  # 5 menit
        mappings = load_message_mappings()
        for user_id, message_ids in mappings.items():
            if message_ids["group_message_id"] == original_message_id:
                await client.send_message(
                    chat_id,
                    "ᯓ ᡣ𐭩 the stars are still — our admin is away for a moment...\nplease wait in the calm, your message will find its way ᡣ𐭩ᡣ𐭩"
                )
                break
    except Exception as e:
        print(f"Error delay notice: {e}")