# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import math
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "maps"
DATA_PATH = OUT_DIR / "beijing_6h_route_weather.json"
LIGHT_POLLUTION_IMAGE = OUT_DIR / "Asia2025_lightpollution.png"
AMAP_KEY = os.environ.get("AMAP_WEB_SERVICE_KEY")

BASE_FONT = Path(r"C:\Windows\Fonts\msyh.ttc")
BOLD_FONT = Path(r"C:\Windows\Fonts\msyhbd.ttc")

WINDOW_START = "2026-08-12T20:00"
WINDOW_END = "2026-08-13T05:00"


@dataclass(frozen=True)
class Place:
    code: str
    name: str
    lon: float
    lat: float
    group: str
    foreground: str
    light: str
    xhs_signal: str
    xhs_url: str
    lodging: str
    food: str
    caveat: str
    foreground_score: float
    light_score: float
    logistics_score: float


BEIJING = Place(
    "京",
    "北京",
    116.397428,
    39.909230,
    "start",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    0,
    0,
    0,
)


def xhs_search_url(keyword: str) -> str:
    return "https://www.xiaohongshu.com/search_result?keyword=" + urllib.parse.quote(keyword) + "&source=web_explore_feed&type=51"


PLACES = [
    Place(
        "1",
        "上都湖",
        116.262055,
        42.599649,
        "north",
        "湖岸、蒙古包、孤树、草坡，16mm 可做湖面+北天广角。",
        "很暗，远离正蓝旗镇和湖边营地灯后表现好。",
        "小红书可见“上都湖银河”“星空与一棵树”“上都湖星空住宿”等笔记，实拍信号强。",
        xhs_search_url("上都湖 星空 银河"),
        "优先住正蓝旗/上都镇或湖边合规营地；湖边住宿旺季要提前确认热水、停车和夜间灯光。",
        "正蓝旗补给更稳；湖边多为民宿/牧家乐，夜里基本没有热食。",
        "湖边草场和湿地不要硬闯；先白天踩点，确认是否属于私人草场或景区管理区。",
        5,
        5,
        3.5,
    ),
    Place(
        "2",
        "元上都遗址外缘",
        116.186575,
        42.361721,
        "north",
        "遗址轮廓、草原地平线，文化前景强。",
        "很暗，但应避开游客中心和镇区方向。",
        "和上都湖笔记经常联动出现，更多适合作为上都湖周边机动点。",
        xhs_search_url("元上都 星空 银河"),
        "住正蓝旗最方便；不要把住宿押在遗址周边。",
        "正蓝旗县城餐饮选择明显好于湖边。",
        "严格只取外围合法道路/停车区，夜间不要进入遗址保护区。",
        4,
        5,
        3.5,
    ),
    Place(
        "3",
        "多伦湖",
        116.660941,
        42.197453,
        "north",
        "湖岸、湿地、草坡、观景平台，适合拍湖岸流星和银河。",
        "很暗，县城灯在局部方向有影响。",
        "小红书可见“多伦越野捡玛瑙拍银河”“多伦湖观星/日落”等信号。",
        xhs_search_url("多伦湖 星空 银河"),
        "多伦县住宿和补给比湖边更稳；湖边住宿需提前问夜间进出。",
        "县城餐饮选择较多，湖边夜间补给弱。",
        "湖区夜间风大、湿气重，注意镜头结露；部分景区道路夜间可能受限。",
        4,
        5,
        4,
    ),
    Place(
        "4",
        "乌兰哈达火山/G208",
        113.122579,
        41.555532,
        "ulanchabu",
        "火山锥、火山口剪影、公路、荒野地平线，前景辨识度极高。",
        "很暗，但热门火山口、营地和车灯会显著污染局部画面。",
        "小红书可见“乌兰察布G208银河”“火山口银河”“新手观星拍摄”等大量近期笔记。",
        xhs_search_url("乌兰哈达火山 星空 银河"),
        "住察右后旗白音察干镇最稳；也可住火山营地但要问灯光和夜间车流。",
        "白音察干镇吃饭补给方便；火山核心区夜间补给弱。",
        "不要在火山口边缘夜间乱走；避开 5/6 号火山核心区车灯，优先外缘和 G208 北向。",
        5,
        5,
        3.5,
    ),
    Place(
        "5",
        "辉腾锡勒/黄花沟",
        112.537638,
        41.130892,
        "ulanchabu",
        "草原、风车、山梁，适合风电剪影和草坡。",
        "较暗，但景区/住宿灯较多。",
        "小红书上草原星空信号存在，但这次更适合作为乌兰哈达西侧天气转好备选。",
        xhs_search_url("辉腾锡勒 星空 银河"),
        "黄花沟/辉腾锡勒周边住宿多，但夜间灯光不可控；也可住察右中旗。",
        "景区和镇上旺季餐饮够用，夜间补给弱。",
        "8 月草原夜风大，景区夜间通行和停车点要提前电话确认。",
        4,
        4,
        3,
    ),
    Place(
        "6",
        "丰宁坝上大滩",
        115.988194,
        41.601121,
        "north",
        "草原、马场、木栅栏、蒙古包、孤树，宽广易构图。",
        "偏暗，离大滩镇和住宿灯远一点即可明显改善。",
        "小红书可见“丰宁坝上银河实拍”“北京周边看银河”“拍银河看这一篇”等笔记。",
        xhs_search_url("丰宁坝上 星空 银河"),
        "大滩镇住宿密集，民宿/度假村多，适合第一次租车夜拍。",
        "大滩镇餐饮和超市方便，夜拍前吃饭补给最省心。",
        "很多草场是私人区域，不要压草地；旺季车灯多，机位要离镇区和营地远。",
        4,
        4,
        5,
    ),
    Place(
        "7",
        "千松坝/京北第一天路",
        116.217993,
        41.548671,
        "north",
        "山脊、松林、草坡、观景台，前景层次比大滩更好。",
        "偏暗，但景区入口和住宿灯会影响。",
        "小红书有“丰宁坝上看星星绝佳地点”“英仙座流星雨”等相关笔记，常和大滩联动。",
        xhs_search_url("千松坝 星空 银河"),
        "住大滩镇最稳；不要指望深夜在景区内找住宿或补给。",
        "大滩镇解决晚饭和水，进山前备足热饮。",
        "景区道路夜间是否开放不确定，必须白天踩点并确认可停车/可进入。",
        4,
        4,
        3.5,
    ),
    Place(
        "8",
        "张北草原天路/桦皮岭",
        115.400771,
        41.272936,
        "northwest",
        "公路 S 弯、风车、草坡、山脊，适合流星+道路前景。",
        "中等偏暗，风车/民宿/车灯会污染局部。",
        "小红书可见“张北草原天路的星空”“草原天路拍星空攻略”“北京3h怒拍银河”等近期笔记。",
        xhs_search_url("张北草原天路 星空 银河"),
        "可住张北县城、崇礼或天路沿线民宿；夜间进出要问停车和路况。",
        "县城/崇礼吃饭稳，天路沿线夜间补给弱。",
        "草原天路夜间车灯、弯道和牲畜风险都高，不建议边开边找点；日落前定机位。",
        4,
        3.5,
        4,
    ),
    Place(
        "9",
        "崇礼太舞/翠云山",
        115.448069,
        40.887507,
        "northwest",
        "山地、滑雪小镇、山脊、缆车/建筑剪影，前景现代感强。",
        "中等，度假区灯光明显，需离小镇核心远一点。",
        "小红书可见“崇礼观星最佳地点”“太舞小镇看星空”“崇礼能看到银河吗”等搜索信号。",
        xhs_search_url("崇礼 太舞 星空 银河"),
        "住宿最稳，太舞/崇礼酒店多，适合天气不确定时机动。",
        "餐饮丰富，夜间回酒店恢复体力容易。",
        "暗度不如坝上/茶山/上都湖；更像舒适备选，而不是追求极限暗夜。",
        3,
        3,
        5,
    ),
    Place(
        "10",
        "沽源闪电湖",
        115.801458,
        41.652305,
        "north",
        "湖面、湿地、草原、木栈道，流星雨画面会比较柔和。",
        "偏暗，湖边营地灯和车灯需规避。",
        "小红书可见“沽源县拍星空的地方”“闪电湖露营/拍星空”等搜索信号。",
        xhs_search_url("沽源闪电湖 星空 银河"),
        "住沽源县城或湖边合规营地；湖边住宿提前确认夜间进出。",
        "县城吃饭方便，湖边适合提前带水和干粮。",
        "湿气、蚊虫、镜头结露是核心问题；湖边风大，三脚架要压稳。",
        4,
        4.5,
        4,
    ),
    Place(
        "11",
        "滦河神韵",
        115.788080,
        41.773846,
        "north",
        "湿地河湾、草原曲线，适合做地景轮廓。",
        "偏暗，附近村镇灯光较少。",
        "小红书相关词更多和闪电湖、沽源观星联动，单点星空笔记少于闪电湖。",
        xhs_search_url("滦河神韵 星空 银河"),
        "住沽源县城更稳；景区夜间管理要提前确认。",
        "餐饮依赖沽源县城。",
        "夜间入园/停车不确定，建议作为闪电湖一带的白天踩点和备用前景。",
        4,
        4.5,
        3.5,
    ),
    Place(
        "12",
        "蔚县茶山",
        114.921802,
        39.731405,
        "west",
        "高海拔山地、村落、草坡、牛群，暗夜和纵深都很强。",
        "很暗，是北京周边硬核暗夜候选。",
        "小红书可见“茶山追英仙座流星雨”“北京4小时可达茶山”“蔚县茶山银河更绝”等近期笔记。",
        xhs_search_url("蔚县茶山 星空 银河"),
        "茶山村农家院少且条件朴素，务必提前订；也可住蔚县县城但夜里往返很累。",
        "村里补给弱，蔚县县城提前吃饭并带足水和保暖。",
        "盘山路、夜路、无信号/弱信号是最大风险；不建议深夜继续找新点。",
        5,
        5,
        2.5,
    ),
    Place(
        "13",
        "暖泉古镇/西古堡",
        114.433664,
        39.800090,
        "west",
        "古堡、城墙、巷口、老建筑，文化前景非常强。",
        "中等，古镇灯和县城灯会影响，适合做前景而非极暗。",
        "小红书更多是古镇/打树花旅行笔记，星空信号弱于茶山。",
        xhs_search_url("暖泉古镇 星空 银河"),
        "暖泉和蔚县县城住宿都方便，适合和茶山做一远一近组合。",
        "古镇餐饮方便，夜拍前补给容易。",
        "夜间城墙/古堡机位需确认开放和管理，不要进入居民区打扰住户。",
        5,
        3.5,
        4.5,
    ),
    Place(
        "14",
        "大同火山群",
        113.654338,
        40.078549,
        "shanxi",
        "火山锥、荒坡、停车点、火山口剪影，前景强且不俗套。",
        "中等偏暗，东南侧大同市和云州灯光需避开构图方向。",
        "小红书可见“大同火山群星空纯享”“狼窝山找搭子看银河”“大同火山群观星”等信号。",
        xhs_search_url("大同火山群 星空 银河"),
        "住大同市区/云州区最稳，舒适度高；火山附近住宿少。",
        "大同市区餐饮最稳，火山附近夜间基本无补给。",
        "景区夜间可达性要提前确认；火山口边缘夜间行动危险，建议取外围路侧/停车区。",
        5,
        3.5,
        4,
    ),
    Place(
        "15",
        "大同土林",
        113.474297,
        39.954032,
        "shanxi",
        "土柱、沟壑、低角度前景，画面很有电影感。",
        "中等偏暗，但离大同城区较近。",
        "小红书有“土林星空”信号，但搜索里会混入云南元谋土林，需要以大同本地笔记核实。",
        xhs_search_url("大同土林 星空 银河"),
        "住大同市区最稳，土林周边不建议压住宿。",
        "大同市区餐饮好，土林附近夜间补给弱。",
        "景区夜间大概率有管理限制；若不能入园，只作为日落前景或外侧备用。",
        5,
        3.5,
        4,
    ),
    Place(
        "16",
        "金山岭长城",
        117.248826,
        40.697879,
        "east",
        "长城城墙、敌楼、山脊，前景极强。",
        "中等，京津冀光害和景区灯光存在。",
        "小红书可见“古长城遇上银河”“金山岭长城星轨/拍星空攻略”等笔记。",
        xhs_search_url("金山岭长城 星空 银河"),
        "景区周边酒店/客栈较多，离北京近，适合天气临时转好。",
        "景区外和服务区补给方便。",
        "最大不确定是夜间入园/拍摄许可；没有许可时不建议把它作为唯一方案。",
        5,
        3,
        4,
    ),
    Place(
        "17",
        "雾灵山",
        117.498299,
        40.552530,
        "east",
        "山顶、云海、森林线、日出，适合星空+云海组合。",
        "中等偏暗，东侧湿度和云雾概率偏高。",
        "小红书可见“北大山观星台”“雾灵山银河/云海日出”等笔记。",
        xhs_search_url("雾灵山 星空 银河"),
        "兴隆/雾灵山镇住宿可选，山上住宿和夜间通行要确认。",
        "镇上餐饮尚可，山里夜间无补给。",
        "湿度、雾、夜间道路和景区管理风险都高；适合天气明确晴朗时的近程备选。",
        4,
        3.5,
        3,
    ),
    Place(
        "18",
        "白石山/涞源",
        114.702724,
        39.216782,
        "west",
        "山体、古长城、村落轮廓，西南线前景不错。",
        "偏暗，涞源县城方向需避开。",
        "小红书搜索里有“涞源古长城杏花银河”“北京最近2级区看银河”等相关信号。",
        xhs_search_url("白石山 星空 银河"),
        "住涞源县城最稳，山下民宿也可但要问停车和灯光。",
        "涞源县城餐饮补给方便。",
        "白石山景区夜间入园限制较大，推荐找景区外合法道路/村道前景，不夜爬。",
        4,
        4,
        4,
    ),
    Place(
        "19",
        "东灵山/百花山",
        115.494375,
        40.016715,
        "west",
        "近郊高山、山脊、草甸，适合做近程保底。",
        "中等，受北京西部光污染影响，暗度不如茶山/坝上。",
        "小红书可见“东灵山保姆级教程”“百花山看银河攻略”“夜爬星空日出”等笔记。",
        xhs_search_url("东灵山 星空 银河"),
        "可住门头沟/斋堂/洪水口周边，条件一般；适合短线不熬大车程。",
        "沿途镇村补给有限，出城前备好水和热食。",
        "夜爬和保护区管理风险高，若没有成熟户外经验，不建议作为主方案。",
        3,
        3,
        3,
    ),
]

