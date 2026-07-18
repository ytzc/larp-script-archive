-- SQLite database initialization for Kou Xia

CREATE TABLE IF NOT EXISTS users (
    character_id TEXT PRIMARY KEY,
    player_name TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TEXT,
    last_login TEXT,
    last_seen TEXT
);

CREATE TABLE IF NOT EXISTS game_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS private_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    sender_id TEXT,
    recipient_id TEXT
);

CREATE TABLE IF NOT EXISTS ai_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER UNIQUE NOT NULL,
    status TEXT NOT NULL,
    attempts INTEGER DEFAULT 0,
    error TEXT,
    locked_at TEXT,
    worker_id TEXT,
    reply_message_id INTEGER,
    created_at TEXT,
    processed_at TEXT,
    FOREIGN KEY(message_id) REFERENCES private_messages(id),
    FOREIGN KEY(reply_message_id) REFERENCES private_messages(id)
);

INSERT OR IGNORE INTO game_state (key, value) VALUES ('act1_unlocked', '0');
INSERT OR IGNORE INTO game_state (key, value) VALUES ('act2_unlocked', '0');
INSERT OR IGNORE INTO game_state (key, value) VALUES ('act2_questions_unlocked', '0');

