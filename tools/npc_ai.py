import os
import sys
import sqlite3
import time
import uuid
import datetime
import threading
from tools import gemini_client

# Environment configuration
NPC_AI_ENABLED = os.environ.get("NPC_AI_ENABLED", "true").lower() == "true"
NPC_AI_POLL_INTERVAL_SECONDS = float(os.environ.get("NPC_AI_POLL_INTERVAL_SECONDS", "1"))
NPC_AI_STALE_TASK_SECONDS = float(os.environ.get("NPC_AI_STALE_TASK_SECONDS", "60"))
NPC_AI_HISTORY_LIMIT = int(os.environ.get("NPC_AI_HISTORY_LIMIT", "10"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(PROJECT_ROOT, "kou_xia.db")
MATERIALS_DIR = os.path.join(PROJECT_ROOT, "materials")

# Unique identifier for this worker instance (useful in locked_at multi-worker scenario)
WORKER_ID = f"worker-{uuid.uuid4()}"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    # Enable WAL mode and busy timeout for safe concurrent writing across threads
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

def get_game_state(conn):
    c = conn.cursor()
    c.execute("SELECT key, value FROM game_state")
    rows = c.fetchall()
    state = {}
    for row in rows:
        key, val = row[0], row[1]
        state[key] = (val == '1')
    return state

def build_system_instruction(state):
    npc_dir = os.path.join(MATERIALS_DIR, "kou-xia", "npcs", "zhang-meng")
    
    # White-list knowledge files
    files_to_load = ["system_rules.md", "identity.md"]
    
    # Condition-based knowledge loading depending on GM's current Act status
    # Act 1 knowledge is loaded as baseline
    files_to_load.append("act1_knowledge.md")
    
    if state.get("act2_unlocked", False):
        files_to_load.append("act2_knowledge.md")
        
    if state.get("act3_unlocked", False):
        files_to_load.append("act3_knowledge.md")
        
    parts = []
    for filename in files_to_load:
        path = os.path.join(npc_dir, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f.read())
        else:
            print(f"⚠️ Warning: Knowledge file not found: {path}", file=sys.stderr)
            
    return "\n\n".join(parts)

def clean_ai_response(text):
    """
    Cleans response text to strip HTML tags, preventing XSS and injection.
    Limits length to 200 characters.
    """
    if not text:
        return ""
    import re
    # Simple HTML tag removal
    clean = re.sub(r'<[^>]*>', '', text)
    # Limit length
    clean = clean[:200]
    return clean.strip()

def process_single_task(conn, message_id):
    """
    Executes a single enqueued AI reply task.
    """
    c = conn.cursor()
    
    # 1. Fetch details of the incoming message we need to respond to
    c.execute("SELECT sender_id, recipient_id, content, character_id FROM private_messages WHERE id = ?", (message_id,))
    msg_row = c.fetchone()
    if not msg_row:
        # Invalid message ID
        c.execute("UPDATE ai_tasks SET status = 'failed', error = 'Message not found' WHERE message_id = ?", (message_id,))
        conn.commit()
        return
        
    player_id, zhang_meng_id, user_message, character_id = msg_row
    
    # 2. Fetch game state and assemble system instructions
    state = get_game_state(conn)
    system_instruction = build_system_instruction(state)
    
    # 3. Retrieve historical dialog context (excluding the prompt itself)
    c.execute("""
        SELECT sender_id, content 
        FROM private_messages 
        WHERE ((sender_id = ? AND recipient_id = ?) 
           OR (sender_id = ? AND recipient_id = ?))
           AND id < ?
        ORDER BY id DESC 
        LIMIT ?
    """, (player_id, zhang_meng_id, zhang_meng_id, player_id, message_id, NPC_AI_HISTORY_LIMIT))
    history_rows = c.fetchall()
    history_rows.reverse() # Sort chronologically
    chat_history = [{"sender_id": r[0], "content": r[1]} for r in history_rows]
    
    # 4. Invoke Gemini API client
    try:
        raw_reply = gemini_client.generate_npc_reply(system_instruction, chat_history, user_message)
        reply_content = clean_ai_response(raw_reply)
        
        if not reply_content:
            raise ValueError("Sanitized AI response is empty.")
            
        # 5. Write reply and complete task inside an Atomic Transaction
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            conn.execute("BEGIN TRANSACTION;")
            
            # Write reply back to private_messages (always grouped under user's character_id)
            c.execute("""
                INSERT INTO private_messages (character_id, sender, content, created_at, sender_id, recipient_id) 
                VALUES (?, 'player', ?, ?, 'zhang-meng', ?)
            """, (character_id, reply_content, now_str, player_id))
            
            reply_message_id = c.lastrowid
            
            # Update task status to completed
            c.execute("""
                UPDATE ai_tasks 
                SET status = 'completed', reply_message_id = ?, processed_at = ? 
                WHERE message_id = ?
            """, (reply_message_id, now_str, message_id))
            
            conn.commit()
            print(f"✅ AI Replied successfully to message {message_id}: {reply_content[:30]}...")
        except Exception as tx_err:
            conn.rollback()
            raise tx_err
            
    except Exception as api_err:
        print(f"⚠️ Worker error processing task {message_id}: {api_err}", file=sys.stderr)
        # Fetch current attempt count
        c.execute("SELECT attempts FROM ai_tasks WHERE message_id = ?", (message_id,))
        attempt_row = c.fetchone()
        attempts = attempt_row[0] if attempt_row else 0
        
        if attempts >= 3:
            # Mark failed and insert fallback message in a single transaction
            fallback_text = "「（張猛在大堂裡忙著張羅客人，一邊高聲吆喝，似乎沒顧上你的私訊。）」"
            now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                conn.execute("BEGIN TRANSACTION;")
                
                c.execute("""
                    INSERT INTO private_messages (character_id, sender, content, created_at, sender_id, recipient_id) 
                    VALUES (?, 'player', ?, ?, 'zhang-meng', ?)
                """, (character_id, fallback_text, now_str, player_id))
                
                fallback_msg_id = c.lastrowid
                
                c.execute("""
                    UPDATE ai_tasks 
                    SET status = 'failed', reply_message_id = ?, error = ?, processed_at = ? 
                    WHERE message_id = ?
                """, (fallback_msg_id, str(api_err), now_str, message_id))
                
                conn.commit()
                print(f"🛑 Max attempts reached for message {message_id}. Written fallback reply.")
            except Exception as tx_err:
                conn.rollback()
                print(f"❌ Failed to commit fallback transaction: {tx_err}", file=sys.stderr)
        else:
            # Set back to pending so it can be retried
            c.execute("UPDATE ai_tasks SET status = 'pending', error = ? WHERE message_id = ?", (str(api_err), message_id))
            conn.commit()

def worker_loop():
    """
    Continuous background loop for enqueued tasks.
    """
    print(f"🤖 Starting background AI Worker ({WORKER_ID}) polling on {DB_FILE}...")
    
    while True:
        conn = None
        try:
            conn = get_db_connection()
            c = conn.cursor()
            
            now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Determine stale threshold
            stale_threshold_dt = datetime.datetime.now() - datetime.timedelta(seconds=NPC_AI_STALE_TASK_SECONDS)
            stale_threshold = stale_threshold_dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Query eligible tasks
            c.execute("""
                SELECT message_id 
                FROM ai_tasks 
                WHERE status = 'pending' 
                   OR (status = 'processing' AND locked_at < ?)
                ORDER BY id ASC
            """, (stale_threshold,))
            
            tasks = c.fetchall()
            
            for row in tasks:
                message_id = row[0]
                
                # Atomic claim update
                c.execute("""
                    UPDATE ai_tasks 
                    SET status = 'processing', locked_at = ?, worker_id = ?, attempts = attempts + 1 
                    WHERE message_id = ? AND (status = 'pending' OR (status = 'processing' AND locked_at < ?))
                """, (now_str, WORKER_ID, message_id, stale_threshold))
                conn.commit()
                
                # If we locked the row, process it
                if c.rowcount == 1:
                    print(f"⚡ Worker claimed task for message_id: {message_id}")
                    process_single_task(conn, message_id)
                    break # Break to fetch fresh tasks list on next loop
                    
        except Exception as loop_err:
            print(f"❌ Worker loop encounter unexpected error: {loop_err}", file=sys.stderr)
        finally:
            if conn:
                conn.close()
                
        time.sleep(NPC_AI_POLL_INTERVAL_SECONDS)

def start_worker():
    if not NPC_AI_ENABLED:
        print("ℹ️ NPC AI background worker is disabled via environment configuration.")
        return
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY is not defined. NPC AI background worker will not be started.")
        return
        
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