GROUP_COLORS = {
    "start": "#111827",
    "north": "#E76F00",
    "ulanchabu": "#2563EB",
    "northwest": "#0D9488",
    "west": "#7C3AED",
    "shanxi": "#DC2626",
    "east": "#15803D",
}

GROUP_NAMES = {
    "north": "北线草原湖泊",
    "ulanchabu": "乌兰察布火山线",
    "northwest": "张北/崇礼机动线",
    "west": "西线山地暗夜",
    "shanxi": "山西火山土林线",
    "east": "东北长城山地线",
}

LP_ZONE_INFO = {
    "0": {"lpi": "<0.01", "mpsas": "22.00-21.99", "bortle": "1"},
    "1a": {"lpi": "0.01-0.06", "mpsas": "21.99-21.93", "bortle": "1-2"},
    "1b": {"lpi": "0.06-0.11", "mpsas": "21.93-21.89", "bortle": "2"},
    "2a": {"lpi": "0.11-0.19", "mpsas": "21.89-21.81", "bortle": "2-3"},
    "2b": {"lpi": "0.19-0.33", "mpsas": "21.81-21.69", "bortle": "3"},
    "3a": {"lpi": "0.33-0.58", "mpsas": "21.69-21.51", "bortle": "3-4"},
    "3b": {"lpi": "0.58-1.00", "mpsas": "21.51-21.25", "bortle": "4"},
    "4a": {"lpi": "1.00-1.73", "mpsas": "21.25-20.91", "bortle": "4-5"},
    "4b": {"lpi": "1.73-3.00", "mpsas": "20.91-20.49", "bortle": "5"},
    "5a": {"lpi": "3.00-5.20", "mpsas": "20.49-20.02", "bortle": "5-6"},
    "5b": {"lpi": "5.20-9.00", "mpsas": "20.02-19.50", "bortle": "6"},
    "6a": {"lpi": "9.00-15.59", "mpsas": "19.50-18.95", "bortle": "6-7"},
    "6b": {"lpi": "15.59-27.00", "mpsas": "18.95-18.38", "bortle": "7"},
    "7a": {"lpi": "27.00-46.77", "mpsas": "18.38-17.80", "bortle": "8"},
    "7b": {"lpi": ">46.77", "mpsas": "<17.80", "bortle": "9"},
}

