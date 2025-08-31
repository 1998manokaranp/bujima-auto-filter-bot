# By ThiruXD

from pymongo import MongoClient
from info import DATABASE_URI, DATABASE_NAME

client = MongoClient(DATABASE_URI)  # adjust URI if needed
fsub_db = client[DATABASE_NAME]

force_channels_collection = fsub_db['force_channels']

async def get_force_sub_channels():
    return list(force_channels_collection.find({}))

async def add_force_sub_channel(chat_id):
    force_channels_collection.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)

async def remove_force_sub_channel(chat_id):
    force_channels_collection.delete_one({"chat_id": chat_id})

async def is_force_sub_channel(chat_id):
    return force_channels_collection.find_one({"chat_id": chat_id}) is not None
