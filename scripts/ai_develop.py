"""AI Company OS — Codex 開發腳本 v2.0
支援：靜態網站、FastAPI 後端、AI QA 測試生成
"""
import os, re, json, shutil
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
issue_body   = os.environ.get("ISSUE_BODY", "")
issue_title  = os.environ.get("ISSUE_TITLE", "")
issue_number = os.environ.get("ISSUE_NUMBER", "0")
category     = os.environ.get("CATEGORY", "新功能開發")
project_id   = os.environ.get("PROJECT_ID", "")
customer_id  = os.environ.get("CUSTOMER_ID", "")

# 修正亂碼
for var_name in ["category", "issue_title", "issue_body"]:
    val = locals()[var_name]
    try: val = val.encode('latin-1').decode('utf-8')
    except: pass
    exec(f"{var_name} = val")

# 判斷專案類型
needs_backend = any(k in (category + issue_title + issue_body).lower()
    for k in ["api", "backend", "fastapi", "database", "auth", "登入", "資料庫", "後端", "server"])
needs_frontend = any(k in (category + issue_title + issue_body).lower()
    for k in ["frontend", "ui", "網頁", "介面", "前端", "html", "react"])
is_static = not needs_backend or needs_frontend

print(f"專案類型：{'靜態' if is_static else '全端'} | Backend={needs_backend} | Frontend={needs_frontend}")
print(f"專案ID：{project_id} | 客戶ID：{customer_id}")

# 提取 Codex Prompt
prompt = ""
in_prompt = False
for line in issue_body.split("\n"):
    if line.strip() == "## Codex Prompt":
        in_prompt = True
        continue
    if in_prompt and line.startswith("## "):
        break
    if in_prompt:
        prompt += line + "\n"

prompt = prompt.strip().strip("`")
if not prompt:
    prompt = f"根據以下需求實作：{issue_title}\n\n{issue_body[:1000]}"

print(f"需求：{issue_title[:60]}")
print(f"Prompt 長度：{len(prompt)} 字元")

# ─── 讀取 API 金鑰（從 PM Center）─────────────────────────────
import urllib.request, json as _json, base64 as _b64
PM_CENTER = "https://ai-pm-center-827577239332.asia-east1.run.app"
stored_keys = {}
try:
    req = urllib.request.Request(f"{PM_CENTER}/projects/{project_id}/keys")
    resp = urllib.request.urlopen(req, timeout=5)
    stored_keys = _json.loads(resp.read()).get("keys", {})
    if stored_keys:
        print(f"已載入 API 金鑰: {list(stored_keys.keys())}")
except Exception as e:
    print(f"無 API 金鑰或載入失敗: {e}")

# 建立 API 金鑰的 STRICT_RULE 補充
API_KEY_RULES = ""
if stored_keys:
    key_lines = "\n".join([f"  - {k}: 使用環境變數 os.environ.get('{k}', '')" for k in stored_keys.keys()])
    API_KEY_RULES = f"""
【API 金鑰使用規則】
以下 API 金鑰已由消費者提供，必須在程式中正確使用：
{key_lines}

在 FastAPI 中用 os.environ.get('KEY_NAME') 讀取。
在靜態 HTML 中用 localStorage 或 .env.local 方式。
絕對不要在前端 JS 中硬編碼 SECRET 金鑰。
"""

# ─── 系統提示詞 ─────────────────────────────────────────
STRICT_RULE = f"""
【最重要規則】
你必須嚴格按照用戶的「原始需求」開發，不得自行更改功能或主題。
原始需求：{prompt[:300]}

如果需求是「薪資記帳本」就做薪資記帳本，不能做會員系統。
如果需求是「預約系統」就做預約系統，不能做其他東西。
功能必須與需求完全對應，不得替換或簡化核心功能。
{API_KEY_RULES}
"""

