-- SQLite database initialization for Kou Xia

CREATE TABLE IF NOT EXISTS users (
    character_id TEXT PRIMARY KEY,
    player_name TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TEXT,
    last_login TEXT
);

CREATE TABLE IF NOT EXISTS game_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO game_state (key, value) VALUES ('act1_unlocked', '0');
INSERT OR IGNORE INTO game_state (key, value) VALUES ('act2_unlocked', '0');
INSERT OR IGNORE INTO game_state (key, value) VALUES ('act2_questions_unlocked', '0');
