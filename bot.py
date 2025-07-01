import random
import os, logging, asyncio, time, datetime
from telethon import Button
from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest, EditAdminRequest
from telethon.errors import UserNotParticipantError
from telethon.tl.types import ChatAdminRights, PeerUser
from tinydb import TinyDB, Query

# === Logging ===
logging.basicConfig(level=logging.INFO, format='%(name)s - [%(levelname)s] - %(message)s')
LOGGER = logging.getLogger(__name__)

# === Config ===
api_id = 4226067
api_hash = "2d01711f0566de2309b633f49542e7e2"
bot_token = "8134891989:AAHMEvVHGWSzux-AtQP3856X6-k2gmzQJEM"
bot_owner_id = 6279412066

# === Init ===
client = TelegramClient('client_mention', api_id, api_hash).start(bot_token=bot_token)
spam_chats = []
emojis = ["😀", "😍", "🤣", "👍", "🌟", "🎉", "👏", "🤔", "😎", "🥰", "🥳", "🙌", "🌺", "🎈", "🌞", "🌍", "🎶", "🍕", "🍦", "🚀"]
bot_start_time = time.time()

# === TinyDB ===
db = TinyDB("bot_data.json")
users_table = db.table("users")
groups_table = db.table("groups")
channels_table = db.table("channels")

# === Commands ===

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
    await client.send_message(
        event.chat_id,
        "__I'm @TagallxBot Bot, I can mention almost all members in group or channel 👻\nClick `/help` for more information__\n\nJoin @AshxBots For Latest Updates",
        link_preview=False,
        buttons=[[Button.url('📦 Owner', 'https://t.me/AshKetchum_001')]]
    )

@client.on(events.NewMessage(pattern="^/help$"))
async def help(event):
    await event.reply(
        "**Help Menu of @TagAllxBot**\n\n"
        "Commands: /mention | /emoji\n"
        "__Use with any message or reply.__\n"
        "**Examples:**\n"
        "`/mention Good Morning!`\n"
        "`/emoji Hello World!`\n"
        "`/promote Admin` (reply)\n"
        "`/fullpromote Boss` (reply)\n\n"
        "Join @AshxBots for updates.",
        link_preview=False,
        buttons=[[Button.url('📦 Owner', 'https://t.me/AshKetchum_001')]]
    )