LP_ZONE_COLORS = {
    (0, 0, 0): "0",
    (34, 34, 34): "1a",
    (66, 66, 66): "1b",
    (20, 47, 114): "2a",
    (33, 84, 216): "2b",
    (15, 87, 20): "3a",
    (31, 161, 42): "3b",
    (110, 100, 30): "4a",
    (184, 166, 37): "4b",
    (191, 100, 30): "5a",
    (253, 150, 80): "5b",
    (251, 90, 73): "6a",
    (251, 153, 138): "6b",
    (160, 160, 160): "7a",
    (242, 242, 242): "7b",
}

LP_FALLBACK_ZONES = {
    "1": "1a",
    "2": "2a",
    "3": "3a",
    "4": "2b",
    "5": "3a",
    "6": "3a",
    "7": "2a",
    "8": "2b",
    "9": "4b",
    "10": "3b",
    "11": "3a",
    "12": "2b",
    "13": "4a",
    "14": "4b",
    "15": "5a",
    "16": "3b",
    "17": "3b",
    "18": "3b",
    "19": "3b",
}


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
    with urllib.request.urlopen(url, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def amap_get_image(params: dict) -> Image.Image:
    params = dict(params)
    params["key"] = AMAP_KEY
    url = "https://restapi.amap.com/v3/staticmap?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as response:
        raw = response.read()
    temp_path = OUT_DIR / "_last_beijing_6h_staticmap.png"
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


def fetch_route(dest: Place) -> dict:
    data = amap_get_json(
        "https://restapi.amap.com/v3/direction/driving",
        {
            "origin": f"{BEIJING.lon:.6f},{BEIJING.lat:.6f}",
            "destination": f"{dest.lon:.6f},{dest.lat:.6f}",
            "extensions": "base",
            "strategy": "0",
        },
    )
    if data.get("status") != "1":
        raise RuntimeError(f"Amap route failed Beijing->{dest.name}: {data}")
    path = data["route"]["paths"][0]
    coords: list[tuple[float, float]] = []
    for step in path["steps"]:
        step_points = parse_polyline(step["polyline"])
        if coords and step_points and coords[-1] == step_points[0]:
            coords.extend(step_points[1:])
        else:
            coords.extend(step_points)
    return {
        "destination": dest.code,
        "distance_m": int(path["distance"]),
        "duration_s": int(path["duration"]),
        "coords": coords,
    }


def fetch_open_meteo() -> dict[str, dict]:
    params = {
        "latitude": ",".join(f"{p.lat:.6f}" for p in PLACES),
        "longitude": ",".join(f"{p.lon:.6f}" for p in PLACES),
        "hourly": "cloud_cover,precipitation_probability,temperature_2m,wind_gusts_10m,visibility",
        "timezone": "Asia/Shanghai",
        "start_date": "2026-08-12",
        "end_date": "2026-08-13",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as response:
        raw = json.loads(response.read().decode("utf-8"))
    series = raw if isinstance(raw, list) else [raw]
    result: dict[str, dict] = {}
    for place, item in zip(PLACES, series):
        hourly = item.get("hourly", {})
        times = hourly.get("time", [])
        idx = [i for i, t in enumerate(times) if WINDOW_START <= t <= WINDOW_END]
        if not idx:
            result[place.code] = {"available": False}
            continue
        clouds = [hourly["cloud_cover"][i] for i in idx if hourly["cloud_cover"][i] is not None]
        precip = [hourly["precipitation_probability"][i] for i in idx if hourly["precipitation_probability"][i] is not None]
        temps = [hourly["temperature_2m"][i] for i in idx if hourly["temperature_2m"][i] is not None]
        gusts = [hourly["wind_gusts_10m"][i] for i in idx if hourly["wind_gusts_10m"][i] is not None]
        vis = [hourly["visibility"][i] for i in idx if hourly["visibility"][i] is not None]
        avg_cloud = sum(clouds) / len(clouds) if clouds else None
        max_cloud = max(clouds) if clouds else None
        max_precip = max(precip) if precip else None
        rating = "?"
        if avg_cloud is not None:
            if avg_cloud < 25 and (max_precip is None or max_precip <= 25):
                rating = "A"
            elif avg_cloud < 45 and (max_precip is None or max_precip <= 35):
                rating = "B"
            elif avg_cloud < 70:
                rating = "C"
            else:
                rating = "D"
        result[place.code] = {
            "available": True,
            "avg_cloud": round(avg_cloud, 1) if avg_cloud is not None else None,
            "min_cloud": min(clouds) if clouds else None,
            "max_cloud": max_cloud,
            "max_precip_prob": max_precip,
            "temp_min": round(min(temps), 1) if temps else None,
            "temp_max": round(max(temps), 1) if temps else None,
            "gust_max": round(max(gusts), 1) if gusts else None,
            "visibility_min_km": round(min(vis) / 1000, 1) if vis else None,
            "rating": rating,
        }
    return result


def nearest_lp_zone(rgb: tuple[int, int, int]) -> str:
    color = min(LP_ZONE_COLORS, key=lambda c: sum((rgb[i] - c[i]) ** 2 for i in range(3)))
    return LP_ZONE_COLORS[color]


def sample_light_pollution() -> dict[str, dict]:
    if not LIGHT_POLLUTION_IMAGE.exists():
        zones = LP_FALLBACK_ZONES
    else:
        Image.MAX_IMAGE_PIXELS = None
        image = Image.open(LIGHT_POLLUTION_IMAGE).convert("RGB")
        zones = {}
        for place in PLACES:
            x = int((place.lon - 60) * 120)
            y = int((75 - place.lat) * 120)
            x = min(max(x, 0), image.width - 1)
            y = min(max(y, 0), image.height - 1)
            zones[place.code] = nearest_lp_zone(image.getpixel((x, y)))

    result = {}
    for code, zone in zones.items():
        info = LP_ZONE_INFO[zone]
        result[code] = {
            "zone": zone,
            "lpi": info["lpi"],
            "mpsas": info["mpsas"],
            "approx_bortle": info["bortle"],
        }
    return result


def load_or_fetch_data(force: bool = False) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    expected_codes = {p.code for p in PLACES}
    if DATA_PATH.exists() and not force:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if "light_pollution" not in data or expected_codes - set(data.get("light_pollution", {}).keys()):
            data["light_pollution"] = sample_light_pollution()
            DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        if (
            expected_codes <= set(data.get("routes", {}).keys())
            and expected_codes <= set(data.get("weather", {}).keys())
            and expected_codes <= set(data.get("light_pollution", {}).keys())
        ):
            return data

    routes = {}
    for place in PLACES:
        routes[place.code] = fetch_route(place)
        time.sleep(0.45)
    weather = fetch_open_meteo()
    data = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "weather_window": f"{WINDOW_START} - {WINDOW_END} Asia/Shanghai",
        "routes": routes,
        "weather": weather,
        "light_pollution": sample_light_pollution(),
    }
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


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


def draw_route(draw: ImageDraw.ImageDraw, project, route: dict, color: str, width: int, alpha: int = 120):
    pixels = [project(lon, lat) for lon, lat in route["coords"]]
    pixels = [(x, y) for x, y in pixels if -200 <= x <= 2300 and -200 <= y <= 1700]
    if len(pixels) >= 2:
        draw.line(pixels, fill=hex_to_rgba(color, alpha), width=width, joint="curve")


def text_size(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=text_font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_marker(
    draw: ImageDraw.ImageDraw,
    project,
    place: Place,
    color: str,
    label: str,
    dx: int = 18,
    dy: int = -42,
    compact: bool = False,
):
    x, y = project(place.lon, place.lat)
    r = 21 if len(place.code) <= 1 else 23
    draw.ellipse((x - r, y - r, x + r, y + r), fill=hex_to_rgba(color, 245), outline=(255, 255, 255, 255), width=4)
    code_font = font(21 if len(place.code) <= 1 else 17, bold=True)
    cw, ch = text_size(draw, place.code, code_font)
    draw.text((x - cw / 2, y - ch / 2 - 1), place.code, fill=(255, 255, 255, 255), font=code_font)

    label_font = font(18 if compact else 20, bold=True)
    lw, lh = text_size(draw, label, label_font)
    lx, ly = x + dx, y + dy
    pad_x, pad_y = 8, 5
    draw.rounded_rectangle(
        (lx - pad_x, ly - pad_y, lx + lw + pad_x, ly + lh + pad_y),
        radius=9,
        fill=(255, 255, 255, 232),
        outline=hex_to_rgba(color, 235),
        width=2,
    )
    draw.text((lx, ly), label, fill=(15, 23, 42, 255), font=label_font)


def draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str, w: int):
    draw.rounded_rectangle((28, 24, w - 28, 116), radius=16, fill=(255, 255, 255, 238), outline=(203, 213, 225, 255), width=2)
    draw.text((52, 36), title, fill=(15, 23, 42, 255), font=font(32, bold=True))
    draw.text((52, 80), subtitle, fill=(71, 85, 105, 255), font=font(19))


def draw_panel(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, title: str, rows: Sequence[tuple[str, str]]):
    row_h = 31
    h = 78 + row_h * len(rows)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=(255, 255, 255, 238), outline=(148, 163, 184, 255), width=2)
    draw.text((x + 20, y + 16), title, fill=(15, 23, 42, 255), font=font(25, bold=True))
    yy = y + 56
    for text, color in rows:
        draw.text((x + 22, yy), text, fill=hex_to_rgba(color), font=font(18, bold=True))
        yy += row_h


