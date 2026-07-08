from mcp.server.fastmcp import FastMCP
from datetime import date
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
    DATA.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


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


@mcp.tool()
def start_period() -> str:
    """记录今天开始月经。"""
    data = load()
    day = today()

    data["periods"].append({"start": day, "end": None})

    record = get_record(data, day)
    record["period"] = "start"
    record["note"] = "今天开始月经。"

    save(data)
    return f"已记录 {day} 月经开始。"


@mcp.tool()
def end_period() -> str:
    """记录今天结束月经。"""
    data = load()
    day = today()

    for item in reversed(data["periods"]):
        if item.get("end") is None:
            item["end"] = day

            record = get_record(data, day)
            record["period"] = "end"
            record["note"] = "今天月经结束。"

            save(data)
            return f"已记录 {day} 月经结束。"

    return "没有找到正在进行中的经期。"


@mcp.tool()
def record_today(raw_text: str) -> str:
    """用自然语言记录今天的经期、心情、流量、疼痛、颜色等。"""
    data = load()
    day = today()
    record = get_record(data, day)

    record["raw"].append(raw_text)
    record["note"] = raw_text

    moods = {"烦": "烦躁", "难过": "难过", "开心": "开心", "累": "疲惫",
             "崩溃": "崩溃", "还行": "还行", "平静": "平静"}
    for k, v in moods.items():
        if k in raw_text:
            record["mood"] = v
            break

    if "量多" in raw_text or "很多" in raw_text:
        record["flow"] = "多"
    elif "量少" in raw_text or "一点点" in raw_text:
        record["flow"] = "少"
    elif "中等" in raw_text or "量中" in raw_text:
        record["flow"] = "中"

    if "很疼" in raw_text or "痛死" in raw_text or "疼死" in raw_text:
        record["pain"] = "重"
    elif "有点疼" in raw_text or "坠" in raw_text or "酸" in raw_text:
        record["pain"] = "轻中度"
    elif "不疼" in raw_text or "没疼" in raw_text:
        record["pain"] = "无"

    for c in ["鲜红", "深红", "暗红", "粉色", "褐色", "黑色"]:
        if c in raw_text:
            record["color"] = c
            break

    save(data)

    return (
        "记下来了。\n"
        f"日期：{day}\n"
        f"心情：{record.get('mood') or '未识别'}\n"
        f"流量：{record.get('flow') or '未识别'}\n"
        f"疼痛：{record.get('pain') or '未识别'}\n"
        f"颜色：{record.get('color') or '未识别'}"
    )


@mcp.tool()
def get_day_detail(day: str = "") -> str:
    """查看某一天的详细记录。day 格式 YYYY-MM-DD，不填默认今天。"""
    data = load()
    day = day or today()
    record = data.get("records", {}).get(day)

    if not record:
        return f"{day} 暂无记录。"

    return (
        f"📅 {day}\n\n"
        f"心情：{record.get('mood') or '-'}\n"
        f"流量：{record.get('flow') or '-'}\n"
        f"疼痛：{record.get('pain') or '-'}\n"
        f"颜色：{record.get('color') or '-'}\n"
        f"备注：{record.get('note') or '-'}"
    )


