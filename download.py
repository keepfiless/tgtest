import os
import re
import sys
import base64
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

def get_session():
    if not os.path.exists("session.dat"):
        print("❌ No session found. Run Login workflow first.")
        sys.exit(1)
    with open("session.dat", "r") as f:
        data = base64.b64decode(f.read()).decode()
    return data

async def download_file(telegram_url):
    match = re.search(r'(?:https?://)?(?:t\.me/|@)([\w\-]+)/(\d+)', telegram_url)
    if not match:
        print("Invalid URL format")
        return None

    channel, msg_id = match.group(1), int(match.group(2))
    session = get_session()
    client = TelegramClient(StringSession(session), API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        print("❌ Session expired. Run Login workflow again.")
        sys.exit(1)

    try:
        message = await client.get_messages(channel, ids=msg_id)
        if not message or not message.media:
            print("No media found")
            return None

        fname = f"file_{msg_id}"
        if isinstance(message.media, MessageMediaDocument):
            doc = message.media.document
            for attr in doc.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    fname = attr.file_name
                    break
            if fname == f"file_{msg_id}":
                mime = doc.mime_type or ""
                ext = mime.split('/')[-1] if '/' in mime else 'bin'
                fname = f"file_{msg_id}.{ext}"
        elif isinstance(message.media, MessageMediaPhoto):
            fname = f"photo_{msg_id}.jpg"

        os.makedirs("downloads", exist_ok=True)
        path = f"downloads/{fname}"

        print(f"Downloading: {fname}")
        await client.download_media(message, path)
        print(f"✅ Downloaded: {path}")
        return path
    finally:
        await client.disconnect()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if not url:
        print("Usage: python download.py <telegram_url>")
        sys.exit(1)
    asyncio.run(download_file(url))
