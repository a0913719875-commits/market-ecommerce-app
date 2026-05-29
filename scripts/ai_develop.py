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

# ─── 系統提示詞 ─────────────────────────────────────────
if needs_backend and not is_static:
    system_prompt = """你是資深全端工程師（AI Company OS Codex）。
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
- 加入 /health 端點回傳 {"status":"ok"}
- 資料暫存用 dict（無 DB 時）

只輸出代碼，不要解釋。"""
else:
    system_prompt = """你是資深前端工程師（AI Company OS Codex）。
根據需求生成完整可執行的靜態網頁。

輸出格式：每個文件用 '=== 文件名 ===' 分隔。

必須輸出以下文件：
1. === index.html === (完整 HTML，含所有 CSS/JS，無外部依賴)
2. === tests/test_ui.py === (Playwright 自動測試)

index.html 注意事項：
- 深色主題
- 響應式設計
- 所有功能在單一 HTML 文件中

只輸出代碼，不要解釋。"""

# ─── 呼叫 GPT-4o ─────────────────────────────────────────
response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=6000,
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
