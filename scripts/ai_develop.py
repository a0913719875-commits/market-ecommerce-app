"""AI 自動開發腳本 - 由 GitHub Actions 呼叫"""
import os
import re
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
issue_body   = os.environ.get("ISSUE_BODY", "")
issue_title  = os.environ.get("ISSUE_TITLE", "")
issue_number = os.environ.get("ISSUE_NUMBER", "0")
category     = os.environ.get("CATEGORY", "新功能開發")

# 提取 Codex Prompt 區塊
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
    prompt = f"根據以下需求實作代碼：{issue_title}\n\n{issue_body[:1000]}"

print(f"開發需求：{issue_title}")
print(f"分類：{category}")
print(f"Prompt 長度：{len(prompt)} 字元")

# 呼叫 OpenAI 生成代碼
response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=4000,
    messages=[
        {
            "role": "system",
            "content": (
                f"你是一個資深 {category} 開發工程師。"
                "根據需求生成完整可執行的代碼。"
                "輸出格式：每個文件用 '=== 文件名 ===' 分隔，後接代碼區塊。"
                "重要：若需求是網頁、前端、UI、名片、介面、靜態網站，主文件必須命名為 index.html（單一完整 HTML，包含所有 CSS 和 JS，無外部依賴）。"
                "只輸出代碼，不要額外解釋。"
            )
        },
        {"role": "user", "content": prompt}
    ]
)

code_output = response.choices[0].message.content
print("AI 生成完成，準備寫入文件...")

# 解析並寫入文件
files_written = []
sections = re.split(r'={3}\s*(.+?)\s*={3}', code_output)

for i in range(1, len(sections), 2):
    filename = sections[i].strip()
    content  = sections[i+1].strip() if i+1 < len(sections) else ""
    content  = re.sub(r'^```\w*\n?', '', content)
    content  = re.sub(r'```$', '', content).strip()

    if filename and content and filename.count('/') <= 4:
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
        f.write(f"# Issue #{issue_number} AI 開發輸出\n\n{code_output}")
    files_written.append(out_file)
    print(f"寫入說明文件：{out_file}")

# 若 AI 產出 HTML 但未命名 index.html，自動補建 index.html（GitHub Pages 需要）
if 'index.html' not in files_written:
    html_files = [f for f in files_written if f.endswith('.html')]
    if html_files:
        import shutil
        shutil.copy(html_files[0], 'index.html')
        files_written.append('index.html')
        print(f"自動建立 index.html（來源：{html_files[0]}）")

print(f"完成！共寫入 {len(files_written)} 個文件：{files_written}")
