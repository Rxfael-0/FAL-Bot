import sqlite3
import os

os.makedirs("database", exist_ok=True)

conn = sqlite3.connect(
    "database/database.db"
)

cursor = conn.cursor()

cursor.execute("""

DROP TABLE IF EXISTS players

""")

cursor.execute("""

CREATE TABLE players (

    user_id INTEGER PRIMARY KEY,

    trofeus INTEGER DEFAULT 0,
    medalhas INTEGER DEFAULT 0,
    coins INTEGER DEFAULT 0,

    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,

    shop_week INTEGER DEFAULT 0,

    seasonwins TEXT DEFAULT '[]',
    medals TEXT DEFAULT '[]',
    hall TEXT DEFAULT '[]',
    partidas TEXT DEFAULT '[]'

)

""")

cursor.execute("""

CREATE TABLE IF NOT EXISTS clans (

    name TEXT PRIMARY KEY,

    leader TEXT,
    coleader TEXT,

    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    surrenders INTEGER DEFAULT 0,

    status TEXT,
    last_activity TEXT,

    role_id INTEGER,
    channel_id INTEGER,

    panel_channel INTEGER,
    panel_message INTEGER,

    logo TEXT

)

""")

conn.commit()
conn.close()

print("✅ Banco criado.")