def route_summary(route: dict) -> tuple[float, float]:
    return route["distance_m"] / 1000, route["duration_s"] / 3600


def weather_label(weather: dict) -> str:
    if not weather.get("available"):
        return "天气待更新"
    return f"{weather['rating']} 云{weather['avg_cloud']:.0f}%"


def lp_label(lp: dict) -> str:
    return f"LP{lp['zone']}"


def lp_long_label(lp: dict) -> str:
    return f"LP {lp['zone']}，LPI {lp['lpi']}，约 Bortle {lp['approx_bortle']}，{lp['mpsas']} mpsas"


def score_place(place: Place, route: dict, weather: dict) -> float:
    weather_score = {"A": 8, "B": 6, "C": 2, "D": -4}.get(weather.get("rating"), 0)
    _, hours = route_summary(route)
    drive_penalty = max(0, hours - 5.5) * 0.8
    cloud_penalty = 0
    if weather.get("available") and weather.get("rating") == "D" and weather.get("avg_cloud", 0) >= 85:
        cloud_penalty = 6
    precip_penalty = 2 if weather.get("available") and weather.get("max_precip_prob", 0) >= 45 else 0
    return round(
        weather_score * 2.0
        + place.foreground_score * 1.2
        + place.light_score * 1.4
        + place.logistics_score
        - drive_penalty
        - cloud_penalty
        - precip_penalty,
        1,
    )


