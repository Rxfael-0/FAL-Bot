import sqlite3
import os

# =========================
# DATABASE
# =========================

os.makedirs("database", exist_ok=True)

DATABASE = "database/database.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# =========================
# PLAYERS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (

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

# =========================
# CLANS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS clans (

    name TEXT PRIMARY KEY,
    data TEXT

)
""")

# =========================
# HALL DA FAMA
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS hall (

    id TEXT PRIMARY KEY,
    data TEXT

)
""")

# =========================
# TOURNAMENT
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS tournament (

    user_id INTEGER PRIMARY KEY,

    tipo TEXT,
    nome TEXT,
    roblox TEXT,
    convidado TEXT,

    validado INTEGER DEFAULT 0

)
""")

# =========================
# SALVAR
# =========================

conn.commit()
conn.close()

print("✅ Banco de dados carregado.")
