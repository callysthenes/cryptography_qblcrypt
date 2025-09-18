import asyncio
import logging
import os
import json
import sys
from nio import AsyncClient, MatrixRoom, RoomMessageText, LoginResponse, JoinResponse, RoomCreateResponse
from nio.exceptions import OlmUnverifiedDeviceError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
client = None
config_file = "matrix_config.json"
user_keys = {}
current_room_id = None

# Vigenère Cipher functions
def vigenere_encrypt(plaintext, key):
    """Encrypt plaintext using Vigenère cipher"""
    encrypted_text = []
    key = key.upper()
    key_length = len(key)
    
    for i, char in enumerate(plaintext):
        if char.isalpha():
            # Determine the shift based on the key character
            key_char = key[i % key_length]
            shift = ord(key_char) - ord('A')
            
            if char.isupper():
                base = ord('A')
            else:
                base = ord('a')
                
            # Apply the shift
            encrypted_char = chr((ord(char) - base + shift) % 26 + base)
            encrypted_text.append(encrypted_char)
        else:
            encrypted_text.append(char)
    
    return ''.join(encrypted_text)

def vigenere_decrypt(ciphertext, key):
    """Decrypt ciphertext using Vigenère cipher"""
    decrypted_text = []
    key = key.upper()
    key_length = len(key)
    
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            # Determine the shift based on the key character
            key_char = key[i % key_length]
            shift = ord(key_char) - ord('A')
            
            if char.isupper():
                base = ord('A')
            else:
                base = ord('a')
                
            # Apply the inverse shift
            decrypted_char = chr((ord(char) - base - shift) % 26 + base)
            decrypted_text.append(decrypted_char)
        else:
            decrypted_text.append(char)
    
    return ''.join(decrypted_text)

# Configuration management
def load_config():
    """Load Matrix client configuration"""
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {
        "homeserver": "https://matrix.org",
        "user_id": "@atlantic_pacific:matrix.org",
        "device_id": "",
        "access_token": "",
        "room_id": ""
    }

def save_config(config):
    """Save Matrix client configuration"""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

# Matrix setup functions
async def setup_client():
    """Set up the Matrix client with user-provided details"""
    global client, current_room_id
    
    config = load_config()
    
    print("Matrix Client Setup")
    print("===================")
    
    # Get homeserver
    homeserver = input(f"Enter Matrix homeserver URL [{config['homeserver']}]: ").strip()
    if not homeserver:
        homeserver = config['homeserver']
    
    # Check if we have existing credentials
    if config.get('user_id') and config.get('access_token'):
        use_existing = input("Found existing credentials. Use them? (y/n): ").strip().lower()
        if use_existing == 'y':
            user_id = config['user_id']
            # Create client with user_id
            client = AsyncClient(homeserver, user_id)
            client.device_id = config['device_id']
            client.access_token = config['access_token']
            
            if config.get('room_id'):
                current_room_id = config['room_id']
                print(f"Using existing room: {current_room_id}")
                return True
            else:
                print("No room configured. You'll need to join or create one.")
                return True  # Still return True, as login is done via token
    
    # Get user_id for new login
    user_id = input("Matrix User ID (e.g., @username:matrix.org): ").strip()
    if not user_id:
        user_id = config.get('user_id', "@atlantic_pacific:matrix.org")
    
    # Create client with user_id
    client = AsyncClient(homeserver, user_id)
    
    password = input("Password: ").strip()
    
    # Try to login
    try:
        device_name = "VigenereDemoDevice"
        resp = await client.login(password=password, device_name=device_name)
        
        if isinstance(resp, LoginResponse):
            print("Login successful!")
            
            # Save credentials
            config['homeserver'] = homeserver
            config['user_id'] = resp.user_id or user_id
            config['device_id'] = resp.device_id
            config['access_token'] = resp.access_token
            save_config(config)
            
            # Set up room
            await setup_room(config)
            return True
        else:
            print(f"Login failed: {resp}")
            print(f"Error message: {getattr(resp, 'message', 'No error message')}")
            return False
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def setup_room(config):
    """Set up the Matrix room"""
    global current_room_id
    
    print("\nRoom Setup")
    print("==========")
    
    room_option = input("Join existing room (j) or create new room (c)? [j/c]: ").strip().lower()
    
    if room_option == 'c':
        # Create a new room
        room_name = input("Room name: ").strip()
        try:
            resp = await client.room_create(name=room_name)
            if isinstance(resp, RoomCreateResponse):
                current_room_id = resp.room_id
                config['room_id'] = current_room_id
                save_config(config)
                print(f"Created room: {current_room_id}")
            else:
                print(f"Failed to create room: {resp}")
        except Exception as e:
            print(f"Error creating room: {e}")
    else:
        # Join an existing room
        room_id_or_alias = input("Room ID or alias (e.g., #room:matrix.org): ").strip()
        try:
            resp = await client.join(room_id_or_alias)
            if isinstance(resp, JoinResponse):
                current_room_id = resp.room_id
                config['room_id'] = current_room_id
                save_config(config)
                print(f"Joined room: {current_room_id}")
            else:
                print(f"Failed to join room: {resp}")
        except Exception as e:
            print(f"Error joining room: {e}")

