import os
import asyncio
import json
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeFilename
from dotenv import load_dotenv

load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
group_name = os.getenv('TELEGRAM_GROUP_NAME')

async def main():
    client = TelegramClient('astrology_session_copy', int(api_id), api_hash)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Session not authorized.")
        return

    groups = [g.strip() for g in group_name.split(',')]
    manifest = []

    print("Starting metadata scrape...")
    for group in groups:
        print(f"Scanning group: {group}...")
        try:
            entity = await client.get_entity(group)
            
            async for message in client.iter_messages(entity, filter=None):
                if message.document:
                    file_name = None
                    for attr in message.document.attributes:
                        if isinstance(attr, DocumentAttributeFilename):
                            file_name = attr.file_name
                            
                    if not file_name:
                        file_name = f"{group}_document_{message.id}.pdf"
                        
                    safe_file_name = file_name.encode('ascii', 'ignore').decode('ascii')
                    
                    manifest.append({
                        "group": group,
                        "message_id": message.id,
                        "file_name": safe_file_name,
                        "size_bytes": message.document.size,
                        "downloaded": False
                    })
        except Exception as e:
            print(f"Error scanning {group}: {e}")

    with open("telegram_files_manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"Successfully saved {len(manifest)} files to telegram_files_manifest.json")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
