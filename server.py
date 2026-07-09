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
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

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
    conn.commit()
    conn.close()
    print("✅ 資料庫初始化完成。")

class DualStackServer(ThreadingHTTPServer):
    def server_bind(self):
        # Allow immediate reuse of the port to avoid "Address already in use" errors
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle GET API for fetching character registration statuses
        if self.path == '/api/kou-xia/characters':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute('SELECT character_id, player_name FROM users')
                rows = c.fetchall()
                conn.close()
            except Exception as e:
                print(f"❌ 查詢資料庫時發生錯誤: {e}")
                rows = []
                
            claimed = {row[0]: row[1] for row in rows}
            
            resp = []
            for cid, name in CHARACTERS.items():
                is_claimed = cid in claimed
                resp.append({
                    'characterId': cid,
                    'characterName': name,
                    'claimed': is_claimed,
                    'playerName': claimed[cid] if is_claimed else ''
                })
            
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        # Otherwise, fall back to standard static file serving
        super().do_GET()

    def do_POST(self):
        # Intercept API POST routes
        if self.path in ('/api/kou-xia/register', '/api/kou-xia/login', '/api/kou-xia/reset'):
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
                            c.execute('INSERT INTO users (character_id, player_name, password) VALUES (?, ?, ?)', (cid, player_name, password))
                            conn.commit()
                            res = {
                                'success': True,
                                'session': {
                                    'characterId': cid,
                                    'characterName': CHARACTERS[cid],
                                    'playerName': player_name
                                }
                            }
                            print(f"🆕 玩家註冊成功: {CHARACTERS[cid]} ({player_name})")
                        except sqlite3.IntegrityError:
                            res = {'success': False, 'message': '該角色已被其他玩家註冊！'}

                elif self.path == '/api/kou-xia/login':
                    username = data.get('username', '').strip().lower()
                    password = data.get('password', '')

                    if username == 'gm' and password == 'gm':
                        res = {
                            'success': True,
                            'is_gm': True,
                            'session': {
                                'characterId': 'gm',
                                'characterName': 'GM',
                                'playerName': 'GM'
                            }
                        }
                        print("🎲 GM 登入成功")
                    elif username in CHARACTERS:
                        c.execute('SELECT player_name, password FROM users WHERE character_id = ?', (username,))
                        row = c.fetchone()
                        if row and row[1] == password:
                            res = {
                                'success': True,
                                'session': {
                                    'characterId': username,
                                    'characterName': CHARACTERS[username],
                                    'playerName': row[0]
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
    if len(sys.argv) < 3:
        print("用法: server.py <port> <directory>")
        sys.exit(1)

    port = int(sys.argv[1])
    directory = sys.argv[2]

    # Switch working directory so SimpleHTTPRequestHandler serves files correctly
    os.chdir(directory)

    # Setup DB
    init_db()

    try:
        server = DualStackServer(('0.0.0.0', port), CustomHandler)
        print(f"🚀 伺服器正在 0.0.0.0:{port} 運行，託管目錄為 {directory}")
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
