# 台股系統優化

此專案使用 FastAPI 來實作台股系統的優化需求，包括停損邏輯改進、MACD 買入策略、掃股時間調整及通知修復。

## 功能

1. 更新交易邏輯：設定停損百分比與 MACD 黃金交叉的買入信號。
2. 調整掃股時間：設定掃股的具體時間。
3. 修正推播格式：修正 RISK_ALERT 的 LINE 推播通知格式。

## 快速開始

1. 安裝依賴：

    ```bash
    pip install -r requirements.txt
    ```

2. 啟動服務：

    ```bash
    python main.py
    ```

3. 瀏覽以下端點：

    - 更新交易邏輯: `PATCH /trading/rules`
    - 設置掃股時間: `PATCH /schedule`
    - 發送風險警告: `POST /alert/risk`

## 技術細節

- **框架**：FastAPI
- **文件**：使用 Swagger 錯誤 https://localhost:8000/docs 檢視