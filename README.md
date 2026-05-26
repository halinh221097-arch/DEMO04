# fetch_kcg_data Flask App

此專案會從新北市資料平台抓取活動資料並顯示。

快速上手

1. 建議建立虛擬環境並安裝依賴：

```bash
python -m venv .venv
.venv\\Scripts\\activate      # Windows PowerShell
pip install -r requirements.txt
```

2. 啟動網站（預設會啟動 Flask）：

```bash
python fetch_kcg_data.py
```

3. 若要以命令列模式列印資料：

```bash
python fetch_kcg_data.py cli
```

路由

- `/` : 顯示 HTML 表格
- `/json` : 回傳 JSON 格式的資料

注意

若在某些環境遇到 SSL 驗證錯誤，程式會嘗試改用不驗證的方式重試。