if needs_backend and not is_static:
    system_prompt = f"""你是世界頂尖的全端工程師（AI Company OS Codex）。
{STRICT_RULE}

你的目標：生成一個「生產環境就緒」的真實產品，不是 Demo。

【後端品質標準】
- 完整的 CRUD API（Create/Read/Update/Delete 都要實作）
- 資料驗證（Pydantic models 完整定義）
- 適當的 HTTP 狀態碼（200/201/400/404/500）
- 錯誤處理（try/except + 有意義的錯誤訊息）
- 搜尋和篩選端點
- 分頁支援（limit/offset）
- 資料匯出端點（CSV 格式）
- API 文件（使用 FastAPI 自動 Swagger）

【前端品質標準】
- 完整呼叫所有 API 端點
- Loading 狀態顯示
- 錯誤訊息顯示
- 成功操作後的 Toast 通知
- 確認刪除的對話框
- 搜尋和篩選 UI
- 分頁元件

根據需求生成完整可執行的 FastAPI 後端 + 前端。
輸出格式：每個文件用 '=== 文件名 ===' 分隔。

必須輸出以下文件：
1. === main.py === (FastAPI 主程式，包含所有 API 路由)
2. === requirements.txt === (Python 依賴)
3. === Dockerfile === (生產用 Dockerfile)
4. === index.html === (前端頁面，呼叫後端 API)
5. === tests/test_api.py === (pytest 自動測試)

Dockerfile 範本：
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

FastAPI 注意事項：
- 加入 CORS 設定（允許所有 origin）
- 加入 /health 端點回傳 {{"status":"ok"}}
- 資料暫存用 dict（無 DB 時）

只輸出代碼，不要解釋。"""
else:
    # 從需求中提取 UI 風格偏好
    ui_style = "科技深色"  # 預設
    style_configs = {
        "極簡": {"bg":"#ffffff","card":"#f8f9fa","accent":"#1a1a2e","text":"#1a1a2e","border":"#e2e8f0","mode":"light"},
        "企業": {"bg":"#f0f4f8","card":"#ffffff","accent":"#2563eb","text":"#1e293b","border":"#cbd5e1","mode":"light"},
        "科技": {"bg":"#07070f","card":"#0f1020","accent":"#7c6cff","text":"#ffffff","border":"#1a1d35","mode":"dark"},
        "活潑": {"bg":"#fefce8","card":"#ffffff","accent":"#f59e0b","text":"#1f2937","border":"#fde68a","mode":"light"},
        "高端": {"bg":"#0a0a0a","card":"#141414","accent":"#d4af37","text":"#f5f5f5","border":"#2a2a2a","mode":"dark"},
    }
    for style_key in style_configs:
        if style_key in prompt:
            ui_style = style_key
            break
    sc = style_configs.get(ui_style, style_configs["科技"])

    # Load template
    template_path = os.path.join(os.path.dirname(__file__), 'template_static.html')
    template = open(template_path, encoding='utf-8').read() if os.path.exists(template_path) else ''

    system_prompt = f"""你是世界頂尖的全端工程師（AI Company OS Codex）。
{STRICT_RULE}

你的工作：使用下方提供的「完整運作模板」，填入業務邏輯，生成真正可用的產品。

【模板填入規則】
模板已有完整的：新增/編輯/刪除/搜尋/篩選/統計/匯出CSV/Toast通知/確認對話框。
你的工作是「填入」以下部分，不是重寫：
1. {{APP_TITLE}} → 產品名稱
2. {{APP_DESC}} → 一句描述
3. {{BG_COLOR}}、{{CARD_COLOR}}、{{ACCENT1}}、{{ACCENT2}}、{{TEXT_COLOR}}、{{BORDER_COLOR}} → 根據 {ui_style} 填入顏色
4. {{ITEM_NAME}} → 單筆資料名稱（如「股票」「客戶」「記帳」）
5. {{STORAGE_KEY}} → localStorage key（英文）
6. {{FIELDS_CONFIG}} → JSON array，每個欄位包含 name/label/type/required/options
7. {{SAMPLE_DATA}} → JSON array，5筆真實感的示範資料
8. {{STATS_CONFIG}} → JSON array，3-4個統計指標定義
9. {{STAT_CARDS}} → HTML，統計卡片
10. {{TABLE_HEADERS}} → HTML，表格標題列
11. {{FORM_FIELDS}} → HTML，表單欄位（使用 id="f_欄位名"）
12. {{FILTER_SELECTS}} → HTML，篩選下拉選單
13. {{renderRow}} function → JavaScript，渲染每一行的 HTML
14. {{updateStats}} function → JavaScript，計算並更新統計數字
15. {{BUSINESS_LOGIC}} → 其他業務邏輯函數

輸出完整的 index.html（替換模板中所有 placeholder）。

【基礎模板】（必須使用，不要重寫）：
{template[:8000]}

輸出格式：每個文件用 '=== 文件名 ===' 分隔。

你的終極目標：生成一個「真正可以每天使用」的產品，不是 Demo。

【產品品質標準 — 必須全部達到】

★★★ 最嚴格禁令（違反即視為失敗）★★★
- 絕對不能出現「說明文字...」「功能名稱」「統計數字1」「操作」「TODO」「placeholder」等任何佔位符
- 所有按鈕必須有描述真實動作的標籤（「新增股票」而不是「操作」，「計算報酬率」而不是「功能」）
- 所有統計數字必須從實際資料計算（不能是寫死的假數字或空佔位）
- 第一次開啟頁面必須自動載入 3-5 筆示範資料（讓使用者立刻看到效果）
- 每一個功能點下去都要有真實的反應和效果

★ 功能完整性（最重要）
- 每個功能都要能真正運作，不能只是 UI 空殼
- 所有按鈕點了要有真實效果
- 資料要能新增、編輯、刪除、查詢
- 有資料驗證（空白欄位、格式錯誤要提示）
- 有確認對話框（刪除前要確認）
- 有 Loading 狀態（操作中顯示等待）
- 有 Empty State（沒有資料時顯示友善訊息）
- 有錯誤處理（操作失敗要告知用戶）

★ 示範資料（必須）
- 頁面初始化時自動插入 3-5 筆真實感的示範資料到 localStorage
- 示範資料必須符合業務情境（股票選股 → 插入真實股票代碼和籌碼數據）
- 讓使用者打開頁面就立刻能「看到」和「操作」，而不是看到空頁面

★ 資料管理
- 所有資料存入 localStorage，重開頁面不會消失
- 支援搜尋和篩選功能
- 資料有時間戳記（建立時間、修改時間）
- 重要資料有備份/匯出功能（CSV 或 JSON）

★ 統計與分析
- 有數字摘要（總數、加總、平均等）
- 有圖表或視覺化（如果資料允許）
- 有時間段篩選（本週、本月、自訂）

★ 使用者體驗
- 鍵盤支援（Enter 送出、Escape 取消）
- 操作成功後有明確回饋（Toast 通知）
- 支援拖曳排序（如果是列表）
- 手機版完整支援（RWD）

★ 業務邏輯
- 根據需求加入合理的業務規則
- 例如：記帳本 → 自動計算結餘、月份統計
- 例如：預約系統 → 防止重複預約、時段衝突
- 例如：客戶管理 → 生日提醒、分類標籤

輸出格式：每個文件用 '=== 文件名 ===' 分隔。

必須輸出：
1. === index.html === (完整 HTML+CSS+JS，無外部依賴，data 存 localStorage)
2. === tests/test_ui.py === (Playwright 自動測試)

━━━━━━ UI 風格：{ui_style}風格 ━━━━━━

【配色系統】
- 背景色：{sc['bg']}
- 卡片色：{sc['card']}
- 主強調色：{sc['accent']}
- 主文字色：{sc['text']}
- 邊框色：{sc['border']}

【字體排版系統（嚴格執行）】
- 大標題：font-size:2rem; font-weight:800; letter-spacing:-0.02em
- 中標題：font-size:1.25rem; font-weight:700
- 小標籤：font-size:0.75rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase
- 內文：font-size:1rem; line-height:1.7; font-weight:400
- 說明文字：font-size:0.875rem; color:透明度70%

【間距系統（嚴格執行）】
- 頁面 padding：2.5rem 3rem（桌面）/ 1.25rem 1rem（手機）
- 區塊間距：3rem 到 5rem
- 卡片內距：1.5rem 到 2rem
- 元素間距：0.75rem / 1rem / 1.5rem
- 按鈕：padding 0.75rem 1.5rem，高度 44px（觸控標準）

【視覺品質要求（必須實作）】
- 卡片：box-shadow 精緻陰影 + border-radius:16px
- 所有互動：transition: all 0.2s cubic-bezier(0.4,0,0.2,1)
- 按鈕 hover：brightness(1.1) + translateY(-1px) + 更強陰影
- 按鈕 active：scale(0.97)
- 卡片 hover：translateY(-4px) + 陰影加深
- 輸入框 focus：邊框色換主色 + box-shadow ring
- 頁面載入：fade-in 動畫 0.3s ease-out

【版面結構（必須有）】
- Header：品牌名稱 + 核心統計數字 + 操作按鈕
- 主內容區：左右分欄或卡片網格，充足留白
- 每個功能模組：標題 + 說明 + 操作
- Empty State：沒有資料時顯示友善提示
- 響應式：完整支援手機版（Tailwind sm/md/lg）

【嚴禁事項】
- 不可用 text-xs 作為主要文字
- 不可按鈕沒有 hover 效果
- 不可版面沒有留白（元素不能擠在一起）
- 不可沒有 loading 或 empty state 設計
- 不可顏色單調（要有層次感）

【技術】
- Tailwind CSS CDN + 自訂 CSS style 標籤
- Google Fonts：<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
- font-family: 'Inter', system-ui, sans-serif
- 繁體中文介面
- localStorage 儲存資料

只輸出代碼，不要解釋。"""