LABEL_OFFSETS = {
    "京": (20, -54),
    "1": (24, -66),
    "2": (-205, -48),
    "3": (26, 18),
    "4": (-226, -64),
    "5": (-238, 14),
    "6": (-286, -58),
    "7": (28, 16),
    "8": (-248, -20),
    "9": (24, 18),
    "10": (26, -78),
    "11": (28, -6),
    "12": (-206, -60),
    "13": (-214, 16),
    "14": (-218, -58),
    "15": (-210, 14),
    "16": (24, -54),
    "17": (24, 14),
    "18": (-210, -58),
    "19": (-214, -54),
}


def compose_map(data: dict, out_name: str, with_routes: bool = True) -> Path:
    logical_size = (1024, 768)
    center = (115.55, 40.85)
    zoom = 7
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

    if with_routes:
        route_codes = ["1", "3", "4", "6", "8", "10", "12", "14", "16", "18", "19"]
        for code in route_codes:
            place = next(p for p in PLACES if p.code == code)
            draw_route(draw, project, data["routes"][code], GROUP_COLORS[place.group], width=7, alpha=128)

    for place in PLACES:
        color = GROUP_COLORS[place.group]
        lp = data["light_pollution"][place.code]
        label = f"{place.code} {place.name} {lp_label(lp)}"
        draw_marker(draw, project, place, color, label, *LABEL_OFFSETS.get(place.code, (18, -42)), compact=True)
    draw_marker(draw, project, BEIJING, GROUP_COLORS["start"], "北京出发", *LABEL_OFFSETS["京"], compact=True)

    draw_header(
        draw,
        "2026 英仙座流星雨：北京周边 2-6 小时候选机位",
        "高德底图/驾车路线 + Open-Meteo 8/12 20:00-8/13 05:00 云量；编号见补充文档",
        base.size[0],
    )
    rows = [
        ("橙：北线草原湖泊  上都湖/多伦/丰宁/沽源", GROUP_COLORS["north"]),
        ("蓝：乌兰察布线  乌兰哈达/G208/辉腾锡勒", GROUP_COLORS["ulanchabu"]),
        ("青：张北/崇礼机动线  天路/太舞", GROUP_COLORS["northwest"]),
        ("紫：西线山地暗夜  蔚县茶山/暖泉/白石山/东灵山", GROUP_COLORS["west"]),
        ("红：山西火山土林线  大同火山群/土林", GROUP_COLORS["shanxi"]),
        ("绿：东北长城山地线  金山岭/雾灵山", GROUP_COLORS["east"]),
        ("LP：Light Pollution Zone，数字越大越亮；b 比 a 更亮", "#334155"),
    ]
    panel_h = 78 + 31 * len(rows)
    draw_panel(draw, 34, base.size[1] - panel_h - 28, 742, "路线分组", rows)
    out = OUT_DIR / out_name
    base.convert("RGB").save(out, "PNG", optimize=True)
    return out


