import random
import os
import logging
import asyncio
import telethon
import time
from telethon import Button
from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
import pymongo
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(__name__)

MONGO_URI = "mongodb+srv://ladisak673_db_user:JMMYnzOPl4iBEvq2@mention.a2nbbtz.mongodb.net/?appName=mention"

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
stats_collection = db["bot_stats"]
broadcasts_collection = db["broadcasts"]
spam_collection = db["spam_chats"]

emojis = ["😀", "😍", "🤣", "👍", "🌟", "🎉", "👏", "🤔", "😎", "🥰", "🥳", "🙌", "🌺", "🎈", "🌞", "🌍", "🎶", "🍕", "🍦", "🚀"]
api_id = int(8447214)
api_hash = "9ec5782ddd935f7e2763e5e49a590c0d"
bot_token = "8183522431:AAGwFEjqcciFW7jqQUbEP_F3tYo2V35c-hA"
client = TelegramClient('client61727', api_id, api_hash).start(bot_token=bot_token)

async def init_mongo_stats():
    existing = stats_collection.find_one({"bot_id": "serena"})
    if not existing:
        stats_collection.insert_one({
            "bot_id": "serena",
            "total_groups": 0,
            "total_users": 0,
            "total_broadcasts": 0,
            "total_mentions": 0,
            "created_at": time.time()
        })

async def update_bot_stats():
    try:
        groups = 0
        users = 0
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                groups += 1
                try:
                    async for participant in client.iter_participants(dialog.entity):
                        users += 1
                except:
                    continue
            elif dialog.is_user:
                users += 1
        
        stats_collection.update_one(
            {"bot_id": "serena"},
            {"$set": {
                "total_groups": groups,
                "total_users": users,
                "last_updated": time.time()
            }}
        )
    except Exception as e:
        LOGGER.error(f"Error updating stats: {e}")

async def get_bot_stats():
    stats = stats_collection.find_one({"bot_id": "serena"})
    if not stats:
        await init_mongo_stats()
        stats = stats_collection.find_one({"bot_id": "serena"})
    return stats

async def add_spam_chat(chat_id):
    spam_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"added_at": time.time()}},
        upsert=True
    )

async def remove_spam_chat(chat_id):
    spam_collection.delete_one({"chat_id": chat_id})

async def is_spam_chat(chat_id):
    chat = spam_collection.find_one({"chat_id": chat_id})
    return chat is not None

async def record_broadcast(sender_id, sent_count, failed_count, broadcast_type):
    broadcasts_collection.insert_one({
        "sender_id": sender_id,
        "sent_count": sent_count,
        "failed_count": failed_count,
        "type": broadcast_type,
        "timestamp": time.time()
    })
    stats_collection.update_one(
        {"bot_id": "serena"},
        {"$inc": {"total_broadcasts": 1}}
    )

async def record_mention(chat_id, sender_id, user_count):
    stats_collection.update_one(
        {"bot_id": "serena"},
        {"$inc": {"total_mentions": 1}}
    )

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
    await client.send_message(
        event.chat_id,
        "__**I'm @SerenaProBot**, I can mention almost all members in group or channel 👻\nClick **/help** for more information__\n\n**Join @AshxBots For Latest Updates**",
        link_preview=False,
        buttons=(
            [
                Button.url('📦 Owner', 'https://t.me/Ashketchum_001')
            ]
        )
    )

@client.on(events.NewMessage(pattern="^/help$"))
async def help(event):
    helptext = """**Help Menu of @SerenaProBot**

**Tagging Commands:**
• `/mention` or `/tagall` - Mention all members with text
• `/emoji` - Mention all members with emojis
• `/cancel` - Cancel ongoing mention

**Broadcast Commands:**
• `/broadcast` - Broadcast to all groups & users
• `/ubroadcast` - Broadcast only to users

**Info Commands:**
• `/botstats` - Show bot statistics

**Usage Examples:**
• `/mention Good Morning!`
• `/emoji` (reply to a message)
• Reply to any message with `/broadcast`

__Note: Mention commands are for admins only.__

**Join @AshxBots For Latest Updates**"""
    
    await event.reply(
        helptext,
        link_preview=False,
        buttons=(
            [
                Button.url('📦 Owner', 'https://t.me/Ashketchum_001')
            ]
        )
    )

