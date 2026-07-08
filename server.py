from mcp.server.fastmcp import FastMCP
from datetime import date, datetime
import json
from pathlib import Path

mcp = FastMCP("Cycle MCP")

DATA = Path(__file__).parent / "cycle.json"


def load():
    if not DATA.exists():
        return {"periods": [], "records": {}}
    data = json.loads(DATA.read_text(encoding="utf-8"))
    data.setdefault("periods", [])
    data.setdefault("records", {})
    return data


def save(data):
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def today():
    return date.today().isoformat()


def get_record(data, day):
    data["records"].setdefault(day, {
        "mood": "",
        "flow": "",
        "pain": "",
        "color": "",
        "note": "",
        "raw": []
    })
    return data["records"][day]


def detect_mood(text):
    moods = {
        "烦": "烦躁",
        "难过": "难过",
        "开心": "开心",
        "累": "疲惫",
        "崩溃": "崩溃",
        "还行": "还行",
        "平静": "平静"
    }
    for k, v in moods.items():
        if k in text:
            return v
    return ""


def detect_flow(text):
    if "量多" in text or "很多" in text:
        return "多"
    if "量少" in text or "一点点" in text:
        return "少"
    if "中等" in text or "量中" in text:
        return "中"
    return ""


def detect_pain(text):
    if "很疼" in text or "痛死" in text or "疼死" in text:
        return "重"
    if "有点疼" in text or "坠" in text or "酸" in text:
        return "轻中度"
    if "不疼" in text or "没疼" in text:
        return "无"
    return ""


def detect_color(text):
    colors = ["鲜红", "深红", "暗红", "粉色", "褐色", "黑色"]
    for c in colors:
        if c in text:
            return c
    return ""


@mcp.tool()
def record_today(raw_text: str) -> str:
    """用自然语言记录今天的经期、心情、流量、疼痛、颜色等。"""
    data = load()
    day = today()
    record = get_record(data, day)

    record["raw"].append(raw_text)
    record["note"] = raw_text

    mood = detect_mood(raw_text)
    flow = detect_flow(raw_text)
    pain = detect_pain(raw_text)
    color = detect_color(raw_text)

    if mood:
        record["mood"] = mood
    if flow:
        record["flow"] = flow
    if pain:
        record["pain"] = pain
    if color:
        record["color"] = color

    if "来了" in raw_text or "来月经" in raw_text or "姨妈来了" in raw_text:
        data["periods"].append({"start": day, "end": None})
        record["period"] = "start"

    if "结束了" in raw_text or "干净了" in raw_text:
        for item in reversed(data["periods"]):
            if item.get("end") is None:
                item["end"] = day
                break
        record["period"] = "end"

    save(data)

    return (
        "我记下来了。\n"
        f"日期：{day}\n"
        f"心情：{record.get('mood') or '未识别'}\n"
        f"流量：{record.get('flow') or '未识别'}\n"
        f"疼痛：{record.get('pain') or '未识别'}\n"
        f"颜色：{record.get('color') or '未识别'}"
    )


@mcp.tool()
def start_period() ->    """记录今天结束月经"""
    data = load()

    for item in reversed(data["periods"]):
        if item["end"] is None:
            item["end"] = str(date.today())
            save(data)
            return f"已记录今天 {date.today()} 为月经结束。"

    return "没有找到正在进行中的经期。"


@mcp.tool()
def history():
    """查看历史记录"""

    data = load()

    if not data["periods"]:
        return "暂无记录。"

    return data["periods"]


if __name__ == "__main__":
    mcp.run()