def compose_rank_map(data: dict, out_name: str) -> Path:
    logical_size = (1024, 768)
    center = (115.6, 40.9)
    zoom = 7
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

    ranked = sorted(
        PLACES,
        key=lambda p: score_place(p, data["routes"][p.code], data["weather"][p.code]),
        reverse=True,
    )
    top_codes = [p.code for p in ranked if data["weather"][p.code].get("rating") in {"A", "B", "C"}][:8]
    for place in [p for p in ranked if p.code in top_codes]:
        draw_route(draw, project, data["routes"][place.code], GROUP_COLORS[place.group], width=9, alpha=155)
    for place in PLACES:
        color = GROUP_COLORS[place.group]
        weather = data["weather"][place.code]
        lp = data["light_pollution"][place.code]
        label = f"{place.code} {place.name} {weather_label(weather)} {lp_label(lp)}"
        if place.code in top_codes:
            label = "★ " + label
        draw_marker(draw, project, place, color, label, *LABEL_OFFSETS.get(place.code, (18, -42)), compact=True)
    draw_marker(draw, project, BEIJING, GROUP_COLORS["start"], "北京出发", *LABEL_OFFSETS["京"], compact=True)
    draw_header(
        draw,
        "候选点天气与优先级图",
        "星号为综合分前 8：综合考虑车程、云量、前景、暗度、住宿补给；天气需 T-3/T-1 复核",
        base.size[0],
    )
    rows = []
    panel_places = [p for p in ranked if p.code in top_codes]
    if len(panel_places) < 8:
        panel_places.extend([p for p in ranked if p.code not in top_codes][: 8 - len(panel_places)])
    for i, place in enumerate(panel_places[:8], 1):
        route = data["routes"][place.code]
        km, hours = route_summary(route)
        weather = data["weather"][place.code]
        lp = data["light_pollution"][place.code]
        prefix = "可冲" if place.code in top_codes else "翻盘备"
        rows.append((f"{i}. {prefix} {place.code} {place.name} {km:.0f}km/{hours:.1f} {weather_label(weather)} {lp_label(lp)}", GROUP_COLORS[place.group]))
    draw_panel(draw, 34, base.size[1] - 342, 1000, "当前优先级", rows)
    out = OUT_DIR / out_name
    base.convert("RGB").save(out, "PNG", optimize=True)
    return out


