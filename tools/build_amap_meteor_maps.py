from __future__ import annotations

import json
import math
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "maps"
DATA_PATH = OUT_DIR / "amap_route_data.json"
AMAP_KEY = os.environ.get("AMAP_WEB_SERVICE_KEY")

BASE_FONT = Path(r"C:\Windows\Fonts\msyh.ttc")
BOLD_FONT = Path(r"C:\Windows\Fonts\msyhbd.ttc")


@dataclass(frozen=True)
class Point:
    code: str
    name: str
    lon: float
    lat: float
    drive: str
    weather: str
    rank: str
    note: str


BEIJING = Point("京", "北京", 116.397428, 39.909230, "-", "-", "起点", "按天安门附近作为起点")

POINTS = [
    Point("1", "上都湖", 116.262055, 42.599649, "5.7-6.0h", "云19%", "主推", "湖岸/敖包/孤树"),
    Point("2", "元上都", 116.186575, 42.361721, "5.2h", "云31%", "联动", "文化遗址外围合法机位"),
    Point("3", "多伦湖", 116.660941, 42.197453, "5.2h", "云16%", "备份", "湖岸/滦河湖观景平台"),
    Point("4", "乌兰哈达", 113.122579, 41.555532, "4.8h", "云12%", "主推", "火山锥/G208北向"),
    Point("5", "辉腾锡勒", 112.537638, 41.130892, "5.1h", "云58%", "天气备选", "草原/风机/山梁"),
    Point("6", "库布齐七星湖", 108.345138, 40.655115, "8.6h", "云35%", "沙漠备选", "沙丘/孤树/07公路"),
    Point("7", "乌拉盖九曲湾", 119.628760, 45.891933, "12.1h", "云6%", "远程冲刺", "河湾/草原/湖面"),
    Point("8", "达里湖", 116.751105, 43.245061, "7.1h", "云77%", "不建议", "湖岸/达达线"),
    Point("9", "阿斯哈图石林", 117.524483, 43.962185, "8.4h", "云68%", "不建议", "石林/热阿线"),
    Point("10", "腾格里月亮湖", 105.156944, 38.462514, "14.2h", "云62%", "飞银川更合理", "沙丘/月亮湖/敖包湖"),
]

ROUTES = {
    "A 主推 上都湖线": ["京", "1", "2", "3"],
    "B 近程 乌兰哈达": ["京", "4"],
    "C 沙漠 库布齐": ["京", "6"],
    "D 远程 乌拉盖": ["京", "7"],
    "E 西线 腾格里": ["京", "10"],
}

ROUTE_COLORS = {
    "A 主推 上都湖线": "#E76F00",
    "B 近程 乌兰哈达": "#15803D",
    "C 沙漠 库布齐": "#7C3AED",
    "D 远程 乌拉盖": "#0F6CBD",
    "E 西线 腾格里": "#DC2626",
}


def point_by_code(code: str) -> Point:
    if code == "京":
        return BEIJING
    for point in POINTS:
        if point.code == code:
            return point
    raise KeyError(code)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = BOLD_FONT if bold and BOLD_FONT.exists() else BASE_FONT
    return ImageFont.truetype(str(path), size=size)


def hex_to_rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def amap_get_json(endpoint: str, params: dict) -> dict:
    params = dict(params)
    params["key"] = AMAP_KEY
    url = endpoint + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def amap_get_image(params: dict) -> Image.Image:
    params = dict(params)
    params["key"] = AMAP_KEY
    url = "https://restapi.amap.com/v3/staticmap?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=45) as response:
        raw = response.read()
    image_path = OUT_DIR / "_last_staticmap.png"
    image_path.write_bytes(raw)
    return Image.open(image_path).convert("RGB")


def parse_polyline(polyline: str) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for item in polyline.split(";"):
        if not item:
            continue
        lon, lat = item.split(",")
        points.append((float(lon), float(lat)))
    return points


def fetch_route(origin: Point, dest: Point) -> dict:
    data = amap_get_json(
        "https://restapi.amap.com/v3/direction/driving",
        {
            "origin": f"{origin.lon:.6f},{origin.lat:.6f}",
            "destination": f"{dest.lon:.6f},{dest.lat:.6f}",
            "extensions": "base",
            "strategy": "0",
        },
    )
    if data.get("status") != "1":
        raise RuntimeError(f"Amap route failed {origin.name}->{dest.name}: {data}")
    path = data["route"]["paths"][0]
    coords: list[tuple[float, float]] = []
    for step in path["steps"]:
        step_points = parse_polyline(step["polyline"])
        if coords and step_points and coords[-1] == step_points[0]:
            coords.extend(step_points[1:])
        else:
            coords.extend(step_points)
    return {
        "origin": origin.code,
        "destination": dest.code,
        "distance_m": int(path["distance"]),
        "duration_s": int(path["duration"]),
        "coords": coords,
    }