@client.on(events.NewMessage(pattern="^/(mention|tagall|utag|tagx|mentionall|chutiyo|bachhelog)(?:\s+(.*))?"))
async def mentionall(event):
    chat_id = event.chat_id

    if event.is_private:
        return await event.reply("🚫 This command can only be used in groups!")

    is_admin = False
    try:
        participant = await client(GetParticipantRequest(chat_id, event.sender_id))
        if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            is_admin = True
    except UserNotParticipantError:
        pass

    if not is_admin:
        return await event.reply("❌ Only admins can mention all members!")

    if await is_spam_chat(chat_id):
        return await event.reply("⚠️ Tagging is already in progress...")

    mode = None
    message = None
    if event.pattern_match.group(2):
        mode = "text_on_cmd"
        message = event.pattern_match.group(2)
    elif event.is_reply:
        mode = "text_on_reply"
        message = await event.get_reply_message()
        if not message:
            return await event.reply("⚠️ Cannot mention users for very old messages!")
    else:
        return await event.reply("❓ Provide some text or reply to a message to tag everyone.")

    await add_spam_chat(chat_id)
    user_count = 0
    tag_text = ''
    total_tagged = 0

    async for user in client.iter_participants(chat_id):
        if not await is_spam_chat(chat_id):
            break

        user_count += 1
        total_tagged += 1
        tag_text += f"<a href='tg://user?id={user.id}'> {user.first_name}</a> "

        if user_count == 7:
            try:
                if mode == "text_on_cmd":
                    await client.send_message(chat_id, f"{tag_text}\n\n<b>{message}</b>", parse_mode='HTML')
                elif mode == "text_on_reply":
                    await message.reply(tag_text, parse_mode='HTML')
            except Exception as e:
                LOGGER.error(f"Error sending message: {e}")
            await asyncio.sleep(1.5)
            user_count = 0
            tag_text = ''

    await remove_spam_chat(chat_id)
    await record_mention(chat_id, event.sender_id, total_tagged)
    await client.send_message(chat_id, "✅ Finished mentioning everyone!\nJoin @AshxBots", parse_mode='HTML')

