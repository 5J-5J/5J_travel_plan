# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont


AMAP_KEY = os.environ.get("AMAP_WEB_SERVICE_KEY")

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\simsun.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
]
BOLD_FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\msyhbd.ttc"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"),
]


@dataclass(frozen=True)
class Point:
    code: str
    name: str
    lon: float
    lat: float
    label: str
    color: str
    dx: int
    dy: int


def read_config(path: str) -> dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def first_existing(paths: Sequence[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = first_existing(BOLD_FONT_CANDIDATES if bold else FONT_CANDIDATES)
    if path:
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def hex_to_rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def parse_point(raw: dict[str, Any], default_color: str = "#2563EB") -> Point:
    code = str(raw["code"])
    name = str(raw["name"])
    label = str(raw.get("label") or f"{code} {name}")
    return Point(
        code=code,
        name=name,
        lon=float(raw["lon"]),
        lat=float(raw["lat"]),
        label=label,
        color=str(raw.get("color") or default_color),
        dx=int(raw.get("dx", 18)),
        dy=int(raw.get("dy", -42)),
    )


def amap_get_json(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    if not AMAP_KEY:
        raise RuntimeError("AMAP_WEB_SERVICE_KEY is not set")
    params = dict(params)
    params["key"] = AMAP_KEY
    url = endpoint + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def amap_get_image(params: dict[str, Any], temp_path: Path) -> Image.Image:
    if not AMAP_KEY:
        raise RuntimeError("AMAP_WEB_SERVICE_KEY is not set")
    params = dict(params)
    params["key"] = AMAP_KEY
    url = "https://restapi.amap.com/v3/staticmap?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as response:
        raw = response.read()
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.write_bytes(raw)
    return Image.open(temp_path).convert("RGB")


def parse_polyline(polyline: str) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for item in polyline.split(";"):
        if not item:
            continue
        lon, lat = item.split(",")
        points.append((float(lon), float(lat)))
    return points


def fetch_route(origin: Point, dest: Point, strategy: str = "0") -> dict[str, Any]:
    data = amap_get_json(
        "https://restapi.amap.com/v3/direction/driving",
        {
            "origin": f"{origin.lon:.6f},{origin.lat:.6f}",
            "destination": f"{dest.lon:.6f},{dest.lat:.6f}",
            "extensions": "base",
            "strategy": strategy,
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


def required_segments(routes: Sequence[dict[str, Any]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    pairs: list[tuple[str, str]] = []
    for route in routes:
        codes = [str(code) for code in route["codes"]]
        for origin, dest in zip(codes, codes[1:]):
            pair = (origin, dest)
            if pair not in seen:
                seen.add(pair)
                pairs.append(pair)
    return pairs


def load_or_fetch_routes(
    points: dict[str, Point],
    routes: Sequence[dict[str, Any]],
    route_data_path: Path | None,
    refresh: bool,
    strategy: str,
) -> dict[str, Any]:
    route_data: dict[str, Any] = {}
    if route_data_path and route_data_path.exists() and not refresh:
        route_data = json.loads(route_data_path.read_text(encoding="utf-8"))

    for origin_code, dest_code in required_segments(routes):
        key = f"{origin_code}-{dest_code}"
        if key in route_data and not refresh:
            continue
        route_data[key] = fetch_route(points[origin_code], points[dest_code], strategy=strategy)
        time.sleep(0.35)

    if route_data_path:
        route_data_path.parent.mkdir(parents=True, exist_ok=True)
        route_data_path.write_text(json.dumps(route_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return route_data


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
        return (x - center_x + logical_w / 2) * sx, (y - center_y + logical_h / 2) * sy

    return project


def draw_route(draw: ImageDraw.ImageDraw, project, route: dict[str, Any], color: str, width: int, alpha: int):
    pixels = [project(lon, lat) for lon, lat in route["coords"]]
    pixels = [(x, y) for x, y in pixels if -250 <= x <= 2300 and -250 <= y <= 1800]
    if len(pixels) >= 2:
        draw.line(pixels, fill=hex_to_rgba(color, alpha), width=width, joint="curve")


def text_size(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=text_font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_marker(draw: ImageDraw.ImageDraw, project, point: Point, marker_size: int, label_size: int):
    x, y = project(point.lon, point.lat)
    r = marker_size if len(point.code) <= 2 else marker_size + 2
    draw.ellipse((x - r, y - r, x + r, y + r), fill=hex_to_rgba(point.color, 245), outline=(255, 255, 255, 255), width=4)

    code_font = font(max(13, int(marker_size * 0.92)), bold=True)
    cw, ch = text_size(draw, point.code, code_font)
    draw.text((x - cw / 2, y - ch / 2 - 1), point.code, fill=(255, 255, 255, 255), font=code_font)

    label_font = font(label_size, bold=True)
    lw, lh = text_size(draw, point.label, label_font)
    lx, ly = x + point.dx, y + point.dy
    pad_x, pad_y = 8, 5
    draw.rounded_rectangle(
        (lx - pad_x, ly - pad_y, lx + lw + pad_x, ly + lh + pad_y),
        radius=9,
        fill=(255, 255, 255, 232),
        outline=hex_to_rgba(point.color, 235),
        width=2,
    )
    draw.text((lx, ly), point.label, fill=(15, 23, 42, 255), font=label_font)


def draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str, image_width: int):
    if not title and not subtitle:
        return
    height = 92 if subtitle else 62
    draw.rounded_rectangle((28, 24, image_width - 28, 24 + height), radius=16, fill=(255, 255, 255, 238), outline=(203, 213, 225, 255), width=2)
    if title:
        draw.text((52, 36), title, fill=(15, 23, 42, 255), font=font(32, bold=True))
    if subtitle:
        draw.text((52, 80), subtitle, fill=(71, 85, 105, 255), font=font(19))


def draw_panel(draw: ImageDraw.ImageDraw, panel: dict[str, Any], image_size: tuple[int, int]):
    if not panel:
        return
    rows = panel.get("rows") or []
    if not rows:
        return

    x = int(panel.get("x", 34))
    width = int(panel.get("width", min(760, image_size[0] - 68)))
    row_height = int(panel.get("row_height", 31))
    title = str(panel.get("title", "路线说明"))
    height = int(panel.get("height", 78 + row_height * len(rows)))
    y = int(panel.get("y", image_size[1] - height - 28))

    draw.rounded_rectangle((x, y, x + width, y + height), radius=16, fill=(255, 255, 255, 238), outline=(148, 163, 184, 255), width=2)
    draw.text((x + 20, y + 16), title, fill=(15, 23, 42, 255), font=font(25, bold=True))
    yy = y + 56
    for row in rows:
        text = str(row["text"] if isinstance(row, dict) else row)
        color = str(row.get("color", "#1F2937") if isinstance(row, dict) else "#1F2937")
        draw.text((x + 22, yy), text, fill=hex_to_rgba(color), font=font(18, bold=True))
        yy += row_height


def compose_map(config: dict[str, Any], route_data: dict[str, Any], output_path: Path) -> Path:
    logical_size = tuple(config.get("size", [1024, 768]))
    if len(logical_size) != 2:
        raise ValueError("config.size must be [width, height]")
    logical_size = (int(logical_size[0]), int(logical_size[1]))

    center = tuple(config["center"])
    zoom = int(config.get("zoom", 7))
    scale = int(config.get("scale", 2))
    temp_path = output_path.with_suffix(".staticmap.tmp.png")
    base = amap_get_image(
        {
            "location": f"{float(center[0]):.6f},{float(center[1]):.6f}",
            "zoom": str(zoom),
            "size": f"{logical_size[0]}*{logical_size[1]}",
            "scale": str(scale),
            "traffic": str(config.get("traffic", 0)),
        },
        temp_path=temp_path,
    ).convert("RGBA")
    draw = ImageDraw.Draw(base, "RGBA")
    project = make_projector((float(center[0]), float(center[1])), zoom, base.size, logical_size)

    route_width = int(config.get("route_width", 8))
    route_alpha = int(config.get("route_alpha", 150))
    points = build_points(config)

    for route in config.get("routes", []):
        color = str(route.get("color", "#2563EB"))
        codes = [str(code) for code in route["codes"]]
        for origin, dest in zip(codes, codes[1:]):
            key = f"{origin}-{dest}"
            if key in route_data:
                draw_route(draw, project, route_data[key], color, width=route_width, alpha=route_alpha)

    marker_size = int(config.get("marker_size", 21))
    label_size = int(config.get("label_size", 19))
    for code in config.get("marker_order", points.keys()):
        if str(code) in points:
            draw_marker(draw, project, points[str(code)], marker_size=marker_size, label_size=label_size)

    draw_header(draw, str(config.get("title", "")), str(config.get("subtitle", "")), base.size[0])
    draw_panel(draw, config.get("panel", {}), base.size)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(output_path, "PNG", optimize=True)
    return output_path


def build_points(config: dict[str, Any]) -> dict[str, Point]:
    points: dict[str, Point] = {}
    origin = config.get("origin")
    if origin:
        parsed = parse_point(origin, default_color=str(origin.get("color", "#111827")))
        points[parsed.code] = parsed
    for raw in config.get("points", []):
        parsed = parse_point(raw, default_color=str(raw.get("color", "#2563EB")))
        points[parsed.code] = parsed
    return points


def route_summary(route: dict[str, Any]) -> str:
    km = route["distance_m"] / 1000
    hours = route["duration_s"] / 3600
    return f"{km:.0f}km / {hours:.1f}h"


def main() -> None:
    parser = argparse.ArgumentParser(description="Draw an annotated Amap static map with Amap driving polyline routes.")
    parser.add_argument("--config", required=True, help="JSON config path, or '-' to read JSON from stdin.")
    parser.add_argument("--output", required=True, help="Output PNG path.")
    parser.add_argument("--route-data", help="Optional route cache JSON path.")
    parser.add_argument("--refresh-routes", action="store_true", help="Refresh Amap driving routes even when cache exists.")
    parser.add_argument("--strategy", default="0", help="Amap driving strategy. Default: 0.")
    args = parser.parse_args()

    config = read_config(args.config)
    points = build_points(config)
    route_data_path = Path(args.route_data) if args.route_data else None
    route_data = load_or_fetch_routes(points, config.get("routes", []), route_data_path, args.refresh_routes, strategy=args.strategy)
    output = compose_map(config, route_data, Path(args.output))

    summary = {
        "output": str(output),
        "route_data": str(route_data_path) if route_data_path else None,
        "segments": {key: route_summary(value) for key, value in route_data.items()},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
