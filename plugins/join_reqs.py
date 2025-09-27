import motor.motor_asyncio
from info import DATABASE_URI, ADMINS
import os
from pyrogram import Client, filters, enums
from pymongo import MongoClient
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest
from pyrogram.errors import *

# MongoDB setup
old_client = MongoClient(DATABASE_URI)
old_db = old_client['techvj']
channels_collection = old_db['channels']

class JoinReqs:

    def __init__(self):
        if DATABASE_URI:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
            self.db = self.client["JoinReqs"]
            self.col = self.db["techvj"]
        else:
            self.client = None
            self.db = None
            self.col = None

    def isActive(self):
        if self.client is not None:
            return True
        else:
            return False

    async def add_user(self, user_id, first_name, username, date, channel_id):
        try:
            await self.col.insert_one({"channel_id": int(channel_id), "user_id": int(user_id), "first_name": first_name, "username": username, "date": date})
        except:
            pass

    async def get_user(self, user_id, channel_id):
        return await self.col.find_one({"user_id": int(user_id), "channel_id": int(channel_id)})

    async def get_all_users(self):
        return await self.col.find().to_list(None)

    async def delete_user(self, user_id, channel_id):
        await self.col.delete_one({"user_id": int(user_id), "channel_id": int(channel_id)})

    async def delete_all_users(self):
        await self.col.delete_many({})

    async def get_all_users_count(self):
        return await self.col.count_documents({})


@Client.on_message(filters.private & filters.command("add_channel") & filters.user(ADMINS))
async def add_channel(client, message):
    if len(message.command) != 2:
        await message.reply("Usage: /add_channel channel_id")
        return

    channel_id = message.command[1]

    try:
        try:
            info = await client.get_chat(int(channel_id))
        except:
            await message.reply("Please make me an admin in this channel.")
            return

        # Check if already exists
        if channels_collection.find_one({"channel_id": channel_id}):
            await message.reply("This channel ID is already added.")
            return

        # Add the channel ID to MongoDB
        channels_collection.insert_one({"channel_id": channel_id})
        await message.reply(f"Channel ID {channel_id} added successfully.")

    except Exception as e:
        message.reply(f"Error: {str(e)}")

@Client.on_message(filters.private & filters.command("delete_channel") & filters.user(ADMINS))
async def delete_channel(client, message):
    if len(message.command) != 2:
        await message.reply("Usage: /delete_channel channel_id")
        return

    channel_id = message.command[1]
    
    result = channels_collection.delete_one({"channel_id": channel_id})
    if result.deleted_count > 0:
        await message.reply(f"Channel ID {channel_id} deleted successfully.")
    else:
        await message.reply("Channel ID not found.")

@Client.on_message(filters.private & filters.command("list_channels") & filters.user(ADMINS))
async def list_channels(client, message):
    channels = channels_collection.find()
    if channels.count() == 0:
        await message.reply("No channels found.")
        return

    response = "Channel IDs:\n"
    for channel in channels:
        response += f"- {channel['channel_id']}\n"

    await message.reply(response)

join_db = JoinReqs

async def join_is_subscribed(bot, query, channels):
    btn = []
    for channel in channels:
        try:
            user = await join_db().get_user(query.from_user.id, channel)
            if user and user["user_id"] == query.from_user.id and user["channel_id"] == channel:
                return
            else:
                try:
                    user_data = await bot.get_chat_member(channel, query.from_user.id)
                except UserNotParticipant:
                    chat = await bot.create_chat_invite_link(chat_id=(int(channel)), creates_join_request=True)
                    btn.append(
                        [InlineKeyboardButton('Join', url=chat.invite_link)]
                    )
                except Exception as e:
                    pass
        except Exception as e:
            print(e)
    return btn


@Client.on_chat_join_request((filters.group | filters.channel))
async def join_auto_approve(client, message: ChatJoinRequest):
    if not join_db().isActive():
        return
    ap_user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    date = message.date
    chat = message.chat.id
    await join_db().add_user(user_id=ap_user_id, first_name=first_name, username=username, date=date, channel_id=chat)
  