async def view_room_messages():
    """View recent messages in the current room, decrypting encrypted ones if possible"""
    global current_room_id
    
    if not current_room_id:
        print("No room configured. Please set up a room first.")
        return
    
    try:
        # Get room state to check if it's encrypted
        room_state = await client.room_get_state(current_room_id)
        
        # Check if room is encrypted
        is_encrypted = False
        for event in room_state.events:
            if (event.get('type') == 'm.room.encryption' and 
                event.get('content', {}).get('algorithm')):
                is_encrypted = True
                break
        
        # We remove the refusal for encrypted rooms to allow viewing if the client can decrypt
        
        # Get recent messages
        messages_response = await client.room_messages(
            current_room_id, 
            limit=20  # Get last 20 messages
        )
        
        if hasattr(messages_response, 'chunk'):
            print(f"\nRecent messages in room {current_room_id}:")
            print("=" * 60)
            
            for event in reversed(messages_response.chunk):  # Reverse to show oldest to newest
                if (hasattr(event, 'content') and 
                    hasattr(event.content, 'body') and 
                    hasattr(event, 'sender')):
                    
                    # Format the message based on type
                    if hasattr(event, 'type') and event.type == 'm.room.message':
                        timestamp = getattr(event, 'origin_server_ts', 0)
                        if timestamp:
                            from datetime import datetime
                            dt = datetime.fromtimestamp(timestamp / 1000)
                            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            time_str = "Unknown time"
                        
                        body = event.content.body
                        if body.startswith("ENC:"):
                            ciphertext = body[4:]
                            key = user_keys.get(event.sender)
                            if key:
                                try:
                                    decrypted = vigenere_decrypt(ciphertext, key)
                                    print(f"[{time_str}] {event.sender}: {decrypted} (decrypted)")
                                except Exception as e:
                                    print(f"[{time_str}] {event.sender}: {body} (decryption failed: {e})")
                            else:
                                print(f"[{time_str}] {event.sender}: {body} (encrypted, no key available)")
                        else:
                            print(f"[{time_str}] {event.sender}: {body}")
            
            print("=" * 60)
        else:
            print("Failed to retrieve messages from the room.")
            
    except Exception as e:
        print(f"Error viewing room messages: {e}")
        import traceback
        traceback.print_exc()

