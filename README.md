# NANG4 JOENG6 STUDIO - Pottery Booking System

能樣陶室 - 陶藝課程預約系統

## 功能特色
- ✅ 用戶註冊與登入（密碼安全加密）
- ✅ 課程預約系統（支持日期、課程類型、時段選擇）
- ✅ 時數管理與扣費
- ✅ 管理員面板（充值時數、成員管理）
- ✅ 雙語支持（中文/English）
- ✅ 響應式設計（手機友好）

## 安裝與運行

### 環境要求
- Python 3.8+
- pip

### 步驟1：安裝依賴
```bash
pip install -r requirements.txt
```

### 步驟2：配置環境變數
複製 `.env.example` 並創建 `.env` 文件：
```bash
cp .env.example .env
```

編輯 `.env` 並設置：
- `SECRET_KEY` - Flask 應用密鑰（用於會話加密）
- `ADMIN_EMAIL` - 管理員電郵地址（默認：admin@nang4joeng6.studio）
- `FLASK_ENV` - 環境模式（development/production）

### 步驟3：啟動應用
```bash
python app.py
```

應用將運行在 `http://127.0.0.1:5000`

## 使用方法

### 管理員設置
1. 首先使用管理員電郵地址註冊帳戶
   - 電郵：`admin@nang4joeng6.studio`（或您在 ADMIN_EMAIL 設置的地址）
   - 密碼：設置任意安全密碼

2. 登入後訪問 `/nang4_topup` 進入管理員面板

3. 在管理員面板中：
   - 查看所有成員列表
   - 搜索成員並充值時數
   - 點擊成員名行自動填充電郵

### 普通用戶
1. **註冊**：使用任意電郵創建帳戶
2. **預約**：
   - 選擇預約日期
   - 選擇課程類型（陶輪/手捏）
   - 選擇預約時段（09:00, 10:30, 12:00, 14:00, 16:00, 18:00）
   - 確認預約（扣除1小時時數）

3. **語言切換**：右上角中文/EN 按鈕切換語言

## 預約時段
- 09:00 AM
- 10:30 AM
- 12:00 PM
- 14:00 (2:00 PM)
- 16:00 (4:00 PM)
- 18:00 (6:00 PM)

## 數據存儲
- 使用 SQLite 數據庫（`instance/nang4_studio.db`）
- 自動創建於首次運行

## API 路由
- `GET /` - 首頁（登入後顯示預約頁面）
- `POST /login` - 登入
- `POST /register` - 註冊
- `POST /book` - 新增預約
- `GET /logout` - 登出
- `GET /nang4_topup` - 管理員面板
- `POST /nang4_topup` - 管理員充值時數
- `GET /set_lang/<lang>` - 切換語言

## 技術棧
- **後端**：Flask 2.3.3
- **數據庫**：SQLAlchemy 3.0.5 + SQLite
- **安全**：Werkzeug（密碼雜湊）
- **時區**：pytz
- **環境配置**：python-dotenv

## 開發者注意

### 修改預約時段
編輯 `app.py` 中的 `BOOKING_TIMES` 列表：
```python
BOOKING_TIMES = ['09:00', '10:30', '12:00', '14:00', '16:00', '18:00']
```

### 新增語言
在 `LANG_DICT` 中添加新的語言字典

### 數據庫遷移
如果修改了模型，需要刪除舊的 `instance/nang4_studio.db` 並重新運行應用

## 故障排除

**管理員無法登入**
- 確認已用 ADMIN_EMAIL 郵箱註冊帳戶
- 檢查 `.env` 中的 ADMIN_EMAIL 設置是否正確

**預約時無法選擇時段**
- 確保已刷新頁面
- 檢查瀏覽器控制台是否有錯誤

## 安全建議（生產環境）
- 更改 `SECRET_KEY` 為強隨機密鑰
- 使用生產級 WSGI 服務器（Gunicorn/uWSGI）
- 配置 HTTPS
- 定期備份數據庫
- 設置強密碼策略

---
**最後更新**：2026年4月21日
