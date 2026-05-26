import csv
import ssl
import sys
import urllib.error
import urllib.request
from typing import List, Dict

try:
    from flask import Flask, render_template_string, jsonify
except Exception:
    Flask = None

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


def parse_records(text: str) -> List[Dict[str, str]]:
        """Parse CSV text and return list of records with only the configured fields."""
        text = text.lstrip('\ufeff')
        lines = text.splitlines()
        reader = csv.DictReader(lines)
        result: List[Dict[str, str]] = []
        for row in reader:
                item = {k: row.get(k, "") for k in FIELD_ORDER}
                result.append(item)
        return result


# Flask app and templates
HTML_TEMPLATE = """
<!doctype html>
<html lang="zh-Hant">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>活動資料</title>
        <style>
            :root{--accent:#2c7be5;--muted:#6b7280}
            body{font-family:Arial, Helvetica, "Microsoft JhengHei", sans-serif;margin:0;padding:20px;background:#f7f9fb;color:#111}
            .container{max-width:1200px;margin:0 auto;background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(20,20,20,0.05)}
            h1{margin-top:0;color:var(--accent)}
            .meta{color:var(--muted);margin-bottom:12px}
            .table-wrap{overflow-x:auto}
            table{border-collapse:collapse;width:100%;min-width:800px;table-layout:fixed}
            th,td{border:1px solid #e6edf3;padding:12px 10px;text-align:left;vertical-align:top;word-wrap:break-word;white-space:pre-wrap}
            th{background:linear-gradient(0deg,#f1f8ff,#f9fbff);color:#0b3b70;font-weight:600}
            tr:hover td{background:#fbfdff}
            tbody tr:nth-child(even) td{background:#fcfcfd}
            a.link{color:var(--accent);text-decoration:none}
            a.link:hover{text-decoration:underline}
            @media (max-width:720px){
                th,td{padding:10px 6px;font-size:13px}
                .container{padding:12px}
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>活動資料</h1>
            <p class="meta">資料來源: <a class="link" href="{{ url }}" target="_blank" rel="noopener">{{ url }}</a> • 共 {{ records|length }} 筆資料</p>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                        {% for key in field_order %}
                            <th>{{ field_labels[key] }}</th>
                        {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                    {% for r in records %}
                        <tr>
                        {% for key in field_order %}
                            <td>
                                {% if key == 'link' %}
                                    {% if r['link'] %}
                                        <a class="link" href="{{ r['link'] }}" target="_blank" rel="noopener">{{ r['link'] }}</a>
                                    {% endif %}
                                {% else %}
                                    {{ r[key] }}
                                {% endif %}
                            </td>
                        {% endfor %}
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
</html>
"""


app = Flask(__name__) if Flask is not None else None


if app is not None:
        @app.route('/')
        def index():
                try:
                        content = fetch_url(url)
                        text = decode_content(content)
                        records = parse_records(text)
                        return render_template_string(HTML_TEMPLATE, records=records, url=url, field_order=FIELD_ORDER, field_labels=FIELD_LABELS)
                except Exception as e:
                        return f"讀取資料時發生錯誤: {e}", 500

        @app.route('/json')
        def api_json():
                try:
                        content = fetch_url(url)
                        text = decode_content(content)
                        records = parse_records(text)
                        return jsonify(records)
                except Exception as e:
                        return jsonify({'error': str(e)}), 500


def main():
    try:
        content = fetch_url(url)
        text = decode_content(content)
        print_records(text)
    except Exception as e:
        print(f"讀取資料時發生錯誤: {e}")


if __name__ == '__main__':
    # Default behaviour: start Flask web server.
    # Use 'cli' or '--cli' argument to run the original CLI printing instead.
    if app is None:
        print('Flask is not installed. Install with: pip install -r requirements.txt')
    else:
        if any(a in ('cli', '--cli') for a in sys.argv[1:]):
            main()
        else:
            app.run(host='0.0.0.0', port=5000)
