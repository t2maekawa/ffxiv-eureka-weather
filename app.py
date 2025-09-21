from flask import Flask, render_template
from eorzeaenv import EorzeaEnv
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
env = EorzeaEnv()

# 日本時間（JST）
JST = timezone(timedelta(hours=9))

# 英語→日本語の天候マッピング
WEATHER_TRANSLATE = {
    "Fog": "霧",
    "Blizzards": "吹雪"
}

# エリアと対象天候のマッピング
AREAS = {
    "pagos": {
        "name": "Eureka Pagos",
        "weathers": ["Fog", "Blizzards"],
    },
    "pyros": {
        "name": "Eureka Pyros",
        "weathers": ["Blizzards"],
    },
}

def format_jst(dt: datetime) -> str:
    """JST日時を '9月22日 11:00' の形式にフォーマット"""
    return f"{dt.month}月{dt.day}日 {dt.strftime('%H:%M')}"

def get_weather_list(area_name, allowed_weathers, count=100):
    """
    指定エリアの天気予報を取得し、特定の天候だけ残す
    過去2時間〜未来24時間, JST表示, 古い順ソート
    """
    location = env.location(area_name)
    forecast = location.forecast(count=count)

    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    start_time = now_utc - timedelta(hours=2)
    end_time = now_utc + timedelta(hours=24)

    data = []
    for f in forecast:
        if f.weather in allowed_weathers:
            if start_time <= f.target_time <= end_time:
                jst_time = f.target_time.replace(tzinfo=timezone.utc).astimezone(JST)
                data.append({
                    "datetime": jst_time,  # ソート用
                    "time": format_jst(jst_time),
                    "weather": WEATHER_TRANSLATE.get(f.weather, f.weather)
                })

    # 過去→未来順にソート
    data.sort(key=lambda x: x["datetime"])
    return data

@app.route("/")
def index():
    return render_template("index.html", areas=AREAS)

@app.route("/<zone>")
def show_zone(zone):
    if zone not in AREAS:
        return "Area not found", 404
    area_info = AREAS[zone]
    weather_list = get_weather_list(area_info["name"], area_info["weathers"])
    return render_template("zone.html", area=area_info["name"], weather_list=weather_list)

if __name__ == "__main__":
    app.run(debug=True)