# Matrix event handlers
async def message_callback(room: MatrixRoom, event: RoomMessageText):
    """Handle incoming messages"""
    try:
        # Check if the message is encrypted with our format
        if event.body.startswith("ENC:"):
            ciphertext = event.body[4:]
            user_id = event.sender
            
            if user_id in user_keys:
                key = user_keys[user_id]
                decrypted = vigenere_decrypt(ciphertext, key)
                print(f"\n🔓 Decrypted message from {user_id}: {decrypted}")
            else:
                print(f"\n⚠️  Received encrypted message from {user_id}, but no key available")
                print(f"Message: {ciphertext}")
        else:
            print(f"\n📨 Message from {event.sender}: {event.body}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

async def start_sync():
    """Start syncing with the Matrix server"""
    if client:
        client.add_event_callback(message_callback, RoomMessageText)
        try:
            while True:
                await client.sync(timeout=30000, full_state=False)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Sync error: {e}")

async def send_encrypted_message(message, key):
    """Send an encrypted message to the current Matrix room"""
    global current_room_id
    
    if not current_room_id:
        print("No room configured. Please set up a room first.")
        return False
    
    encrypted = vigenere_encrypt(message, key)
    try:
        resp = await client.room_send(
            room_id=current_room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": f"ENC:{encrypted}"
            }
        )
        # Check if response indicates success (no error)
        if hasattr(resp, 'event_id') and resp.event_id:
            print("✅ Encrypted message sent successfully")
            return True
        else:
            print(f"Send failed: {resp}")
            return False
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False

async def main_loop():
    """Main application loop"""
    global current_room_id
    
    # Set up the client
    if not await setup_client():
        print("Failed to set up client. Exiting.")
        return
    
    # Load room ID from config if not set
    config = load_config()
    if not current_room_id and config.get('room_id'):
        current_room_id = config['room_id']
    
    # Start syncing in the background
    asyncio.create_task(start_sync())
    
    while True:
        print("\n" + "="*50)
        print("Vigenère Encrypted Matrix Messenger")
        print("="*50)
        print(f"User: {client.user_id if client else 'Not set'}")
        print(f"Room: {current_room_id or 'Not set'}")
        print("="*50)
        print("Options:")
        print("1. Set encryption key for a user")
        print("2. Send encrypted message")
        print("3. Change room")
        print("4. Reconfigure client")
        print("5. View room messages")
        print("6. Exit")
        
        try:
            choice = input("Choose an option: ").strip()
            
            if choice == "1":
                user_id = input("Enter user ID (e.g., @user:matrix.org): ").strip()
                key = input("Enter encryption key: ").strip()
                if user_id and key:
                    user_keys[user_id] = key
                    print(f"Key set for {user_id}")
                else:
                    print("User ID and key cannot be empty.")
                    
            elif choice == "2":
                if not user_keys:
                    print("No encryption keys set. Please set a key first.")
                    continue
                    
                if not current_room_id:
                    print("No room configured. Please set up a room first.")
                    continue

                print("Available users:")
                for i, uid in enumerate(user_keys.keys(), 1):
                    print(f"{i}. {uid}")
                try:
                    sel = int(input("Select user to send to (number): ")) - 1
                    users_list = list(user_keys.items())
                    if 0 <= sel < len(users_list):
                        selected_user_id, key = users_list[sel]
                        message = input("Enter message to encrypt and send: ").strip()
                        if message:
                            await send_encrypted_message(message, key)
                            print(f"Encrypted and sent to {selected_user_id} using shared key.")
                        else:
                            print("Message cannot be empty.")
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                
            elif choice == "3":
                await setup_room(load_config())
                
            elif choice == "4":
                # Reconfigure client
                if await setup_client():
                    config = load_config()
                    if config.get('room_id'):
                        current_room_id = config['room_id']
                    # Restart sync
                    asyncio.create_task(start_sync())
            
            elif choice == "5":
                await view_room_messages()
                
            elif choice == "6":
                print("Exiting...")
                if client:
                    await client.close()
                break
                
            else:
                print("Invalid option. Please choose 1-6.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            if client:
                await client.close()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if client:
            asyncio.run(client.close())