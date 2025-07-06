import aiosqlite
import os

class SQLiteManager:
    def __init__(self, db_path='gitflow_studio.db'):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    name TEXT,
                    last_opened TIMESTAMP
                )
            ''')
            await db.commit()

    async def execute(self, query, params=None):
        async with aiosqlite.connect(self.db_path) as db:
            if params is None:
                params = ()
            await db.execute(query, params)
            await db.commit()

    async def fetchall(self, query, params=None):
        async with aiosqlite.connect(self.db_path) as db:
            if params is None:
                params = ()
            async with db.execute(query, params) as cursor:
                return await cursor.fetchall() 