def fetch_routes() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pairs: list[tuple[str, str]] = [
        ("京", "1"),
        ("1", "2"),
        ("2", "3"),
        ("京", "4"),
        ("京", "5"),
        ("京", "6"),
        ("京", "7"),
        ("京", "8"),
        ("京", "9"),
        ("京", "10"),
    ]
    routes = {}
    for origin_code, dest_code in pairs:
        origin = point_by_code(origin_code)
        dest = point_by_code(dest_code)
        route = fetch_route(origin, dest)
        routes[f"{origin_code}-{dest_code}"] = route
        time.sleep(0.2)
    DATA_PATH.write_text(json.dumps(routes, ensure_ascii=False, indent=2), encoding="utf-8")
    return routes


def load_or_fetch_routes() -> dict:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return fetch_routes()


def mercator_world(lon: float, lat: float, zoom: int) -> tuple[float, float]:
    siny = math.sin(math.radians(lat))
    siny = min(max(siny, -0.9999), 0.9999)
    scale = 256 * 2**zoom
    x = scale * (0.5 + lon / 360.0)
    y = scale * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))
    return x, y


def make_projector(center: tuple[float, float], zoom: int, image_size: tuple[int, int], logical_size: tuple[int, int]):
    center_x, center_y = mercator_world(center[0], center[1], zoom)
    img_w, img_h = image_size
    logical_w, logical_h = logical_size
    sx = img_w / logical_w
    sy = img_h / logical_h

    def project(lon: float, lat: float) -> tuple[float, float]:
        x, y = mercator_world(lon, lat, zoom)
        px = (x - center_x + logical_w / 2) * sx
        py = (y - center_y + logical_h / 2) * sy
        return px, py

    return project


def draw_route(draw: ImageDraw.ImageDraw, project, route: dict, color: str, width: int, alpha: int = 210):
    pixels = [project(lon, lat) for lon, lat in route["coords"]]
    pixels = [(x, y) for x, y in pixels if -100 <= x <= 2200 and -100 <= y <= 1700]
    if len(pixels) >= 2:
        draw.line(pixels, fill=hex_to_rgba(color, alpha), width=width, joint="curve")


def draw_marker(draw: ImageDraw.ImageDraw, project, point: Point, color: str, dx: int = 16, dy: int = -38):
    x, y = project(point.lon, point.lat)
    r = 19 if len(point.code) == 1 else 21
    draw.ellipse((x - r, y - r, x + r, y + r), fill=hex_to_rgba(color, 245), outline=(255, 255, 255, 255), width=4)
    code_font = font(22 if len(point.code) == 1 else 17, bold=True)
    bbox = draw.textbbox((0, 0), point.code, font=code_font)
    draw.text((x - (bbox[2] - bbox[0]) / 2, y - (bbox[3] - bbox[1]) / 2 - 1), point.code, fill=(255, 255, 255, 255), font=code_font)

    label = f"{point.name}  {point.drive}  {point.weather}" if point.code != "京" else "北京起点"
    label_font = font(21, bold=True)
    pad_x, pad_y = 9, 6
    lb = draw.textbbox((0, 0), label, font=label_font)
    lx, ly = x + dx, y + dy
    rect = (lx - pad_x, ly - pad_y, lx + (lb[2] - lb[0]) + pad_x, ly + (lb[3] - lb[1]) + pad_y)
    draw.rounded_rectangle(rect, radius=10, fill=(255, 255, 255, 228), outline=hex_to_rgba(color, 230), width=2)
    draw.text((lx, ly), label, fill=(20, 30, 45, 255), font=label_font)


def draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str, w: int):
    draw.rounded_rectangle((28, 24, w - 28, 118), radius=16, fill=(255, 255, 255, 232), outline=(203, 213, 225, 255), width=2)
    draw.text((52, 38), title, fill=(15, 23, 42, 255), font=font(34, bold=True))
    draw.text((52, 82), subtitle, fill=(71, 85, 105, 255), font=font(20))


def draw_panel(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, title: str, rows: Sequence[str]):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=(255, 255, 255, 236), outline=(148, 163, 184, 255), width=2)
    draw.text((x + 20, y + 18), title, fill=(15, 23, 42, 255), font=font(27, bold=True))
    yy = y + 62
    for row in rows:
        color = (31, 41, 55, 255)
        if row.startswith("A "):
            color = hex_to_rgba(ROUTE_COLORS["A 主推 上都湖线"])
        elif row.startswith("B "):
            color = hex_to_rgba(ROUTE_COLORS["B 近程 乌兰哈达"])
        elif row.startswith("C "):
            color = hex_to_rgba(ROUTE_COLORS["C 沙漠 库布齐"])
        elif row.startswith("D "):
            color = hex_to_rgba(ROUTE_COLORS["D 远程 乌拉盖"])
        elif row.startswith("E "):
            color = hex_to_rgba(ROUTE_COLORS["E 西线 腾格里"])
        draw.text((x + 22, yy), row, fill=color, font=font(20, bold=row[:1] in "ABCDE"))
        yy += 33