def markdown_table(data: dict) -> str:
    ranked = sorted(
        PLACES,
        key=lambda p: score_place(p, data["routes"][p.code], data["weather"][p.code]),
        reverse=True,
    )
    rows = [
        "| 排名 | 编号 | 地点 | 车程 | 8/12 夜天气 | 光污染等级 | 光污染/暗度 | 前景 | 综合建议 |",
        "|---:|---:|---|---:|---|---|---|---|---|",
    ]
    for i, place in enumerate(ranked, 1):
        route = data["routes"][place.code]
        weather = data["weather"][place.code]
        lp = data["light_pollution"][place.code]
        km, hours = route_summary(route)
        wx = (
            f"{weather['rating']}，均云{weather['avg_cloud']}%，"
            f"云{weather['min_cloud']}-{weather['max_cloud']}%，"
            f"降水概率峰值{weather['max_precip_prob']}%，"
            f"{weather['temp_min']}-{weather['temp_max']}℃，阵风{weather['gust_max']}km/h"
            if weather.get("available")
            else "待更新"
        )
        rating = weather.get("rating")
        avg_cloud = weather.get("avg_cloud", 100)
        if rating in {"A", "B"} and avg_cloud < 55:
            suggestion = "主推/优先踩点"
        elif rating == "C" or (rating == "B" and avg_cloud < 70):
            suggestion = "临近天气转好可冲"
        else:
            suggestion = "仅天气翻盘备选"
        rows.append(
            f"| {i} | {place.code} | {place.name} | {km:.0f}km / {hours:.1f}h | {wx} | {lp_long_label(lp)} | {place.light} | {place.foreground} | {suggestion} |"
        )
    return "\n".join(rows)


def place_detail(place: Place, data: dict) -> str:
    route = data["routes"][place.code]
    weather = data["weather"][place.code]
    lp = data["light_pollution"][place.code]
    km, hours = route_summary(route)
    wx = (
        f"{weather['rating']} 级，平均云量 {weather['avg_cloud']}%，逐小时范围 {weather['min_cloud']}-{weather['max_cloud']}%，"
        f"降水概率峰值 {weather['max_precip_prob']}%，温度 {weather['temp_min']}-{weather['temp_max']}℃，阵风峰值 {weather['gust_max']} km/h。"
        if weather.get("available")
        else "天气待更新。"
    )
    return f"""### {place.code}. {place.name}

- 车程：北京出发约 {km:.0f} km / {hours:.1f} h（高德驾车规划静态结果；实际以 8 月 12 日出发当天实时路况为准）。
- 天气窗口：{wx}
- 小红书笔记信号：{place.xhs_signal} 关键词入口：[{place.name} 搜索]({place.xhs_url})。
- 光污染等级：{lp_long_label(lp)}。LP Zone 是天顶人工亮度模型采样，不等同于现场肉眼 Bortle；同一地点还会受地平线光穹、车灯、营地灯影响。
- 周边环境/前景：{place.foreground}
- 光污染判断：{place.light}
- 住宿：{place.lodging}
- 饮食补给：{place.food}
- 机位注意：{place.caveat}
"""


