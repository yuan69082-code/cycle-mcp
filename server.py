from mcp.server.fastmcp import FastMCP
from datetime import date
import json
from pathlib import Path

mcp = FastMCP("Cycle MCP")

DATA = Path(__file__).parent / "cycle.json"


def load():
    if not DATA.exists():
        return {"periods": []}
    with open(DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@mcp.tool()
def start_period():
    """记录今天开始来月经"""
    data = load()
    data["periods"].append({
        "start": str(date.today()),
        "end": None
    })
    save(data)
    return f"已记录今天 {date.today()} 为月经开始。"


@mcp.tool()
def end_period():
    """记录今天结束月经"""
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
