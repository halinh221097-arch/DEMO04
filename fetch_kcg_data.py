import csv
import ssl
import sys
import urllib.error
import urllib.request

url = "https://data.kcg.gov.tw/File/DirectDownload/80bbbbd3-9ee4-4244-98e9-b4c08deda91b"

# 強制使用 UTF-8 輸出，避免 PowerShell 顯示中文欄位時變成空白或亂碼
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

COLUMN_LABELS = {
    "Id": "編號",
    "Status": "狀態",
    "Name": "活動名稱",
    "Description": "說明",
    "Particpation": "參加對象",
    "Location": "地點",
    "Add": "地址",
    "Tel": "電話",
    "Org": "主辦單位",
    "Start": "開始時間",
    "End": "結束時間",
    "Cycle": "週期",
    "Noncycle": "非週期",
    "Map": "地圖",
    "Px": "經度",
    "Py": "緯度",
    "Travellinginfo": "交通資訊",
    "Parkinginfo": "停車資訊",
    "Charge": "費用",
    "Remarks": "備註",
    "Changetime": "更新時間",
}


def fetch_url(url):
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen(url, context=context) as response:
            return response.read()
    except urllib.error.URLError as e:
        if isinstance(e.reason, ssl.SSLCertVerificationError):
            print("SSL 驗證失敗，改用不驗證方式重試。")
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(url, context=context) as response:
                return response.read()
        raise


def decode_content(content):
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("utf-8", errors="replace")


def print_records(text):
    text = text.lstrip('\ufeff')
    lines = text.splitlines()
    reader = csv.DictReader(lines)
    for row_index, row in enumerate(reader, start=1):
        if row_index > 1:
            print()
        for key, value in row.items():
            label = COLUMN_LABELS.get(key, key)
            print(f"{label}:{value}")


try:
    content = fetch_url(url)
    text = decode_content(content)
    print_records(text)
except Exception as e:
    print(f"讀取資料時發生錯誤: {e}")
