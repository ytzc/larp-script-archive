#!/usr/bin/env python3
"""
Custom Multi-threaded HTTP Server for LARP Script Archive.
Handles static file serving AND SQLite-backed REST API for player registration, character login, and GM control.
"""
import sys
import os
import json
import sqlite3
import socket
import http.server
import secrets
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from tools import npc_ai

# Database location: root of the project to keep it secure from direct web access
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kou_xia.db')

CHARACTERS = {
    'wang-si-han': '王思涵',
    'jia-san-niang': '賈三娘',
    'diao-wu-er': '刁五兒',
    'yan-yi': '嚴逸',
    'yan-shi': '嚴氏',
    'wang-shun': '王順',
    'nong-sou': '農叟',
    'jin-si-dao': '金四刀',
    'zhang-meng': '張猛'
}

def init_db():
    """Initialises the SQLite database and creates the users table if it does not exist."""
    print(f"⚙️ 正在初始化資料庫: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            character_id TEXT PRIMARY KEY,
            player_name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Add optional tracking columns if they don't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN last_seen TEXT")
    except sqlite3.OperationalError:
        pass

    # Game state table for Act 1 and Act 2 access control
    c.execute('''
        CREATE TABLE IF NOT EXISTS game_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act1_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act1_guide_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act1_characters_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act1_scripts_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act1_rumours_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act1_personal_clues_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act1_questions_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act2_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act2_questions_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act3_unlocked', '0')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act2_code', 'act2')")
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act3_code', 'act3')")

    # Player answers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_answers (
            character_id TEXT PRIMARY KEY,
            answers TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Landing page comments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    # Private messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS private_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    # Add new columns to private_messages table if they do not exist
    try:
        c.execute("ALTER TABLE private_messages ADD COLUMN sender_id TEXT")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE private_messages ADD COLUMN recipient_id TEXT")
    except Exception:
        pass

    # Backfill migration for older messages to ensure backward compatibility
    try:
        c.execute("UPDATE private_messages SET sender_id = character_id, recipient_id = 'gm' WHERE sender_id IS NULL AND sender = 'player'")
        c.execute("UPDATE private_messages SET sender_id = 'gm', recipient_id = character_id WHERE sender_id IS NULL AND sender = 'gm'")
    except Exception as e:
        print(f"⚠️ Backfill migration failed (or columns already populated): {e}")

    # Create AI Tasks table for background AI NPC job queue
    c.execute('''
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
        )
    ''')

    # Create User Sessions table for secure session authentication
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            token TEXT PRIMARY KEY,
            character_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    # Enable WAL mode and set busy timeout for thread-safe concurrent access
    try:
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA busy_timeout=5000")
    except Exception as e:
        print(f"⚠️ Failed to set PRAGMA journal_mode/busy_timeout: {e}")

    conn.commit()
    conn.close()
    print("✅ 資料庫初始化完成。")

def create_user_session(conn, character_id):
    import secrets
    import datetime
    token = secrets.token_hex(16)
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c = conn.cursor()
    c.execute("INSERT INTO user_sessions (token, character_id, created_at) VALUES (?, ?, ?)", (token, character_id, now_str))
    conn.commit()
    return token

class DualStackServer(ThreadingHTTPServer):
    def server_bind(self):
        # Allow immediate reuse of the port to avoid "Address already in use" errors
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Redirect root and main index to Kou Xia entrance page
        if self.path in ('/', '/index.html'):
            self.send_response(302)
            self.send_header('Location', '/scripts/kou-xia/index.html')
            self.end_headers()
            return

        # Handle GET API for fetching character registration statuses
        if self.path == '/api/kou-xia/characters':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute('SELECT character_id, player_name, created_at, last_login, password, last_seen FROM users')
                rows = c.fetchall()
                conn.close()
            except Exception as e:
                print(f"❌ 查詢資料庫時發生錯誤: {e}")
                rows = []
                
            claimed = {row[0]: {'playerName': row[1], 'createdAt': row[2], 'lastLogin': row[3], 'password': row[4], 'lastSeen': row[5]} for row in rows}
            
            resp = []
            for cid, name in CHARACTERS.items():
                is_claimed = cid in claimed
                last_seen_secs = -1
                if is_claimed and claimed[cid]['lastSeen']:
                    try:
                        import datetime
                        ls_dt = datetime.datetime.strptime(claimed[cid]['lastSeen'], '%Y-%m-%d %H:%M:%S')
                        now_dt = datetime.datetime.now()
                        last_seen_secs = int((now_dt - ls_dt).total_seconds())
                    except Exception:
                        pass
                resp.append({
                    'characterId': cid,
                    'characterName': name,
                    'claimed': is_claimed,
                    'playerName': (claimed[cid]['playerName'] or '') if is_claimed else '',
                    'createdAt': (claimed[cid]['createdAt'] or '') if is_claimed else '',
                    'lastLogin': (claimed[cid]['lastLogin'] or '') if is_claimed else '',
                    'password': (claimed[cid]['password'] or '') if is_claimed else '',
                    'lastSeen': (claimed[cid]['lastSeen'] or '') if is_claimed else '',
                    'lastSeenSecondsAgo': last_seen_secs
                })
            
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        # Handle GET API for game state
        if self.path == '/api/kou-xia/state':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("SELECT key, value FROM game_state")
                rows = c.fetchall()
                conn.close()
                state = {}
                for row in rows:
                    key, val = row[0], row[1]
                    if key.endswith('_code'):
                        state[key] = val
                    else:
                        state[key] = (val == '1')
            except Exception as e:
                print(f"❌ 查詢遊戲狀態時發生錯誤: {e}")
                state = {"act1_unlocked": False, "act2_unlocked": False, "act2_questions_unlocked": False}
                
            if "act1_unlocked" not in state: state["act1_unlocked"] = False
            if "act2_unlocked" not in state: state["act2_unlocked"] = False
            if "act2_questions_unlocked" not in state: state["act2_questions_unlocked"] = False
            
            self.wfile.write(json.dumps(state).encode('utf-8'))
            return

        # Handle GET API for comments
        if self.path == '/api/kou-xia/comments':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("SELECT id, nickname, content, created_at FROM comments ORDER BY id DESC")
                rows = c.fetchall()
                conn.close()
                comments = [{
                    'id': row[0],
                    'nickname': row[1],
                    'content': row[2],
                    'created_at': row[3]
                } for row in rows]
            except Exception as e:
                print(f"❌ 查詢留言板時發生錯誤: {e}")
                comments = []
                
            self.wfile.write(json.dumps(comments).encode('utf-8'))
            return

        # Handle GET API for GM fetching player answers
        if self.path.startswith('/api/kou-xia/answers'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            is_authorized = 'password=gm' in self.path
            if not is_authorized:
                self.wfile.write(json.dumps({'success': False, 'message': '權限不足'}).encode('utf-8'))
                return
            
            resp = {}
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute('SELECT character_id, answers, updated_at FROM player_answers')
                rows = c.fetchall()
                conn.close()
                for row in rows:
                    resp[row[0]] = {
                        'answers': json.loads(row[1]),
                        'updatedAt': row[2]
                    }
            except Exception as e:
                print(f"❌ 查詢玩家答題時發生錯誤: {e}")
                
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        # Handle GET API for GM fetching ALL private messages
        if self.path.startswith('/api/kou-xia/private-messages-all'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            is_authorized = 'password=gm' in self.path
            if not is_authorized:
                self.wfile.write(json.dumps({'success': False, 'message': '權限不足'}).encode('utf-8'))
                return
                
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute('SELECT id, character_id, sender, content, created_at, sender_id, recipient_id FROM private_messages ORDER BY id ASC')
                rows = c.fetchall()
                conn.close()
                messages = [{
                    'id': row[0],
                    'characterId': row[1],
                    'sender': row[2],
                    'content': row[3],
                    'created_at': row[4],
                    'sender_id': row[5] if row[5] else (row[1] if row[2] == 'player' else 'gm'),
                    'recipient_id': row[6] if row[6] else ('gm' if row[2] == 'player' else row[1])
                } for row in rows]
            except Exception as e:
                print(f"❌ 查詢所有私密留言時發生錯誤: {e}")
                messages = []
                
            self.wfile.write(json.dumps(messages).encode('utf-8'))
            return

        # Handle GET API for fetching private messages for a character
        if self.path.startswith('/api/kou-xia/private-messages'):
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            character_id = params.get('characterId', [''])[0]
            target_id = params.get('targetId', ['gm'])[0]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            if not character_id:
                self.wfile.write(json.dumps([]).encode('utf-8'))
                return
                
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                # Query messages between character_id and target_id (and vice versa)
                c.execute('''
                    SELECT id, character_id, sender, content, created_at, sender_id, recipient_id 
                    FROM private_messages 
                    WHERE (sender_id = ? AND recipient_id = ?) 
                       OR (sender_id = ? AND recipient_id = ?) 
                    ORDER BY id ASC
                ''', (character_id, target_id, target_id, character_id))
                rows = c.fetchall()
                conn.close()
                messages = [{
                    'id': row[0],
                    'characterId': row[1],
                    'sender': row[2],
                    'content': row[3],
                    'created_at': row[4],
                    'sender_id': row[5] if row[5] else (row[1] if row[2] == 'player' else 'gm'),
                    'recipient_id': row[6] if row[6] else ('gm' if row[2] == 'player' else row[1])
                } for row in rows]
            except Exception as e:
                print(f"❌ 查詢私密留言時發生錯誤: {e}")
                messages = []
                
            self.wfile.write(json.dumps(messages).encode('utf-8'))
            return

        # Otherwise, fall back to standard static file serving
        super().do_GET()

    def do_POST(self):
        # Intercept API POST routes
        if self.path in ('/api/kou-xia/register', '/api/kou-xia/login', '/api/kou-xia/reset', '/api/kou-xia/state', '/api/kou-xia/submit-answers', '/api/kou-xia/delete-user', '/api/kou-xia/delete-answers', '/api/kou-xia/comments', '/api/kou-xia/change-password', '/api/kou-xia/send-private-message', '/api/kou-xia/heartbeat'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': '無效的 JSON 格式'}).encode('utf-8'))
                return

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            res = {'success': False, 'message': '未知的 API 請求'}

            try:
                if self.path == '/api/kou-xia/register':
                    cid = data.get('characterId', '').strip().lower()
                    player_name = data.get('playerName', '').strip()
                    password = data.get('password', '')

                    if cid not in CHARACTERS:
                        res = {'success': False, 'message': '無效的角色識別碼'}
                    elif not player_name or not password:
                        res = {'success': False, 'message': '玩家姓名與密碼不能為空'}
                    else:
                        try:
                            c.execute("INSERT INTO users (character_id, player_name, password, created_at, last_login) VALUES (?, ?, ?, strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'), strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))", (cid, player_name, password))
                            conn.commit()
                            token = create_user_session(conn, cid)
                            res = {
                                'success': True,
                                'session': {
                                    'characterId': cid,
                                    'characterName': CHARACTERS[cid],
                                    'playerName': player_name,
                                    'token': token
                                }
                            }
                            print(f"🆕 玩家註冊成功: {CHARACTERS[cid]} ({player_name})")
                        except sqlite3.IntegrityError:
                            res = {'success': False, 'message': '該角色已被其他玩家註冊！'}

                elif self.path == '/api/kou-xia/login':
                    username = data.get('username', '').strip().lower()
                    password = data.get('password', '')

                    if username == 'gm' and password == 'gm':
                        token = create_user_session(conn, 'gm')
                        res = {
                            'success': True,
                            'is_gm': True,
                            'session': {
                                'characterId': 'gm',
                                'characterName': 'GM',
                                'playerName': 'GM',
                                'token': token
                            }
                        }
                        print("🎲 GM 登入成功")
                    elif username in CHARACTERS:
                        c.execute('SELECT player_name, password FROM users WHERE character_id = ?', (username,))
                        row = c.fetchone()
                        if row and row[1] == password:
                            # Update last login time
                            c.execute("UPDATE users SET last_login = (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')) WHERE character_id = ?", (username,))
                            conn.commit()
                            token = create_user_session(conn, username)
                            res = {
                                'success': True,
                                'session': {
                                    'characterId': username,
                                    'characterName': CHARACTERS[username],
                                    'playerName': row[0],
                                    'token': token
                                }
                            }
                            print(f"🔑 玩家登入成功: {CHARACTERS[username]} ({row[0]})")
                        else:
                            res = {'success': False, 'message': '角色密碼錯誤，請再試一次'}
                    else:
                        res = {'success': False, 'message': '此角色尚未註冊，請先進行註冊'}

                elif self.path == '/api/kou-xia/reset':
                    password = data.get('password', '')
                    if password == 'gm':
                        c.execute('DELETE FROM users')
                        conn.commit()
                        res = {'success': True}
                        print("🧹 GM 已重設所有玩家註冊資料")
                    else:
                        res = {'success': False, 'message': '重設失敗：GM 密碼錯誤'}

                elif self.path == '/api/kou-xia/delete-user':
                    password = data.get('password', '')
                    character_id = data.get('characterId', '')
                    if password == 'gm':
                        if character_id:
                            c.execute('DELETE FROM users WHERE character_id = ?', (character_id,))
                            c.execute('DELETE FROM player_answers WHERE character_id = ?', (character_id,))
                            conn.commit()
                            res = {'success': True, 'message': f'已成功刪除角色 {character_id} 的註冊與答題資料！'}
                            print(f"🧹 GM 刪下了註冊角色: {character_id}")
                        else:
                            res = {'success': False, 'message': '刪除失敗：未提供角色 ID'}
                    else:
                        res = {'success': False, 'message': '刪除失敗：GM 密碼錯誤'}

                elif self.path == '/api/kou-xia/delete-answers':
                    password = data.get('password', '')
                    character_id = data.get('characterId', '')
                    if password == 'gm':
                        if character_id:
                            c.execute('DELETE FROM player_answers WHERE character_id = ?', (character_id,))
                            conn.commit()
                            res = {'success': True, 'message': f'已成功刪除角色 {character_id} 的答題資料！'}
                            print(f"🧹 GM 刪除了答題資料: {character_id}")
                        else:
                            res = {'success': False, 'message': '刪除失敗：未提供角色 ID'}
                    else:
                        res = {'success': False, 'message': '刪除失敗：GM 密碼錯誤'}

                elif self.path == '/api/kou-xia/state':
                    password = data.get('password', '')
                    if password == 'gm':
                        res = {'success': True}
                        for key, val in data.items():
                            if key == 'password':
                                continue
                            if key.endswith('_code'):
                                db_val = str(val)
                                res[key] = val
                            else:
                                db_val = '1' if val else '0'
                                res[key] = (db_val == '1')
                            c.execute("INSERT OR REPLACE INTO game_state (key, value) VALUES (?, ?)", (key, db_val))
                        conn.commit()
                        print(f"⚙️ GM 更新遊戲狀態: {res}")
                    else:
                        res = {'success': False, 'message': '權限不足：GM 密碼錯誤'}

                elif self.path == '/api/kou-xia/submit-answers':
                    character_id = data.get('characterId', '')
                    answers = data.get('answers', {})
                    
                    if not character_id or character_id not in CHARACTERS:
                        res = {'success': False, 'message': '無效的角色 ID'}
                    else:
                        import datetime
                        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        answers_json = json.dumps(answers, ensure_ascii=False)
                        
                        c.execute("INSERT OR REPLACE INTO player_answers (character_id, answers, updated_at) VALUES (?, ?, ?)", 
                                  (character_id, answers_json, now_str))
                        conn.commit()
                        res = {'success': True, 'message': '答案已成功提交並儲存！'}
                        print(f"📝 玩家答題已儲存: {character_id} 於 {now_str}")

                elif self.path == '/api/kou-xia/comments':
                    nickname = data.get('nickname', '').strip()
                    content = data.get('content', '').strip()
                    
                    if not nickname or not content:
                        res = {'success': False, 'message': '暱稱與留言內容不得為空！'}
                    else:
                        import datetime
                        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        c.execute("INSERT INTO comments (nickname, content, created_at) VALUES (?, ?, ?)", 
                                  (nickname, content, now_str))
                        conn.commit()
                        res = {'success': True, 'message': '留言發表成功！'}
                        print(f"💬 新增玩家留言: {nickname} 於 {now_str}")

                elif self.path == '/api/kou-xia/change-password':
                    password = data.get('password', '')
                    character_id = data.get('characterId', '')
                    new_password = data.get('newPassword', '')
                    if password == 'gm':
                        if character_id and new_password:
                            c.execute('UPDATE users SET password = ? WHERE character_id = ?', (new_password, character_id))
                            conn.commit()
                            res = {'success': True, 'message': f'已成功修改角色 {character_id} 的密碼！'}
                            print(f"🔑 GM 修改了角色密碼: {character_id}")
                        else:
                            res = {'success': False, 'message': '修改失敗：未提供角色 ID 或新密碼'}
                    else:
                        res = {'success': False, 'message': '修改失敗：GM 密碼錯誤'}

                elif self.path == '/api/kou-xia/send-private-message':
                    token = self.headers.get('X-Session-Token')
                    content = data.get('content', '').strip()
                    target_id = data.get('targetId', 'gm')
                    
                    if not content:
                        res = {'success': False, 'message': '訊息內容不能為空'}
                    elif not token:
                        res = {'success': False, 'message': '未提供認證 Token，請重新登入'}
                    else:
                        # Securely resolve sender_id from token
                        c.execute("SELECT character_id FROM user_sessions WHERE token = ?", (token,))
                        session_row = c.fetchone()
                        
                        if not session_row:
                            res = {'success': False, 'message': '認證無效或登入已過期，請重新登入'}
                        else:
                            sender_id = session_row[0]
                            recipient_id = target_id
                            
                            # Validate recipient
                            if recipient_id not in CHARACTERS and recipient_id != 'gm':
                                res = {'success': False, 'message': '無效的收件者識別碼'}
                            else:
                                sender = 'gm' if sender_id == 'gm' else 'player'
                                character_id = recipient_id if sender_id == 'gm' else sender_id
                                
                                import datetime
                                now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                
                                try:
                                    conn.execute("BEGIN TRANSACTION;")
                                    # 1. Insert message
                                    c.execute("INSERT INTO private_messages (character_id, sender, content, created_at, sender_id, recipient_id) VALUES (?, ?, ?, ?, ?, ?)", 
                                              (character_id, sender, content, now_str, sender_id, recipient_id))
                                    message_id = c.lastrowid
                                    
                                    # 2. If sending to zhang-meng and sender is not zhang-meng itself, enqueue AI task
                                    if recipient_id == 'zhang-meng' and sender_id != 'zhang-meng':
                                        c.execute("INSERT INTO ai_tasks (message_id, status, created_at) VALUES (?, 'pending', ?)", 
                                                  (message_id, now_str))
                                        
                                    conn.commit()
                                    res = {'success': True, 'message': '私密留言傳送成功！'}
                                    print(f"✉️ [Secure] 私密留言: [{sender_id} -> {recipient_id}] {content[:30]} 於 {now_str}")
                                except Exception as tx_err:
                                    conn.rollback()
                                    raise tx_err

                elif self.path == '/api/kou-xia/heartbeat':
                    character_id = data.get('characterId', '')
                    if character_id:
                        import datetime
                        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        c.execute("UPDATE users SET last_seen = ?, last_login = ? WHERE character_id = ?", (now_str, now_str, character_id))
                        conn.commit()
                        res = {'success': True, 'last_seen': now_str}
                    else:
                        res = {'success': False, 'message': 'Missing characterId'}

                self.wfile.write(json.dumps(res).encode('utf-8'))
            except Exception as e:
                print(f"❌ 處理 POST API 發生異常: {e}")
                self.wfile.write(json.dumps({'success': False, 'message': f'伺服器錯誤: {str(e)}'}).encode('utf-8'))
            finally:
                conn.close()
            return

        # Fall back to standard 404 for other POST endpoints
        self.send_response(404)
        self.end_headers()

def main():
    # 讀取環境變數，若無則套用預設值 (Port: 8000, Dir: docs)
    env_port = int(os.environ.get('PORT', 8000))
    env_dir = os.environ.get('WEB_DIR', 'docs')

    # 第一優先：如果指令最後有帶 CLI 參數，則覆蓋環境變數與預設值
    port = int(sys.argv[1]) if len(sys.argv) > 1 else env_port
    directory = sys.argv[2] if len(sys.argv) > 2 else env_dir

    # Switch working directory so SimpleHTTPRequestHandler serves files correctly
    os.chdir(directory)

    # Setup DB
    init_db()

    # Start background AI worker thread
    try:
        npc_ai.start_worker()
    except Exception as e:
        print(f"⚠️ Failed to start NPC AI background worker: {e}", file=sys.stderr)

    try:
        server = DualStackServer(('0.0.0.0', port), CustomHandler)
        print(f"🚀 伺服器正在 0.0.0.0:{port} 運行，託管目錄為 {directory}")

        # Print helpful testing URLs
        host_ip = os.environ.get('HOST_IP')
        print("\n========================================================")
        print("💻 [本機電腦測試網址]")
        print(f"   - 玩家入口: http://localhost:{port}/scripts/kou-xia/player/index.html")
        print(f"   - 角色登入: http://localhost:{port}/scripts/kou-xia/player/login.html")
        print(f"   - 主持人端: http://localhost:{port}/scripts/kou-xia/gm/index.html")
        
        print("\n🌐 [區域網路 / 手機連線測試]")
        if host_ip:
            print(f"   偵測到主機 IP 參數為: {host_ip}")
            print(f"   - 玩家登入: http://{host_ip}:{port}/scripts/kou-xia/player/login.html")
            print(f"   - 主持人端: http://{host_ip}:{port}/scripts/kou-xia/gm/index.html")
        else:
            print(f"   1. 請在 Windows PowerShell 執行 'ipconfig' 查詢您的 Wi-Fi IPv4 (例如 10.0.0.78)")
            print(f"   2. 確保手機與此電腦連接到同一個 Wi-Fi 路由器")
            print(f"   3. 在手機瀏覽器輸入：")
            print(f"      - 玩家登入: http://<您的電腦IP>:{port}/scripts/kou-xia/player/login.html")
            print(f"      - 主持人端: http://<您的電腦IP>:{port}/scripts/kou-xia/gm/index.html")
            print("\n   💡 提示: 啟動 Docker 時加上 -e HOST_IP=您的IP，即可直接印出可點選的完整連線網址！")
            print(f"      範例: docker run -it --rm -e HOST_IP=10.0.0.78 -p 0.0.0.0:{port}:{port} -v \"${{PWD}}:/workspace\" larp-script-archive {port} {directory}")
        print("========================================================\n")

        server.serve_forever()
    except OSError as e:
        if e.errno == 98 or 'already in use' in str(e).lower():
            print(f'\n❌ 錯誤：Port {port} 已被佔用！', file=sys.stderr)
            print('請嘗試使用其他 Port，例如：./serve.sh 8080', file=sys.stderr)
        else:
            print(f'\n❌ 啟動伺服器時發生錯誤：{e}', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\n\n🛑 正在停止本地伺服器...')
        sys.exit(0)

if __name__ == '__main__':
    main()