def format_route_summary(route: dict) -> str:
    km = route["distance_m"] / 1000
    hours = route["duration_s"] / 3600
    return f"{km:.0f}km / {hours:.1f}h"


def route_segments_for(codes: Sequence[str]) -> list[str]:
    keys = []
    for a, b in zip(codes, codes[1:]):
        key = f"{a}-{b}"
        if key not in ROUTE_DATA:
            # Some route groups intentionally use cached Beijing-to-endpoint routes only.
            key = f"京-{b}"
        keys.append(key)
    return keys


def compose_map(
    name: str,
    center: tuple[float, float],
    zoom: int,
    title: str,
    subtitle: str,
    route_names: Sequence[str],
    marker_codes: Sequence[str],
    panel_rows: Sequence[str],
    label_offsets: dict[str, tuple[int, int]],
):
    logical_size = (1024, 768)
    base = amap_get_image(
        {
            "location": f"{center[0]:.6f},{center[1]:.6f}",
            "zoom": str(zoom),
            "size": f"{logical_size[0]}*{logical_size[1]}",
            "scale": "2",
            "traffic": "0",
        }
    ).convert("RGBA")
    draw = ImageDraw.Draw(base, "RGBA")
    project = make_projector(center, zoom, base.size, logical_size)

    for route_name in route_names:
        color = ROUTE_COLORS[route_name]
        codes = ROUTES[route_name]
        for key in route_segments_for(codes):
            if key in ROUTE_DATA:
                draw_route(draw, project, ROUTE_DATA[key], color, width=8)

    color_by_code = {
        "京": "#111827",
        "1": "#E76F00",
        "2": "#E76F00",
        "3": "#E76F00",
        "4": "#15803D",
        "5": "#64748B",
        "6": "#7C3AED",
        "7": "#0F6CBD",
        "8": "#64748B",
        "9": "#64748B",
        "10": "#DC2626",
    }
    for code in marker_codes:
        draw_marker(draw, project, point_by_code(code), color_by_code[code], *label_offsets.get(code, (18, -42)))

    draw_header(draw, title, subtitle, base.size[0])
    if panel_rows:
        panel_h = min(326, max(176, 86 + 33 * len(panel_rows)))
        draw_panel(draw, 34, base.size[1] - panel_h - 36, base.size[0] - 68, panel_h, "路线与编号", panel_rows)

    out = OUT_DIR / name
    base.convert("RGB").save(out, "PNG", optimize=True)
    return out


def write_markdown(outputs: dict[str, Path]):
    table_rows = [
        "| 编号 | 地点 | 车程 | 8/12夜天气 | 推荐 | 机位/说明 |",
        "|---|---|---:|---|---|---|",
    ]
    for point in POINTS:
        table_rows.append(f"| {point.code} | {point.name} | {point.drive} | {point.weather} | {point.rank} | {point.note} |")

    content = f"""# 英仙座流星雨高德路线地图补充

更新时间：2026-08-04  
地图来源：高德静态地图 API；路线来源：高德驾车路径规划 API。  
说明：地图路线为高德 API 返回的驾车 polyline，用于出行判断和方案比较；实际导航请以出发当天高德 App 实时路况为准。

## 总览图

![候选地总览](output/maps/{outputs["overview"].name})

## 编号说明

{chr(10).join(table_rows)}

## 重点路线 A：上都湖 + 元上都 + 多伦湖

![上都湖路线图](output/maps/{outputs["shangdu"].name})

- 主推逻辑：上都湖是这次综合最平衡的目的地，天气窗口约云量 19%，前景有湖岸、敖包、孤树；元上都和多伦湖都在 1.5 小时机动圈内。
- 建议执行：北京中午出发，傍晚先到上都湖，日落前踩东南敖包和北岸孤树；若云量或灯光不理想，转元上都外围合法道路或多伦湖/滦河湖观景平台。

## 重点路线 B：乌兰哈达近程线

![乌兰哈达路线图](output/maps/{outputs["ulanhada"].name})

- 主推逻辑：乌兰哈达车程短，8/12 前半夜云量预报最好；但热门火山口和营地灯多，地图上建议把重点放在火山群外围、G208 北向和暗夜保护区方向。
- 建议执行：日落前踩 5/6 号火山外围和 G208 北向路边，21:30-02:00 主拍，避开游客核心区车灯。

## 远程与沙漠备选

- 库布齐七星湖：沙丘/孤树前景强，约 8.6h，但午夜后云量升高，适合作为有沙漠偏好的备选。
- 乌拉盖九曲湾：天气最好但约 12.1h，适合三天两夜冲刺，不适合疲劳硬跑。
- 腾格里月亮湖：暗夜强，但北京自驾约 14.2h，本次云量不占优；更合理是飞银川再租车。
- 达里湖/阿斯哈图：地景好，但 8/12 夜云量预报偏高，本次不建议首选。

## API 依据

- 高德静态地图 API 支持在图片地图上添加标注、标签、折线等覆盖物。
- 高德路径规划 API 以 HTTP 形式返回驾车线路、距离、预计时长和 polyline；高德官方也提示道路/数据/算法会变更，同一起终点间隔一段时间可能返回不同结果。
"""
    path = ROOT / "英仙座流星雨高德地图补充.md"
    path.write_text(content, encoding="utf-8")
    return path