def write_markdown(data: dict, overview: Path, rank_map: Path) -> Path:
    ranked = sorted(
        PLACES,
        key=lambda p: score_place(p, data["routes"][p.code], data["weather"][p.code]),
        reverse=True,
    )
    top = [p for p in ranked if data["weather"][p.code].get("rating") in {"A", "B", "C"}][:6]
    top_lines = []
    for p in top:
        km, hours = route_summary(data["routes"][p.code])
        top_lines.append(
            f"- {p.code} {p.name}：{km:.0f}km/{hours:.1f}h，{weather_label(data['weather'][p.code])}，"
            f"{lp_label(data['light_pollution'][p.code])}，{GROUP_NAMES[p.group]}。"
        )
    if not top_lines:
        top_lines.append("- 暂无稳定可冲窗口；保留路线池，等 8 月 9 日后重新刷云量。")

    content = f"""# 2026 英仙座流星雨：北京周边 2-6 小时机位扩展

更新时间：2026-08-04  
拍摄窗口：2026-08-12 夜间至 2026-08-13 凌晨，北京时间 20:00-05:00  
硬数据来源：高德 Web Service 驾车路线/静态地图、Open-Meteo 逐小时预报、David Lorenz 2025 Light Pollution Atlas 亚洲 1/120° 栅格采样。小红书部分用于参考实拍经验和机位热度，不作为通行/开放证明。

## 先给结论

这次不只看内蒙，按“天气窗口 + 5-6 小时车程 + 前景质量 + 暗度 + 住宿补给 + 小红书实拍信号”重新排了一遍。按 2026-08-04 这版逐小时云量，当前最值得优先准备的是：

{chr(10).join(top_lines)}

重要变化：这一版预报对北线湖泊/坝上/沽源/张北/东线非常不友好，很多点在 8/12 夜间显示 D 级高云量。它们仍然值得保留为机位池，但不能按现在的天气当主方案押注。真正需要在 8 月 9 日、8 月 11 日、8 月 12 日中午连续复刷云量后再定。

我会把方案分成三类：

- 当前天气可冲：乌兰哈达/G208、大同土林、辉腾锡勒/黄花沟；大同火山群作为同线补充，但云量边缘。
- 天气转晴优先切换：上都湖/多伦湖、丰宁坝上/千松坝、沽源闪电湖/滦河神韵、蔚县茶山。
- 前景强但需许可或管理确认：金山岭、雾灵山、白石山、元上都遗址外缘、大同土林。

## 更新后的线路图

![北京周边 2-6 小时候选总览](output/maps/{overview.name})

![天气与优先级图](output/maps/{rank_map.name})

## 总表

{markdown_table(data)}

## 地点详解

{chr(10).join(place_detail(p, data) for p in PLACES)}

## 16mm f/1.8 拍摄执行建议

- 流星雨构图优先朝东北到北天开阔方向，后半夜辐射点升高后更舒服；16mm 适合把地景控制在画面下 1/4 到 1/3，别让前景太高。
- 起步参数：f/1.8，ISO 1600-3200，单张 8-13 秒；如果星点拖线明显就降到 8-10 秒，靠后期堆栈/间隔拍摄补数量。
- 流星是随机事件，固定机位连续拍比频繁换构图更重要；建议 21:30 前完成对焦和构图，23:30-03:30 连拍。
- 所有湖边/草原点都要准备镜头加热带或暖宝宝防结露；草原和山地凌晨体感会比预报温度低很多。
- 车灯是最大污染源之一，热门地点不要贴着停车场拍；找到可合法停车的位置后，步行 100-300 米往往比继续开车找点更有用。

## 小红书笔记参考方式

这次用小红书站内关键词检查了“星空/银河/机位/露营/英仙座”等组合。比较强的信号包括：

- 丰宁坝上：出现“丰宁坝上银河实拍”“北京周边看银河”“拍银河”等笔记，说明实拍样张和民宿经验都比较多。
- 张北草原天路：出现“张北草原天路的星空”“拍星空攻略”“北京3h怒拍银河”等笔记，适合做近程机动。
- 蔚县茶山：出现“茶山追英仙座流星雨”“北京4小时可达茶山”“蔚县茶山银河更绝”等笔记，暗度和前景信号强，但路况/住宿更硬核。
- 大同火山群：出现“火山群星空纯享”“狼窝山看银河”“大同火山群观星”等笔记，前景强，需核实夜间管理。
- 上都湖/乌兰哈达：两者都出现大量“银河/星空/机位”笔记，是原内蒙方案里最值得保留的两个核心方向。

出发前一天建议在小红书再搜每个候选点的“地点名 + 今天/昨晚 + 星空/银河/云量/封路/住宿”，优先看 7 天内笔记和评论区。小红书笔记里的“能进”“能露营”要按当天景区/村镇管理再确认，不要直接照搬。

## 数据说明

- 高德路线是脚本调用 Web Service 驾车路径规划得到的静态里程/时长和 polyline；出发当天一定以高德 App 实时路况为准。
- Open-Meteo 是模式预报，8 天外云量会变；8 月 9 日、8 月 11 日、8 月 12 日中午需要重刷一次。
- 光污染等级来自 David Lorenz 2025 Light Pollution Atlas 的 Light Pollution Zone。该 Atlas 页面说明数据来自 2025 年 VIIRS 夜光数据建模，分辨率大多为 1/120°；颜色含义对应 LP Zone/LPI/mpsas。作者也明确提醒：它是天顶人工亮度模型，不应直接等同 Bortle 主观目视等级。因此表格里的“约 Bortle”只用于摄影直觉参考。
- 真正到点时还要避开城镇方向、景区灯、营地灯和路过车灯；同一个 LP 等级下，朝向不同会差很多。
"""
    path = ROOT / "英仙座流星雨北京周边5-6小时机位扩展.md"
    path.write_text(content, encoding="utf-8")
    return path


def main() -> None:
    if not AMAP_KEY:
        raise RuntimeError("AMAP_WEB_SERVICE_KEY is not set")
    data = load_or_fetch_data(force=os.environ.get("REFRESH_METEOR_DATA") == "1")
    overview = compose_map(data, "meteor_amap_beijing_6h_options.png", with_routes=True)
    rank_map = compose_rank_map(data, "meteor_amap_beijing_6h_priority.png")
    md = write_markdown(data, overview, rank_map)
    print(
        json.dumps(
            {
                "overview": str(overview),
                "priority_map": str(rank_map),
                "markdown": str(md),
                "data": str(DATA_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