# ─── 呼叫 GPT-4o ─────────────────────────────────────────
response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=16000,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
)

code_output = response.choices[0].message.content
print("AI 生成完成，準備寫入文件...")

# ─── 解析並寫入文件 ──────────────────────────────────────
files_written = []
sections = re.split(r'={3}\s*(.+?)\s*={3}', code_output)

for i in range(1, len(sections), 2):
    filename = sections[i].strip().strip('`')
    content  = sections[i+1].strip() if i+1 < len(sections) else ""
    content  = re.sub(r'^```\w*\n?', '', content)
    content  = re.sub(r'\n?```$', '', content).strip()

    if filename and content and filename.count('/') <= 4 and not filename.startswith('.'):
        dirpath = os.path.dirname(filename)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        files_written.append(filename)
        print(f"寫入：{filename}")

if not files_written:
    out_file = f"ai_output_issue_{issue_number}.md"
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"# Issue #{issue_number}\n\n{code_output}")
    files_written.append(out_file)
    print(f"寫入說明文件：{out_file}")

# ─── 確保 index.html 存在 ────────────────────────────────
if 'index.html' not in files_written:
    html_files = [f for f in files_written if f.endswith('.html')]
    if html_files:
        shutil.copy(html_files[0], 'index.html')
        files_written.append('index.html')
        print(f"自動建立 index.html 來源：{html_files[0]}")

# ─── 後端：寫入部署資訊 ──────────────────────────────────
if 'main.py' in files_written and 'Dockerfile' in files_written:
    deploy_info = {
        "type": "backend",
        "project_id": project_id,
        "customer_id": customer_id,
        "issue_number": issue_number,
        "service_name": f"{customer_id or 'c000000'}-{project_id or 'project'}".lower()[:50],
        "port": "8080"
    }
    with open('deploy_info.json', 'w') as f:
        json.dump(deploy_info, f)
    files_written.append('deploy_info.json')
    print(f"後端部署資訊：{deploy_info['service_name']}")

print(f"完成！共 {len(files_written)} 個文件：{files_written}")
