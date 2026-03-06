# 系統設計文件 (SDD) - V1.0：TravelSync 多人協作旅遊規畫系統

---

## 1. 系統架構

TravelSync V1.0 採用單機全棧 (Single-node Full-stack) 架構，將前端 UI 與後端邏輯整合於 Streamlit 環境。

```text
[使用者瀏覽器] <--(HTTP/WS)--> [app.py (Streamlit UI/Controller)]
                                      |
                              [travel_logic.py (Service Layer)]
                                      |
                              [models.py (ORM Entities)]
                                      |
                              [database.py (Data Persistence)]
                                      |
                              [travelsync.db (SQLite)]
```

---

## 2. 模組功能詳述

### 2.1 `app.py` (介面與控制器)
*   **功能**：管理 Streamlit 頁面配置、Session State (user_name, trip_id)、Tab 分頁渲染與行程卡片 UI。
*   **技術實現**：使用 `st.session_state` 追蹤用戶狀態，`st.rerun()` 確保動作執行後畫面立即更新。

### 2.2 `travel_logic.py` (業務邏輯層)
*   **功能**：封裝核心旅遊管理邏輯。
*   **核心函數**：
    *   `create_trip()`: 處理行程建立與邀請碼生成。
    *   `add_activity()`: 新增行程項目或提案。
    *   `vote_for_item()`: 處理投票防重機制。
    *   `finalize_proposal()`: 轉換提案為正式行程。

### 2.3 `models.py` (資料模型)
*   **Trip** (行程): `id`, `title`, `start_date`, `end_date`, `invite_code` (8碼大寫)。
*   **ScheduleItem** (行程項目): `trip_id`, `day_number`, `title`, `start_time`, `is_proposal` (布林值)。
*   **Vote** (投票): `item_id`, `user_name`。

### 2.4 `database.py` (資料庫層)
*   **連線管理**：使用 SQLAlchemy `create_engine` 與 `SessionLocal`。
*   **初始化**：內建 `init_db()` 函數，程式啟動時自動偵測並建立資料表。

---

## 3. 資料庫設計 (SQLite)

### 3.1 `trips` 表
| 欄位 | 說明 |
|------|------|
| id | INTEGER, PRIMARY KEY |
| title | VARCHAR(255) |
| start_date | DATE |
| end_date | DATE |
| invite_code | VARCHAR(50), UNIQUE |

### 3.2 `schedule_items` 表
| 欄位 | 說明 |
|------|------|
| id | INTEGER, PRIMARY KEY |
| trip_id | INTEGER, FOREIGN KEY |
| day_number | INTEGER |
| title | VARCHAR(255) |
| start_time | TIME, NULLABLE |
| duration | INTEGER |
| location | TEXT |
| note | TEXT |
| is_proposal | BOOLEAN (Default: False) |

### 3.3 `votes` 表
| 欄位 | 說明 |
|------|------|
| id | INTEGER, PRIMARY KEY |
| item_id | INTEGER, FOREIGN KEY |
| user_name | VARCHAR(100) |

---

## 4. 驗證與自動化測試

本系統包含 `test_logic.py` 冒煙測試腳本，驗證以下流程：
1. **資料表初始化與資料庫建立**。
2. **Trip 邀請碼唯一性與關聯建立**。
3. **ScheduleItem 的 is_proposal 旗標切換邏輯**。
4. **Vote 投票統計與使用者身分存取**。

---

## 5. 未來擴充計畫 (Roadmap)
*   **V1.1**: 整合 Google Places API 進行地點搜尋與營業時間抓取。
*   **V1.2**: 實作 Google Maps 地圖元件視覺化行程路徑。
*   **V1.3**: AI 智能優化行程排序建議。
