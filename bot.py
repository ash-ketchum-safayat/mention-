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

warnings_table = db.table("warnings")

@client.on(events.NewMessage(pattern="^/warn$"))
async def warn_user(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Reply to someone in group to warn.")
    
    user_id = event.reply_to_msg_id
    warned_user = (await event.get_reply_message()).sender_id
    key = f"{event.chat_id}:{warned_user}"
    
    entry = warnings_table.get(Query().key == key)
    count = entry["count"] + 1 if entry else 1
    
    if entry:
        warnings_table.update({"count": count}, Query().key == key)
    else:
        warnings_table.insert({"key": key, "count": count})
    
    await event.reply(f"⚠️ Warned user. Total warnings: `{count}`")

@client.on(events.NewMessage(pattern="^/warnings$"))
async def check_warns(event):
    if not event.is_reply:
        return await event.reply("Reply to user to check warnings.")
    
    warned_user = (await event.get_reply_message()).sender_id
    key = f"{event.chat_id}:{warned_user}"
    entry = warnings_table.get(Query().key == key)
    count = entry["count"] if entry else 0
    
    await event.reply(f"🚨 Total warnings: `{count}`")

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
    user_id = event.sender_id
    if not users_table.contains(Query().id == user_id):
        users_table.insert({"id": user_id})

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

@client.on(events.NewMessage(pattern="^/id$"))
async def get_id(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        await event.reply(f"🆔 User ID: `{reply.sender_id}`\n🗨 Message ID: `{reply.id}`")
    else:
        await event.reply(f"🆔 Your ID: `{event.sender_id}`\n📍Chat ID: `{event.chat_id}`")

@client.on(events.NewMessage(pattern="^/(dice|roll)$"))
async def roll_dice(event):
    result = random.randint(1, 6)
    await event.reply(f"🎲 You rolled a `{result}`!")

@client.on(events.NewMessage(pattern="^/tagadmins$"))
async def tag_admins(event):
    if event.is_private:
        return await event.reply("❌ Only in groups.")
    msg = "⚠️ Calling All Admins:\n"
    async for user in client.iter_participants(event.chat_id, filter=ChannelParticipantAdmin):
        msg += f"[{user.first_name}](tg://user?id={user.id}) "
    await event.reply(msg, parse_mode='md')

@client.on(events.NewMessage(pattern="^/ban$"))
async def ban_user(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Reply to a user in a group to ban.")
    reply = await event.get_reply_message()
    try:
        await client.edit_permissions(event.chat_id, reply.sender_id, view_messages=False)
        await event.reply(f"🚫 Banned [{reply.sender.first_name}](tg://user?id={reply.sender_id})", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Error:\n`{e}`")

@client.on(events.NewMessage(pattern="^/unban$"))
async def unban_user(event):
    if not event.is_group or not event.is_reply:
        return await event.reply("⚠️ Reply to a user in a group to unban.")
    reply = await event.get_reply_message()
    try:
        await client.edit_permissions(event.chat_id, reply.sender_id, view_messages=True)
        await event.reply(f"✅ Unbanned [{reply.sender.first_name}](tg://user?id={reply.sender_id})", parse_mode='md')
    except Exception as e:
        await event.reply(f"❌ Error:\n`{e}`")

@client.on(events.NewMessage(pattern="^/info$"))
async def userinfo(event):
    reply = await event.get_reply_message()
    user = await client.get_entity(reply.sender_id if reply else event.sender_id)
    await event.reply(
        f"**👤 User Info:**\n\n"
        f"📌 Name: `{user.first_name}`\n"
        f"🆔 User ID: `{user.id}`\n"
        f"👥 Username: `@{user.username}`\n"
        f"🌐 Data Center ID: `{user.photo.dc_id if user.photo else 'N/A'}`",
        parse_mode='md'
    )

@client.on(events.NewMessage(pattern="^/(who|whois)$"))
async def whois(event):
    if not event.is_reply:
        return await event.reply("Reply to a user to get info.")
    reply = await event.get_reply_message()
    user = await client.get_entity(reply.sender_id)
    await event.reply(
        f"**WHOIS:**\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"📝 Name: `{user.first_name}`\n"
        f"🏷 Username: @{user.username}" if user.username else "❌ No username",
        parse_mode='md'
    )

@client.on(events.NewMessage(pattern="^/clear (\d+)$"))
async def clear_messages(event):
    if not event.is_group:
        return await event.reply("⚠️ Use in groups.")
    try:
        participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("Only admins can use this.")
    except:
        return await event.reply("Only admins can use this.")
    
    count = int(event.pattern_match.group(1))
    msgs = [m async for m in client.iter_messages(event.chat_id, limit=count + 1)]
    await client.delete_messages(event.chat_id, [m.id for m in msgs])
    await event.respond(f"✅ Deleted `{count}` messages.", parse_mode='md')



@client.on(events.NewMessage(pattern="^/groupinfo$"))
async def groupinfo(event):
    if not event.is_group:
        return await event.reply("⚠️ Use in group only.")
    entity = await event.get_chat()
    members = await client.get_participants(event.chat_id)
    admins = [m async for m in client.iter_participants(event.chat_id, filter=ChannelParticipantAdmin)]
    await event.reply(
        f"**📊 Group Info:**\n\n"
        f"🧷 Title: `{entity.title}`\n"
        f"🆔 ID: `{event.chat_id}`\n"
        f"👤 Members: `{len(members)}`\n"
        f"🛡 Admins: `{len(admins)}`"
    )

@client.on(events.NewMessage(pattern="^/tagbots$"))
async def tag_bots(event):
    if not event.is_group:
        return await event.reply("Use this in group only.")
    msg = "**🤖 Bots in Group:**\n"
    count = 0
    async for user in client.iter_participants(event.chat_id):
        if user.bot:
            count += 1
            msg += f"• [{user.first_name}](tg://user?id={user.id})\n"
    await event.reply(msg if count else "❌ No bots found!", parse_mode='md')

@client.on(events.NewMessage(pattern="^/inactive$"))
async def tag_inactive(event):
    inactive = []
    async for user in client.iter_participants(event.chat_id):
        if user.status and hasattr(user.status, "was_online"):
            last_seen = user.status.was_online
            if (datetime.datetime.now(datetime.timezone.utc) - last_seen).days > 30:
                inactive.append(user)
    if not inactive:
        return await event.reply("✅ No inactive users.")
    text = "😴 Inactive users:\n"
    text += "\n".join(f"• [{u.first_name}](tg://user?id={u.id})" for u in inactive[:30])
    await event.reply(text, parse_mode='md')

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
        user_id = user.get("id")
        if not user_id: continue
        try:
            await client.send_message(int(user_id), message)
            sent_users += 1
        except Exception as e:
            LOGGER.warning(f"Failed to send to user {user_id}: {e}")
            failed_users += 1

    for group in groups_table.all():
        group_id = group.get("id")
        if not group_id: continue
        try:
            await client.send_message(int(group_id), message)
            sent_groups += 1
        except Exception as e:
            LOGGER.warning(f"Failed to send to group {group_id}: {e}")
            failed_groups += 1

    for channel in channels_table.all():
        channel_id = channel.get("id")
        if not channel_id: continue
        try:
            await client.send_message(int(channel_id), message)
            sent_channels += 1
        except Exception as e:
            LOGGER.warning(f"Failed to send to channel {channel_id}: {e}")
            failed_channels += 1

    report = (
        "**🔶 Broadcast Summary **\n\n"
        f"👤 Users: `{sent_users}` / `{failed_users}`\n"
        f"👥 Groups: `{sent_groups}` / `{failed_groups}`\n"
        f"📢 Channels: `{sent_channels}` / `{failed_channels}`"
    )
    await event.reply(report)

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

@client.on(events.NewMessage(pattern="^/tagrecent$"))
async def tag_recent(event):
    if event.is_private:
        return
    recent = []
    async for user in client.iter_participants(event.chat_id):
        if user.status and hasattr(user.status, "was_online"):
            last_seen = user.status.was_online
            if (datetime.datetime.now(datetime.timezone.utc) - last_seen).days < 2:
                recent.append(user)
    
    msg = "🔔 Active Users:\n" + ", ".join([f"<a href='tg://user?id={u.id}'>{u.first_name}</a>" for u in recent[:20]])
    await event.reply(msg, parse_mode="html")

lock_table = db.table("locks")

@client.on(events.NewMessage(pattern="^/lock (.+)"))
async def lock_type(event):
    if not event.is_group:
        return await event.reply("⚠️ Use this command in a group.")
    try:
        participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("❌ Only admins can lock content.")
    except:
        return await event.reply("❌ Only admins can lock content.")

    lock_type = event.pattern_match.group(1).lower()
    valid_locks = ["link", "sticker", "photo", "video", "gif", "document", "forward", "all"]
    if lock_type not in valid_locks:
        return await event.reply(f"⚠️ Invalid lock type.\nValid types: {', '.join(valid_locks)}")

    if lock_type == "all":
        for lt in valid_locks[:-1]:
            key = f"{event.chat_id}:{lt}"
            if not lock_table.contains(Query().key == key):
                lock_table.insert({"key": key})
        return await event.reply("🔒 Locked everything!")

    key = f"{event.chat_id}:{lock_type}"
    if not lock_table.contains(Query().key == key):
        lock_table.insert({"key": key})
        await event.reply(f"🔒 Locked `{lock_type}` messages.")
    else:
        await event.reply(f"✅ `{lock_type}` is already locked.")


@client.on(events.NewMessage(pattern="^/unlock (.+)"))
async def unlock_type(event):
    if not event.is_group:
        return await event.reply("⚠️ Use this command in a group.")
    try:
        participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return await event.reply("❌ Only admins can unlock content.")
    except:
        return await event.reply("❌ Only admins can unlock content.")

    lock_type = event.pattern_match.group(1).lower()
    valid_locks = ["link", "sticker", "photo", "video", "gif", "document", "forward", "all"]
    if lock_type not in valid_locks:
        return await event.reply(f"⚠️ Invalid unlock type.\nValid types: {', '.join(valid_locks)}")

    if lock_type == "all":
        count = 0
        for lt in valid_locks[:-1]:
            key = f"{event.chat_id}:{lt}"
            if lock_table.contains(Query().key == key):
                lock_table.remove(Query().key == key)
                count += 1
        return await event.reply(f"🔓 Unlocked `{count}` types.")

    key = f"{event.chat_id}:{lock_type}"
    if lock_table.contains(Query().key == key):
        lock_table.remove(Query().key == key)
        await event.reply(f"🔓 Unlocked `{lock_type}` messages.")
    else:
        await event.reply(f"✅ `{lock_type}` is not locked.")

@client.on(events.NewMessage(pattern="^/locks$"))
async def show_locks(event):
    if not event.is_group:
        return await event.reply("⚠️ Use in groups only.")
    types = ["link", "sticker", "photo", "video", "gif", "document", "forward"]
    locked = []
    for t in types:
        if lock_table.contains(Query().key == f"{event.chat_id}:{t}"):
            locked.append(t)
    if locked:
        await event.reply(f"🔐 **Locked types in this group:** `{', '.join(locked)}`")
    else:
        await event.reply("✅ No locks are active in this group.")


@client.on(events.NewMessage(incoming=True))
async def filter_locked_content(event):
    if event.is_private or event.sender_id == (await client.get_me()).id:
        return

    try:
        participant = await client(GetParticipantRequest(event.chat_id, event.sender_id))
        if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return  # Admins bypass lock
    except:
        pass

    msg = event.message
    cid = event.chat_id

    if msg.web_preview and lock_table.contains(Query().key == f"{cid}:link"):
        return await msg.delete()

    if msg.sticker and lock_table.contains(Query().key == f"{cid}:sticker"):
        return await msg.delete()

    if msg.photo and lock_table.contains(Query().key == f"{cid}:photo"):
        return await msg.delete()

    if msg.video and lock_table.contains(Query().key == f"{cid}:video"):
        return await msg.delete()

    if msg.gif and lock_table.contains(Query().key == f"{cid}:gif"):
        return await msg.delete()

    if msg.document and not msg.gif and lock_table.contains(Query().key == f"{cid}:document"):
        return await msg.delete()

    if msg.fwd_from and lock_table.contains(Query().key == f"{cid}:forward"):
        return await msg.delete()

welcome_table = db.table("welcome_msgs")

@client.on(events.NewMessage(pattern="^/setwelcome (.+)", func=lambda e: e.is_group))
async def set_welcome(event):
    msg = event.pattern_match.group(1)
    welcome_table.upsert({'chat_id': event.chat_id, 'msg': msg}, Query().chat_id == event.chat_id)
    await event.reply("✅ Welcome message set!")

@client.on(events.ChatAction)
async def welcome_user(event):
    if event.user_joined or event.user_added:
        entry = welcome_table.get(Query().chat_id == event.chat_id)
        if entry:
            welcome = entry["msg"]
            name = f"[{event.user.first_name}](tg://user?id={event.user.id})"
            await client.send_message(event.chat_id, welcome.replace("{name}", name), parse_mode='md')

from googletrans import Translator
translator = Translator()

@client.on(events.NewMessage(pattern="^/translate (\w+); (.+)"))
async def translate(event):
    lang, text = event.pattern_match.group(1), event.pattern_match.group(2)
    try:
        translated = translator.translate(text, dest=lang)
        await event.reply(f"🌍 Translated:\n**{translated.text}**")
    except Exception as e:
        await event.reply("❌ Could not translate.")

from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

ban_rights = ChatBannedRights(until_date=None, view_messages=True)
mute_rights = ChatBannedRights(until_date=None, send_messages=True)

@client.on(events.NewMessage(pattern="^/(ban|kick|mute)$"))
async def mod_tools(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Admins only.")
    if not event.is_reply:
        return await event.reply("Reply to user.")

    user_id = (await event.get_reply_message()).sender_id
    cmd = event.pattern_match.group(1)

    try:
        if cmd == "ban":
            await client(EditBannedRequest(event.chat_id, user_id, ban_rights))
            await event.reply("🚫 User banned.")
        elif cmd == "mute":
            await client(EditBannedRequest(event.chat_id, user_id, mute_rights))
            await event.reply("🔇 User muted.")
        elif cmd == "kick":
            await client.kick_participant(event.chat_id, user_id)
            await event.reply("👢 User kicked.")
    except Exception as e:
        await event.reply(f"❌ Error:\n{e}")

@client.on(events.NewMessage(pattern="^/menu$"))
async def show_menu(event):
    await event.respond(
        "**🧠 TagAllXBot Control Menu**\n\nChoose an option below to explore features!",
        buttons=[
            [Button.inline("👥 Mention All", b"mention_menu")],
            [Button.inline("🤖 AI Chat & Tools", b"ai_menu")],
            [Button.inline("🔐 Locks & Moderation", b"lock_menu")],
            [Button.inline("🛠 Utilities", b"util_menu")],
            [Button.inline("🎉 Fun & Games", b"fun_menu")],
            [Button.inline("📊 Bot Stats", b"stats_menu")],
        ],
        link_preview=False
    )

@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode("utf-8")

    if data == "mention_menu":
        await event.edit(
            "**👥 Mention Menu**\n\n"
            "`/mention` – Tag all users with text\n"
            "`/emoji` – Tag all with emojis\n"
            "`/stop` – Stop ongoing mention",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "ai_menu":
        await event.edit(
            "**🤖 AI & GPT Tools**\n\n"
            "`/ask <query>` – Ask ChatGPT privately\n"
            "`/aichat on/off` – Enable AI chat in group\n"
            "`@TagAllxBot` – Mention me to talk in group",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "lock_menu":
        await event.edit(
            "**🔐 Lock System**\n\n"
            "`/lock <type>` – Lock content type\n"
            "`/unlock <type>` – Unlock type\n"
            "`/locks` – Show active locks\n"
            "`/banword <word>` – Auto-delete word\n"
            "`/unbanword <word>` – Remove banned word",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "util_menu":
        await event.edit(
            "**🛠 Utilities**\n\n"
            "`/remindme 10;Take break`\n"
            "`/translate en; bonjour`\n"
            "`/invite` – Group invite link\n"
            "`/setwelcome Welcome {name}`\n"
            "`/save msg`, `/get id`",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "fun_menu":
        await event.edit(
            "**🎉 Fun & Game Commands**\n\n"
            "`/dice`, `/roll 100`\n"
            "`/reverse <text>`\n"
            "`/funify <text>`\n"
            "`/poll What?;Yes;No`",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "stats_menu":
        await event.edit(
            "**📊 Bot Stats & Admin Tools**\n\n"
            "`/botstats` – Show stats\n"
            "`/broadcast` – Send to all\n"
            "`/pinall 10` – Pin last 10 messages\n"
            "`/promote` / `/fullpromote` (reply)\n"
            "`/ban`, `/mute`, `/kick`",
            buttons=[[Button.inline("🔙 Back", b"main_menu")]]
        )

    elif data == "main_menu":
        await show_menu(event)  # Return to main menu


# === Start Bot ===
print(">> BOT STARTED <<")
client.run_until_disconnected()