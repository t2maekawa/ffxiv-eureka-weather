from flask import Flask, render_template
from EorzeaEnv import EorzeaEnv
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
ee = EorzeaEnv()

# JST タイムゾーン
JST = timezone(timedelta(hours=9))

# エリアごとの表示天候
AREA_WEATHER = {
    "pagos": ["霧", "吹雪"],
    "pyros": ["吹雪"]
}

@app.route("/")
def index():
    return "エウレカ天候一覧"

@app.route("/<area>")
def show_area(area):
    area = area.lower()
    if area not in AREA_WEATHER:
        return "指定されたエリアはありません"

    # 現在 UTC 時刻
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)

    # 表示範囲: 過去2時間～未来24時間
    start_time = now_utc - timedelta(hours=2)
    end_time = now_utc + timedelta(hours=24)

    # EorzeaEnv の天候取得
    weathers = ee.weathers_between(start_time, end_time, area=area)

    # JST 表示用に変換
    weather_list = []
    for w in weathers:
        w_time_jst = w.time.astimezone(JST)
        w_name = w.name
        # 指定天候のみ表示
        if w_name in AREA_WEATHER[area]:
            weather_list.append({
                "time": w_time_jst.strftime("%-m月%-d日 %H:%M"),
                "name": w_name
            })

    # 古い順にソート
    weather_list.sort(key=lambda x: x["time"])

    return render_template("weather.html", area=area, weathers=weather_list)
