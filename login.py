import sys
import os
import json
import base64
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
HASH_FILE = "phone_hash.json"

async def send_code(phone):
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()

    result = await client.send_code_request(phone, force_sms=True)

    with open(HASH_FILE, "w") as f:
        json.dump({"phone": phone, "hash": result.phone_code_hash}, f)

    print(f"✅ SMS sent to {phone}")
    print("Run workflow again with the code you received")

    await client.disconnect()

async def verify_code(phone, code):
    if not os.path.exists(HASH_FILE):
        print("❌ Run workflow without code first to receive SMS")
        sys.exit(1)

    with open(HASH_FILE, "r") as f:
        data = json.load(f)

    if data["phone"] != phone:
        print("❌ Phone number mismatch")
        sys.exit(1)

    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()

    try:
        await client.sign_in(phone, code, phone_code_hash=data["hash"])

        session_string = client.session.save()
        session_bytes = session_string.encode()

        with open("session.dat", "w") as f:
            f.write(base64.b64encode(session_bytes).decode())

        print("✅ Login successful! Session saved.")
        os.remove(HASH_FILE)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    phone = sys.argv[1] if len(sys.argv) > 1 else ""
    code = sys.argv[2] if len(sys.argv) > 2 else ""

    if not phone:
        print("Usage: python login.py <phone> [code]")
        sys.exit(1)

    if code:
        asyncio.run(verify_code(phone, code))
    else:
        asyncio.run(send_code(phone))
