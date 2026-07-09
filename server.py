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
    # Add optional tracking columns if they don't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
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
    c.execute("INSERT OR IGNORE INTO game_state (key, value) VALUES ('act2_unlocked', '0')")

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
                c.execute('SELECT character_id, player_name, created_at, last_login FROM users')
                rows = c.fetchall()
                conn.close()
            except Exception as e:
                print(f"❌ 查詢資料庫時發生錯誤: {e}")
                rows = []
                
            claimed = {row[0]: {'playerName': row[1], 'createdAt': row[2], 'lastLogin': row[3]} for row in rows}
            
            resp = []
            for cid, name in CHARACTERS.items():
                is_claimed = cid in claimed
                resp.append({
                    'characterId': cid,
                    'characterName': name,
                    'claimed': is_claimed,
                    'playerName': (claimed[cid]['playerName'] or '') if is_claimed else '',
                    'createdAt': (claimed[cid]['createdAt'] or '') if is_claimed else '',
                    'lastLogin': (claimed[cid]['lastLogin'] or '') if is_claimed else ''
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
                state = {row[0]: row[1] == '1' for row in rows}
            except Exception as e:
                print(f"❌ 查詢遊戲狀態時發生錯誤: {e}")
                state = {"act1_unlocked": False, "act2_unlocked": False}
                
            if "act1_unlocked" not in state: state["act1_unlocked"] = False
            if "act2_unlocked" not in state: state["act2_unlocked"] = False
            
            self.wfile.write(json.dumps(state).encode('utf-8'))
            return

        # Otherwise, fall back to standard static file serving
        super().do_GET()

    def do_POST(self):
        # Intercept API POST routes
        if self.path in ('/api/kou-xia/register', '/api/kou-xia/login', '/api/kou-xia/reset', '/api/kou-xia/state'):
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
                            c.execute("INSERT INTO users (character_id, player_name, password, created_at) VALUES (?, ?, ?, strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))", (cid, player_name, password))
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
                            # Update last login time
                            c.execute("UPDATE users SET last_login = (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')) WHERE character_id = ?", (username,))
                            conn.commit()
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

                elif self.path == '/api/kou-xia/state':
                    password = data.get('password', '')
                    if password == 'gm':
                        res = {'success': True}
                        for key, val in data.items():
                            if key == 'password':
                                continue
                            db_val = '1' if val else '0'
                            c.execute("INSERT OR REPLACE INTO game_state (key, value) VALUES (?, ?)", (key, db_val))
                            res[key] = (db_val == '1')
                        conn.commit()
                        print(f"⚙️ GM 更新遊戲狀態: {res}")
                    else:
                        res = {'success': False, 'message': '權限不足：GM 密碼錯誤'}

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