@client.on(events.NewMessage(pattern="^/emoji ?(.*)"))
async def mentionall(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond("__This command can be use in groups and channels!__")
    
    is_admin = False
    try:
        partici_ = await client(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            is_admin = True
    
    if not is_admin:
        return await event.respond("__Only admins can mention all!__")

    if await is_spam_chat(event.chat_id):
        return await event.respond('**There is already proccess on going...**')

    if event.is_reply:
        mode = "text_on_reply"
        msg = await event.get_reply_message()
        if msg == None:
            return await event.respond("__I can't mention members for older messages! (messages which are sent before I'm added to group)__")
    else:
        return await event.respond("__Reply to a message to mention others with emoji!__")

    await add_spam_chat(chat_id)
    usrnum = 0
    usrtxt = ''
    total_tagged = 0
    
    async for usr in client.iter_participants(chat_id):
        if not await is_spam_chat(chat_id):
            break
        usrnum += 1
        total_tagged += 1
        usrtxt += f"<a href ='tg://user?id={usr.id}'><b>  {random.choice(emojis)}</b></a>"
        if usrnum == 30:
            if mode == "text_on_cmd":
                txt = f"{usrtxt}\n\n<b>{msg}</b>"
                await client.send_message(chat_id, txt, parse_mode='HTML')
            elif mode == "text_on_reply":
                await msg.reply(usrtxt, parse_mode='HTML')
            await asyncio.sleep(1.5)
            usrnum = 0
            usrtxt = ''
    
    await remove_spam_chat(chat_id)
    await record_mention(chat_id, event.sender_id, total_tagged)
    await client.send_message(chat_id, '<b>Mentioning All Users Done ✅</b>', parse_mode='HTML')

@client.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
    if not await is_spam_chat(event.chat_id):
        return await event.respond('__There is no proccess on going...__')
    else:
        await remove_spam_chat(event.chat_id)
        return await event.respond('__Stopped.__')

@client.on(events.NewMessage(pattern="^/botstats$"))
async def botstats(event):
    await update_bot_stats()
    stats = await get_bot_stats()
    
    uptime_seconds = time.time() - stats.get("created_at", time.time())
    uptime_days = int(uptime_seconds // 86400)
    uptime_hours = int((uptime_seconds % 86400) // 3600)
    
    stats_text = f"""**🤖 Bot Statistics**

📊 **Total Groups/Channels:** `{stats.get('total_groups', 0)}`
👥 **Total Users:** `{stats.get('total_users', 0)}`
📨 **Total Broadcasts Sent:** `{stats.get('total_broadcasts', 0)}`
🔖 **Total Mentions Done:** `{stats.get('total_mentions', 0)}`

⏰ **Uptime:** {uptime_days}d {uptime_hours}h
📈 **Bot Status:** ✅ Online

**Join @AshxBots For Updates**"""
    
    await event.reply(
        stats_text,
        link_preview=False,
        buttons=(
            [
                Button.url('📦 Owner', 'https://t.me/Ashketchum_001'),
                Button.url('📢 Channel', 'https://t.me/AshxBots')
            ]
        )
    )

@client.on(events.NewMessage(pattern="^/(broadcast|ubroadcast)$"))
async def broadcast(event):
    owner_ids = [6875482068]
    
    if event.sender_id not in owner_ids:
        return await event.reply("❌ This command is only for bot owner!")
    
    if not event.is_reply:
        return await event.reply("❌ Please reply to a message to broadcast!")
    
    message = await event.get_reply_message()
    
    broadcast_type = "all chats" if event.pattern_match.group(1) == "broadcast" else "users only"
    confirm_msg = await event.reply(
        f"⚠️ **Confirm Broadcast**\n\n"
        f"Type: `{broadcast_type}`\n"
        f"Are you sure you want to broadcast this message?\n\n"
        f"Reply with **YES** to confirm or **NO** to cancel."
    )
    
    try:
        response = await client.wait_event(
            events.NewMessage(from_users=event.sender_id, chats=event.chat_id),
            timeout=30
        )
        
        if response.text.upper() == "YES":
            await confirm_msg.edit("✅ **Broadcast started...**")
            
            sent_count = 0
            failed_count = 0
            
            async for dialog in client.iter_dialogs():
                try:
                    if event.pattern_match.group(1) == "ubroadcast":
                        if dialog.is_user and not dialog.entity.bot:
                            await client.send_message(dialog.entity.id, message)
                            sent_count += 1
                            await asyncio.sleep(0.5)
                    else:
                        await client.send_message(dialog.entity.id, message)
                        sent_count += 1
                        await asyncio.sleep(0.5)
                        
                except Exception as e:
                    LOGGER.error(f"Failed to send to {dialog.id}: {e}")
                    failed_count += 1
                    continue
            
            await record_broadcast(event.sender_id, sent_count, failed_count, event.pattern_match.group(1))
            
            await event.reply(
                f"✅ **Broadcast Completed!**\n\n"
                f"📤 Successfully sent to: `{sent_count}` chats\n"
                f"❌ Failed to send: `{failed_count}` chats\n"
                f"📊 Total broadcasts: `{(await get_bot_stats()).get('total_broadcasts', 0)}`"
            )
            
        elif response.text.upper() == "NO":
            await confirm_msg.edit("❌ **Broadcast cancelled.**")
        else:
            await confirm_msg.edit("❌ **Invalid response. Broadcast cancelled.**")
            
    except asyncio.TimeoutError:
        await confirm_msg.edit("❌ **Confirmation timeout. Broadcast cancelled.**")
    except Exception as e:
        LOGGER.error(f"Broadcast error: {e}")
        await event.reply(f"❌ **Error during broadcast:** `{str(e)}`")

async def periodic_stats_update():
    while True:
        try:
            await update_bot_stats()
            await asyncio.sleep(3600)
        except:
            await asyncio.sleep(300)

async def cleanup_spam_chats():
    while True:
        try:
            cutoff = time.time() - 3600
            spam_collection.delete_many({"added_at": {"$lt": cutoff}})
            await asyncio.sleep(1800)
        except:
            await asyncio.sleep(300)

client.loop.create_task(init_mongo_stats())
client.loop.create_task(periodic_stats_update())
client.loop.create_task(cleanup_spam_chats())

print(">> BOT STARTED <<")
client.run_until_disconnected()