@mcp.tool()
def get_month_view(year: int = 0, month: int = 0) -> str:
    """查看某个月的月历记录。year/month 不填默认本月。"""
    data = load()
    today_date = date.today()

    year = year or today_date.year
    month = month or today_date.month

    first = date(year, month, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    days = (next_month - first).days
    lines = [f"🌸 {year}-{month:02d} 周期月历", ""]

    for d in range(1, days + 1):
        day = f"{year}-{month:02d}-{d:02d}"
        record = data.get("records", {}).get(day, {})

        marks = []
        if record.get("period") == "start":
            marks.append("🩸开始")
        elif record.get("period") == "end":
            marks.append("🩸结束")
        if record.get("mood"):
            marks.append("🙂")
        if record.get("pain"):
            marks.append("疼")
        if record.get("flow"):
            marks.append("量")
        if record.get("note"):
            marks.append("记")

        text = " ".join(marks) if marks else "-"
        lines.append(f"{d:02d}  {text}")

    return "\n".join(lines)


@mcp.tool()
def history() -> str:
    """查看历史经期记录。"""
    data = load()
    periods = data.get("periods", [])

    if not periods:
        return "暂无经期历史。"

    lines = []
    for i, item in enumerate(periods, 1):
        start = item.get("start")
        end = item.get("end") or "未结束"
        lines.append(f"{i}. {start} ~ {end}")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()    return (
        f"📅 {day}\n\n"
        f"心情：{record.get('mood') or '-'}\n"
        f"流量：{record.get('flow') or '-'}\n"
        f"疼痛：{record.get('pain') or '-'}\n"
        f"颜色：{record.get('color') or '-'}\n"
        f"备注：{record.get('note') or '-'}"
    )


@mcp.tool()
def get_current_month_view() -> str:
    """查看本月周期月历。"""
    data = load()
    today_date = date.today()

    year = today_date.year
    month = today_date.month

    first = date(year, month, 1)

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    days = (next_month - first).days
    lines = [f"🌸 {year}-{month:02d} 周期月历", ""]

    for d in range(1, days + 1):
        day = f"{year}-{month:02d}-{d:02d}"
        record = data.get("records", {}).get(day, {})

        marks = []

        if record.get("period") == "start":
            marks.append("🩸开始")
        elif record.get("period") == "end":
            marks.append("🩸结束")

        if record.get("mood"):
            marks.append("🙂")
        if record.get("pain"):
            marks.append("疼")
        if record.get("flow"):
            marks.append("量")
        if record.get("note"):
            marks.append("记")

        text = " ".join(marks) if marks else "-"
        lines.append(f"{d:02d}  {text}")

    return "\n".join(lines)


@mcp.tool()
def history() -> str:
    """查看历史经期记录。"""
    data = load()
    periods = data.get("periods", [])

    if not periods:
        return "暂无经期历史。"

    lines = []

    for i, item in enumerate(periods, 1):
        start = item.get("start")
        end = item.get("end") or "未结束"
        lines.append(f"{i}. {start} ~ {end}")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()    if pain:
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
def start_period() -> str:
    """记录今天开始月经。"""
    data = load()
    day = today()
    data["periods"].append({"start": day, "end": None})
    record = get_record(data, day)
    record["period"] = "start"
    save(data)
    return f"已记录 {day} 月经开始。"


@mcp.tool()
def end_period() -> str:
    """记录今天结束月经。"""
    data = load()
    day = today()

    for item in reversed(data["periods"]):
        if item.get("end") is None:
            item["end"] = day
            record = get_record(data, day)
            record["period"] = "end"
            save(data)
            return f"已记录 {day} 月经结束。"

    return "没有找到正在进行中的经期。"


@mcp.tool()
def get_day_detail(day: str = "") -> str:
    """查看某一天的详细记录。day 格式 YYYY-MM-DD，不填默认今天。"""
    data = load()
    day = day or today()
    record = data.get("records", {}).get(day)

    if not record:
        return f"{day} 暂无记录。"

    return (
        f"📅 {day}\n\n"
        f"心情：{record.get('mood') or '-'}\n"
        f"流量：{record.get('flow') or '-'}\n"
        f"疼痛：{record.get('pain') or '-'}\n"
        f"颜色：{record.get('color') or '-'}\n"
        f"备注：{record.get('note') or '-'}"
    )


@mcp.tool()
def get_month_view(year: int = 0, month: int = 0) -> str:
    """查看某个月的月历记录。"""
    data = load()
    today_date = date.today()

    year = year or today_date.year
    month = month or today_date.month

    first = date(year, month, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    days = (next_month - first).days
    lines = [f"🌸 {year}-{month:02d} 周期月历", ""]

    for d in range(1, days + 1):
        day = f"{year}-{month:02d}-{d:02d}"
        record = data.get("records", {}).get(day, {})

        marks = []
        if record.get("period") == "start":
            marks.append("🩸开始")
        elif record.get("period") == "end":
            marks.append("🩸结束")
        if record.get("mood"):
            marks.append("🙂")
        if record.get("pain"):
            marks.append("疼")
        if record.get("flow"):
            marks.append("量")

        text = " ".join(marks) if marks else "-
