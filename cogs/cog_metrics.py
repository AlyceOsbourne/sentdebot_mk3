"""Cog to handle metrics data collection and storing in a database."""
import asyncio
import os
import time

import aiosqlite
import nextcord
from matplotlib import pyplot as plt
from nextcord.ext import commands, tasks

default_data_collection_config = {
    "metrics_folder": "metrics",
    "metrics_db_name": "metrics.db",
}
default_graph_builder_config = {
    "graphs_folder": "metrics",
    "num_top_users": 5,
    "days": 21,
    "channels": [],

}


class DataCollector(commands.Cog, name="Metric Tool"):
    create_users_query = \
        "CREATE TABLE IF NOT EXISTS users (" \
        "user_id PRIMARY KEY, " \
        "user_name TEXT, " \
        "user_nick TEXT, " \
        "status TEXT)"

    create_channels_query = \
        "CREATE TABLE IF NOT EXISTS channels (" \
        "channel_id PRIMARY KEY," \
        "channel_name TEXT," \
        "channel_type TEXT," \
        "message_id INTEGER," \
        "FOREIGN KEY(message_id) REFERENCES messages(message_id))"

    create_messages_query = \
        "CREATE TABLE IF NOT EXISTS messages (" \
        "message_id PRIMARY KEY," \
        "channel_id INTEGER," \
        "timestamp INTEGER," \
        "user_id INTEGER," \
        "FOREIGN KEY(user_id) REFERENCES users(user_id))"

    create_cleanup_routine = \
        "CREATE TRIGGER IF NOT EXISTS cleanup_messages AFTER INSERT ON messages " \
        "BEGIN " \
        "DELETE FROM messages WHERE timestamp < strftime('%s', 'now', '-21 days');" \
        "END"

    db_creation_queries = [
        create_users_query,
        create_channels_query,
        create_messages_query,
        create_cleanup_routine
    ]

    def __init__(self, bot):
        self.bot = bot
        # copy of default config
        self.config = default_data_collection_config.copy()
        self.path = os.path.join(
            self.config.get("metrics_folder"),
            self.config.get("metrics_db_name")
        )

    @commands.Cog.listener()
    async def on_ready(self):
        if not os.path.exists(self.path):
            os.makedirs(self.config.get("metrics_folder"), exist_ok=True)
        async with aiosqlite.connect(self.path) as db:
            for query in self.db_creation_queries:
                await db.execute(query)
            await db.commit()
        guild_id = self.bot.config.get("guild_id")
        guild = self.bot.get_guild(guild_id)
        if guild:
            for member in guild.members:
                await self.add_user(member)
            for channel in guild.channels:
                await self.add_channel(channel)

    async def add_user(self, member):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, user_name, user_nick, status) VALUES (?, ?, ?, ?)",
                (member.id, member.name, member.nick, member.status.value)
            )
            await db.commit()

    async def remove_user(self, member):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "DELETE FROM users WHERE user_id = ?",
                (member.id,)
            )
            await db.commit()

    async def add_channel(self, channel):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO channels (channel_id, channel_name, channel_type) VALUES (?, ?, ?)",
                (channel.id, str(channel.name), channel.type.name)
            )
            await db.commit()

    async def remove_channel(self, channel):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "DELETE FROM channels WHERE channel_id = ?",
                (channel.id,)
            )
            await db.commit()

    async def add_message(self, message):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO messages (message_id, channel_id, timestamp, user_id) VALUES (?, ?, ?, ?)",
                (message.id, message.channel.id, round(message.created_at.timestamp()), message.author.id)
            )
            await db.commit()

    async def remove_message(self, message):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "DELETE FROM messages WHERE message_id = ?",
                (message.id,)
            )
            await db.commit()

    ####################################################################################################################

    async def get_top_users_for_channel(self, channel_name):
        users_and_counts = {}
        async with aiosqlite.connect(self.config.get("metrics_db_name")) as db:
            async for row in await db.execute(
                    "SELECT user_name, COUNT(message_id) AS message_count FROM messages "
                    "JOIN users ON messages.user_id = users.user_id "
                    "WHERE channel_name = ? "
                    "GROUP BY user_name "
                    "ORDER BY message_count DESC "
                    "LIMIT 10",
                    (channel_name,)
            ):
                users_and_counts[row[0]] = row[1]
        return users_and_counts

    async def get_top_users_for_channels(self, channels):
        channels_and_users = {}
        for channel in channels:
            channels_and_users[channel] = await self.get_top_users_for_channel(channel)
        return channels_and_users

    async def get_top_channels_for_user(self, user_name):
        channels_and_counts = {}
        async with aiosqlite.connect(self.config.get("metrics_db_name")) as db:
            async for row in await db.execute(
                    "SELECT channel_name, COUNT(message_id) AS message_count FROM messages "
                    "JOIN users ON messages.user_id = users.user_id "
                    "WHERE user_name = ? "
                    "GROUP BY channel_name "
                    "ORDER BY message_count DESC "
                    "LIMIT 5",
                    (user_name,)
            ):
                channels_and_counts[row[0]] = row[1]
        return channels_and_counts

    async def get_user_activity_for_days(self, days):
        num_users_per_day = {}
        async with aiosqlite.connect(self.config.get("metrics_db_name")) as db:
            async for row in await db.execute(
                    "SELECT strftime('%Y-%m-%d', timestamp) AS date, COUNT(user_id) AS user_count "
                    "FROM messages "
                    "GROUP BY date "
                    "ORDER BY date ASC "
                    "LIMIT ?",
                    (days,)
            ):
                num_users_per_day[row[0]] = row[1]
        return num_users_per_day

    async def get_top_channels_for_guild(self, days):
        channels_and_counts = {}
        async with aiosqlite.connect(self.config.get("metrics_db_name")) as db:
            async for row in await db.execute(
                    "SELECT channel_name, COUNT(message_id) AS message_count FROM messages "
                    "JOIN channels ON messages.channel_id = channels.channel_id "
                    "WHERE channel_type = 'text' "
                    "GROUP BY channel_name "
                    "ORDER BY message_count DESC "
                    "LIMIT ?",
                    (days,)
            ):
                channels_and_counts[row[0]] = row[1]
        return channels_and_counts


def setup(bot):
    bot.add_cog(DataCollector(bot))