@client.on(events.NewMessage(pattern="^/(tagall|mention|mentionall|utag|loud) ?(.*)"))
async def mention_all(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.reply("__This command can only be used in groups and channels!__")

    try:
        participant = await client(GetParticipantRequest(chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("__Only admins can mention all!__")
    except UserNotParticipantError:
        return await event.reply("__Only admins can mention all!__")

    if chat_id in spam_chats:
        return await event.reply("**There is already a process ongoing...**")

    msg = event.pattern_match.group(2) or "Hello everyone!"
    spam_chats.append(chat_id)

    usrnum = 0
    usrtxt = ''
    async for usr in client.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break
        usrnum += 1
        usrtxt += f"<a href='tg://user?id={usr.id}'><b>{usr.first_name}</b></a>, "
        if usrnum == 7:
            await client.send_message(chat_id, f"{usrtxt}\n\n<b>{msg}</b>", parse_mode='html')
            await asyncio.sleep(1.5)
            usrnum = 0
            usrtxt = ''

    spam_chats.remove(chat_id)
    await client.send_message(chat_id, "<b>✅ Mentioning All Users Done</b>\nJoin @AshxBots", parse_mode='html')

@client.on(events.NewMessage(pattern="^/emoji ?(.*)"))
async def mention_with_emoji(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.reply("__This command can only be used in groups and channels!__")

    try:
        participant = await client(GetParticipantRequest(chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("__Only admins can mention all!__")
    except UserNotParticipantError:
        return await event.reply("__Only admins can mention all!__")

    if chat_id in spam_chats:
        return await event.reply("**There is already a process ongoing...**")

    if not event.is_reply:
        return await event.reply("__Reply to a message to mention others with emoji!__")

    msg = await event.get_reply_message()
    spam_chats.append(chat_id)

    usrnum = 0
    usrtxt = ''
    async for usr in client.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break
        usrnum += 1
        usrtxt += f"<a href='tg://user?id={usr.id}'><b>{random.choice(emojis)}</b></a>, "
        if usrnum == 30:
            await msg.reply(usrtxt, parse_mode='html')
            await asyncio.sleep(1.5)
            usrnum = 0
            usrtxt = ''

    spam_chats.remove(chat_id)
    await client.send_message(chat_id, "<b>✅ Mentioning All Users Done</b>", parse_mode='html')

@client.on(events.NewMessage(pattern="^/(stop|stopall|cancel|unmention|untagall)$"))
async def stop_tagging(event):
    chat_id = event.chat_id
    if chat_id in spam_chats:
        spam_chats.remove(chat_id)
        return await event.reply("__Stopped mentioning users.__")
    await event.reply("__There is no process ongoing...__")

@client.on(events.NewMessage(pattern="^/broadcast$"))
async def broadcast(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ You are not authorized to use this command.")
    if not event.is_reply:
        return await event.reply("❌ Reply to the message you want to broadcast.")

    message = await event.get_reply_message()
    sent_users = sent_groups = sent_channels = 0
    failed_users = failed_groups = failed_channels = 0

    for user in users_table.all():
        try:
            await client.send_message(int(user["id"]), message)
            sent_users += 1
        except:
            failed_users += 1

    for group in groups_table.all():
        try:
            await client.send_message(int(group["id"]), message)
            sent_groups += 1
        except:
            failed_groups += 1

    for channel in channels_table.all():
        try:
            await client.send_message(int(channel["id"]), message)
            sent_channels += 1
        except:
            failed_channels += 1

    await event.reply(
        f"**✅ Broadcast Summary ✅**\n\n"
        f"👤 Users: `{sent_users}` / ❌ `{failed_users}`\n"
        f"👥 Groups: `{sent_groups}` / ❌ `{failed_groups}`\n"
        f"📢 Channels: `{sent_channels}` / ❌ `{failed_channels}`"
    )

@client.on(events.NewMessage(pattern="^/botstats$"))
async def bot_stats(event):
    if event.sender_id != bot_owner_id:
        return await event.reply("❌ You are not authorized to use this command.")
    uptime = str(datetime.timedelta(seconds=int(time.time() - bot_start_time)))
    await event.reply(
        f"**🤖 Bot Statistics**\n\n"
        f"🟢 **Online**\n"
        f"⏱ **Uptime:** `{uptime}`\n"
        f"👤 **Users:** `{len(users_table)}`\n"
        f"👥 **Groups:** `{len(groups_table)}`\n"
        f"📢 **Channels:** `{len(channels_table)}`"
    )

@client.on(events.ChatAction)
async def track_chats(event):
    chat = await event.get_chat()
    chat_id = chat.id
    if event.user_added or event.user_joined:
        if chat.broadcast:
            if not channels_table.contains(Query().id == chat_id):
                channels_table.insert({"id": chat_id})
        elif chat.megagroup:
            if not groups_table.contains(Query().id == chat_id):
                groups_table.insert({"id": chat_id})
        else:
            if not users_table.contains(Query().id == chat_id):
                users_table.insert({"id": chat_id})

@client.on(events.NewMessage(pattern="^/promote$"))
async def promote(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Use in group and reply to user.")
    reply = await event.get_reply_message()
    rights = ChatAdminRights(delete_messages=True, invite_users=True, pin_messages=True, manage_call=True)
    try:
        await client(EditAdminRequest(event.chat_id, PeerUser(reply.sender_id), rights, "Group Admin"))
        await event.reply(f"✅ Promoted [{reply.sender.first_name}](tg://user?id={reply.sender_id})", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Error:\n`{str(e)}`")

@client.on(events.NewMessage(pattern="^/fullpromote$"))
async def full_promote(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Use in group and reply to user.")
    reply = await event.get_reply_message()
    rights = ChatAdminRights(
        change_info=True, delete_messages=True, ban_users=True, invite_users=True,
        pin_messages=True, add_admins=True, anonymous=True, manage_call=True
    )
    try:
        await client(EditAdminRequest(event.chat_id, PeerUser(reply.sender_id), rights, "Full Admin"))
        await event.reply(f"✅ Fully Promoted [{reply.sender.first_name}](tg://user?id={reply.sender_id})", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Error:\n`{str(e)}`")

@client.on(events.NewMessage(pattern="^/(contact|owner|about|support)$"))
async def contact_info(event):
    await event.reply(
        file="https://files.catbox.moe/4xwtlr.jpg",
        message="📞 **Contact Information**\n\n🔹 **Updates**: @AshxBots\n🔹 Developer: @AshKetchum_001",
        buttons=[[Button.url("❤️ Developer", "https://t.me/AshKetchum_001")]],
        link_preview=False
    )

# === Start Bot ===
print(">> BOT STARTED <<")
client.run_until_disconnected()