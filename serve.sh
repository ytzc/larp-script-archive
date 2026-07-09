#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# serve.sh — 本地端網路部署與測試腳本 (Local Hosting Script)
#
# 用途:
#   在本地端啟動一個 HTTP 伺服器，將 `./docs` 資料夾建立在本地端區域網路 (LAN) 上，
#   並自動偵測並顯示本機 IP，以便外部裝置（如同一 Wi-Fi 下的手機、平板、其他電腦）直接連線存取。
#
# 使用方式:
#   ./serve.sh         (預設使用 port 8000)
#   ./serve.sh 8080    (指定使用 port 8080)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# 取得此腳本所在的根目錄，確保無論在何處執行都能正確定位 docs 目錄
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DOCS_DIR="$SCRIPT_DIR/docs"
PORT="${1:-8000}"

# 檢查 docs 資料夾是否存在
if [[ ! -d "$DOCS_DIR" ]]; then
  echo "錯誤: 找不到 '$DOCS_DIR' 資料夾。" >&2
  exit 1
fi

# 使用 Python 內建 socket 庫，精確且跨平台地取得本機在區域網路 (LAN) 中的主要 IP 位址
get_local_ip() {
  python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    # 不需要真正連通該外部 IP，僅用於讓系統路由選擇正確的網路介面並回傳本機 IP
    s.connect(('10.255.255.255', 1))
    print(s.getsockname()[0])
except Exception:
    print('127.0.0.1')
finally:
    s.close()
"
}

LOCAL_IP=$(get_local_ip)

echo "=========================================================="
echo "    LARP 劇本存檔庫 — 本地端區域網路伺服器 (Local Server) "
echo "=========================================================="
echo " 📂 託管資料夾 : $DOCS_DIR"
echo " 🔌 本地端存取 : http://localhost:$PORT/"
if [[ "$LOCAL_IP" != "127.0.0.1" ]]; then
  echo " 📱 區域網路IP : http://$LOCAL_IP:$PORT/"
  echo "                 (請確保您的手機/平板與此電腦連接同一個 Wi-Fi 網路)"
else
  echo " ⚠️ 提示        : 未偵測到有效的區域網路 IP，僅限本機 localhost 連線。"
fi
echo "=========================================================="
echo " 💡 提示：按 Ctrl+C 可以安全停止伺服器。"
echo "=========================================================="
echo ""

# 啟動自訂的 Python 伺服器 (包含 SQLite API 支援)
python3 "$SCRIPT_DIR/server.py" "$PORT" "$DOCS_DIR"
