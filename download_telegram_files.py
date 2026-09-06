import os
import asyncio
import json
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from dotenv import load_dotenv

load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'data', 'telegram_dump')
MANIFEST_FILE = os.path.join(os.path.dirname(__file__), 'telegram_files_manifest.json')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def main():
    if not os.path.exists(MANIFEST_FILE):
        print("Manifest not found. Run scrape_metadata.py first.")
        return
        
    with open(MANIFEST_FILE, 'r') as f:
        manifest = json.load(f)

    client = TelegramClient('astrology_session', int(api_id), api_hash)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Session not authorized.")
        return

    # Group the manifest by channel so we only get_entity once
    from collections import defaultdict
    groups = defaultdict(list)
    for entry in manifest:
        groups[entry['group']].append(entry)

    total_downloaded = 0
    total_skipped = 0

    for group, entries in groups.items():
        print(f"\n--- Processing group: {group} ---")
        try:
            entity = await client.get_entity(group)
        except Exception as e:
            print(f"Error fetching group {group}: {e}")
            continue

        for i, entry in enumerate(entries):
            if entry.get("downloaded", False):
                total_skipped += 1
                continue
                
            file_path = os.path.join(DOWNLOAD_DIR, entry['file_name'])
            
            # Check if file already exists on disk
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"[{i}/{len(entries)}] Already exists: {entry['file_name']}")
                entry['downloaded'] = True
                total_skipped += 1
                # Save progress occasionally
                if i % 50 == 0:
                    with open(MANIFEST_FILE, 'w') as f:
                        json.dump(manifest, f, indent=4)
                continue
                
            # Need to download
            msg_id = entry['message_id']
            print(f"[{i}/{len(entries)}] Safe Downloading {entry['file_name']} (ID: {msg_id}) from {group}...")
            
            success = False
            while not success:
                try:
                    # Get the message object
                    message = await client.get_messages(entity, ids=msg_id)
                    if message and message.document:
                        await asyncio.wait_for(
                            client.download_media(message, file_path),
                            timeout=600 # 10 mins
                        )
                        print(f"Successfully downloaded {entry['file_name']}.")
                        entry['downloaded'] = True
                        total_downloaded += 1
                        success = True
                    else:
                        print(f"Message {msg_id} not found or no document.")
                        entry['downloaded'] = True # Mark as done so we don't keep trying
                        success = True
                        
                except asyncio.TimeoutError:
                    print(f"[!] Timeout downloading {entry['file_name']}. Retrying...")
                    # Usually means connection dropped. Let the while loop try again.
                    await asyncio.sleep(10)
                except FloodWaitError as e:
                    print(f"\n[!] Rate Limit! Sleeping for {e.seconds} seconds...")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    print(f"\n[!] Network or other error: {e}. Reconnecting in 30s...")
                    await asyncio.sleep(30)
                    try:
                        await client.connect()
                    except:
                        pass
            
            # Save progress after every successful download
            with open(MANIFEST_FILE, 'w') as f:
                json.dump(manifest, f, indent=4)
                
    print(f"\n--- DOWNLOAD RUN SUMMARY ---")
    print(f"Total Downloaded this run: {total_downloaded}")
    print(f"Total Skipped: {total_skipped}")

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