if __name__ == "__main__":
    if not AMAP_KEY:
        raise RuntimeError("AMAP_WEB_SERVICE_KEY is not set")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ROUTE_DATA = load_or_fetch_routes()

    outputs = {
        "overview": compose_map(
            "meteor_amap_overview.png",
            center=(112.55, 41.35),
            zoom=6,
            title="2026 英仙座流星雨 - 内蒙古候选机位总览",
            subtitle="高德底图 + 驾车路线；编号对应右下角说明。天气为 8/12 20:00-8/13 05:00 预报摘要。",
            route_names=[
                "A 主推 上都湖线",
                "B 近程 乌兰哈达",
                "C 沙漠 库布齐",
                "D 远程 乌拉盖",
                "E 西线 腾格里",
            ],
            marker_codes=["京", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            panel_rows=[
                "A 橙：京 -> 上都湖 -> 元上都 -> 多伦湖｜主推，5.7h到主点，云19%",
                "B 绿：京 -> 乌兰哈达火山/G208｜近程稳妥，4.8h，云12%",
                "C 紫：京 -> 库布齐七星湖｜沙漠前景，8.6h，云35%",
                "D 蓝：京 -> 乌拉盖九曲湾｜远程冲刺，12.1h，云6%，风大",
                "E 红：京 -> 腾格里月亮湖｜暗夜强，14.2h，云62%，更适合飞银川",
                "灰点：辉腾锡勒/达里湖/阿斯哈图｜本次天气偏弱，仅备选",
            ],
            label_offsets={
                "京": (22, -44),
                "1": (24, -64),
                "2": (-230, -68),
                "3": (26, 24),
                "4": (-210, -46),
                "5": (-230, 22),
                "6": (-258, -42),
                "7": (-268, -42),
                "8": (24, -44),
                "9": (24, -42),
                "10": (24, -62),
            },
        ),
        "shangdu": compose_map(
            "meteor_amap_route_shangdu_duolun.png",
            center=(116.40, 41.35),
            zoom=8,
            title="重点路线 A - 上都湖 / 元上都 / 多伦湖",
            subtitle="主推路线：北京 -> 上都湖；元上都、多伦湖为 1.5 小时内机动备份。",
            route_names=["A 主推 上都湖线"],
            marker_codes=["京", "1", "2", "3"],
            panel_rows=[
                "1 上都湖：5.7-6.0h｜云19%｜敖包/北岸孤树/湖岸",
                "2 元上都：距上都湖约0.9h｜云31%｜只取外围合法机位",
                "3 多伦湖：距上都湖约1.4h｜云16%｜湖岸/滦河湖观景平台",
                "执行：8/12中午北京出发，傍晚上都湖踩点，21:30后开拍",
            ],
            label_offsets={
                "京": (24, -40),
                "1": (24, -64),
                "2": (-230, -58),
                "3": (24, 22),
            },
        ),
        "ulanhada": compose_map(
            "meteor_amap_route_ulanhada.png",
            center=(114.75, 40.85),
            zoom=8,
            title="重点路线 B - 乌兰哈达火山 / G208 北向",
            subtitle="近程稳妥路线：车程短，前半夜云量低；重点是避开火山口和营地灯。",
            route_names=["B 近程 乌兰哈达"],
            marker_codes=["京", "4", "5"],
            panel_rows=[
                "4 乌兰哈达：4.8h｜云12%｜火山锥/G208北向/暗夜保护区方向",
                "5 辉腾锡勒：5.1h｜云58%｜天气转好时才考虑",
                "执行：日落前踩5/6号火山外围，21:30-02:00主拍，避开游客核心区",
            ],
            label_offsets={
                "京": (24, -40),
                "4": (24, -58),
                "5": (24, -54),
            },
        ),
    }
    md = write_markdown(outputs)
    print(json.dumps({k: str(v) for k, v in outputs.items()} | {"markdown": str(md), "route_data": str(DATA_PATH)}, ensure_ascii=False, indent=2))
