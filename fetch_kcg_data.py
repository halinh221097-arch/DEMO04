import csv
import ssl
import sys
import urllib.error
import urllib.request

url = "https://data.ntpc.gov.tw/api/datasets/781b822e-214a-4b9a-b4db-32c9f4626d98/csv/file"

# 強制使用 UTF-8 輸出，避免 PowerShell 顯示中文欄位時變成空白或亂碼
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

FIELD_ORDER = [
    "author",
    "type",
    "startdate",
    "enddate",
    "title",
    "link",
    "description",
    "pubdate",
]

FIELD_LABELS = {
    "author": "Author（發布單位）",
    "type": "Type（活動屬性）",
    "startdate": "Startdate（公告起日）",
    "enddate": "Enddate（公告迄日）",
    "title": "Title（活動名稱）",
    "link": "Link（連結網址）",
    "description": "Description（活動內容）",
    "pubdate": "Pubdate（公布日期）",
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
        print(f"第{row_index}筆資料:")
        for key in FIELD_ORDER:
            value = row.get(key, "")
            label = FIELD_LABELS.get(key, key)
            print(f"{label}:{value}")
        print()


try:
    content = fetch_url(url)
    text = decode_content(content)
    print_records(text)
except Exception as e:
    print(f"讀取資料時發生錯誤: {e}")
