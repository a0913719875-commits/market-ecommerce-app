# 菜市場電商 APP

React + Flask 的菜市場電商初始架構，目標部署到 Firebase Hosting 與 Cloud Run，資料層使用 Firestore，登入入口預留 LINE LIFF。

## 專案結構

```text
market-app/
├── backend/
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── .env.example
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── styles.css
│       ├── api/
│       │   └── client.js
│       ├── context/
│       │   └── AuthContext.jsx
│       └── pages/
│           ├── CartPage.jsx
│           ├── NotificationsPage.jsx
│           ├── OrdersPage.jsx
│           ├── ProductsPage.jsx
│           ├── VendorDashboardPage.jsx
│           └── WalletPage.jsx
├── Dockerfile
├── firebase.json
├── requirements.txt
└── README.md
```

## 後端功能

Flask API 目前包含：

- `GET /api/health`：健康檢查
- `GET /api/products`：商品列表
- `POST /api/products`：新增商品
- `GET /api/cart`：取得購物車
- `POST /api/cart/items`：加入購物車
- `DELETE /api/cart/items/<product_id>`：移除購物車商品
- `GET /api/wallet`：取得錢包餘額與交易紀錄
- `POST /api/wallet/top-up`：錢包儲值
- `GET /api/vendors/<vendor_id>/dashboard`：攤商後台資料
- `GET /api/orders`：訂單列表
- `POST /api/orders`：建立訂單
- `PATCH /api/orders/<order_id>/status`：更新訂單狀態
- `POST /api/line/notify`：LINE 通知佇列入口

需要登入的 API 使用 `X-LIFF-User-ID` header 作為初始身份識別。正式環境應改為驗證 LIFF access token 或 Firebase Auth token。

## 本機開發

### 後端

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export USE_FIRESTORE=false
python backend/main.py
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:USE_FIRESTORE="false"
python backend/main.py
```

後端預設啟動於 `http://localhost:8080`。

### 前端

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

前端預設使用 `VITE_API_BASE_URL=http://localhost:8080`。

## Firestore

初始集合設計：

- `products`
- `carts/{userId}`
- `wallets/{userId}`
- `wallets/{userId}/transactions`
- `orders`

Cloud Run 若在 Google Cloud 上執行，通常透過服務帳號權限連線 Firestore，不需要在容器內放金鑰。請確認 Cloud Run service account 具有 Firestore 讀寫權限。

## LINE LIFF

前端 `.env` 設定：

```text
VITE_LINE_LIFF_ID=your-liff-id
```

若未設定 LIFF ID，前端會使用本機測試使用者 `local-line-user`。正式環境請建立 LIFF app，並把 Firebase Hosting 網址加入 LIFF Endpoint URL。

## Cloud Run 部署

```bash
gcloud run deploy market-app-backend \
  --source . \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars USE_FIRESTORE=true
```

部署完成後，將 Cloud Run URL 設定到前端：

```text
VITE_API_BASE_URL=https://your-cloud-run-url
```

## Firebase Hosting 部署

```bash
cd frontend
npm install
npm run build
cd ..
firebase deploy --only hosting
```

## 後續建議

- LINE Messaging API：在 `POST /api/line/notify` 串接 channel access token 與 push message。
- 權限模型：新增 buyer/vendor/admin roles，避免只依賴 header。
- 金流：錢包儲值目前是 MVP 模擬，正式環境需串接付款服務並保存交易狀態。
- Firestore Rules：依角色限制商品、訂單、錢包讀寫範圍。
