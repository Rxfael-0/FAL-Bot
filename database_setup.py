import sqlite3
import os


# ============================================================
# CONFIGURAÇÃO
# ============================================================

DATABASE_FOLDER = "database"
DATABASE = os.path.join(
    DATABASE_FOLDER,
    "database.db"
)


# ============================================================
# CRIAR PASTA
# ============================================================

os.makedirs(
    DATABASE_FOLDER,
    exist_ok=True
)


# ============================================================
# CONEXÃO
# ============================================================

conn = sqlite3.connect(
    DATABASE
)

cursor = conn.cursor()


# ============================================================
# PLAYERS
# ============================================================

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


# ============================================================
# CLANS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS clans (

    name TEXT PRIMARY KEY,

    data TEXT NOT NULL

)
""")


# ============================================================
# HALL DA FAMA
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS hall (

    id TEXT PRIMARY KEY,

    data TEXT NOT NULL

)
""")


# ============================================================
# TOURNAMENT
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS tournament (

    id INTEGER PRIMARY KEY CHECK (id = 1),

    active INTEGER DEFAULT 0,

    name TEXT DEFAULT '',

    max_players INTEGER DEFAULT 32,

    players TEXT DEFAULT '[]',

    matches TEXT DEFAULT '[]',

    champion INTEGER

)
""")


# ============================================================
# CRIAR TORNEIO PADRÃO
# ============================================================

cursor.execute("""
INSERT OR IGNORE INTO tournament (
    id,
    active,
    name,
    max_players,
    players,
    matches,
    champion
)
VALUES (
    1,
    0,
    '',
    32,
    '[]',
    '[]',
    NULL
)
""")


# ============================================================
# SALVAR
# ============================================================

conn.commit()
conn.close()


print("✅ Banco de dados carregado.")
