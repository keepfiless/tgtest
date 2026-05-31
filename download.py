import os
import re
import sys
import base64
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

def get_session():
    if not os.path.exists("session.dat"):
        print("❌ سشن یافت نشد. ابتدا ورکفلو Login را اجرا کنید.")
        sys.exit(1)
    with open("session.dat", "r") as f:
        data = base64.b64decode(f.read()).decode()
    return data

def update_readme(folder_name, persian_title, telegram_url):
    readme_path = "downloads/README.md"
    date_str = datetime.now().strftime("%Y/%m/%d - %H:%M")

    new_entry = f"| [{persian_title}](./{folder_name}) | [لینک تلگرام]({telegram_url}) | {date_str} |\n"

    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        with open(readme_path, "a", encoding="utf-8") as f:
            f.write(new_entry)
    else:
        header = """# 📥 دانلودها

| 📁 پوشه | 🔗 لینک | 📅 تاریخ |
|--------|--------|---------|
"""
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(header + new_entry)

    print(f"📝 README.md بروزرسانی شد")

async def download_file(telegram_url, persian_title=None):
    match = re.search(r'(?:https?://)?(?:t\.me/|@)([\w\-]+)/(\d+)', telegram_url)
    if not match:
        print("❌ فرمت لینک نامعتبر است")
        return None

    channel, msg_id = match.group(1), int(match.group(2))
    session = get_session()
    client = TelegramClient(StringSession(session), API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        print("❌ سشن منقضی شده. ورکفلو Login را دوباره اجرا کنید.")
        sys.exit(1)

    try:
        message = await client.get_messages(channel, ids=msg_id)
        if not message or not message.media:
            print("❌ مدیایی یافت نشد")
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

        # Create folder for this download
        folder_name = persian_title if persian_title else f"{channel}_{msg_id}"
        folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)  # sanitize
        folder_path = f"downloads/{folder_name}"
        os.makedirs(folder_path, exist_ok=True)

        path = f"{folder_path}/{fname}"

        print(f"📥 در حال دانلود: {fname}")
        await client.download_media(message, path)
        print(f"✅ دانلود شد: {path}")

        # Update README
        update_readme(folder_name, persian_title or folder_name, telegram_url)

        return path
    finally:
        await client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ استفاده: python download.py <telegram_url> [عنوان_فارسی]")
        sys.exit(1)

    url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(download_file(url, title))
