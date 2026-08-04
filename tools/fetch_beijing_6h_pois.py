import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path


AMAP_KEY = os.environ.get("AMAP_WEB_SERVICE_KEY")

QUERIES = [
    ("丰宁坝上大滩镇", "承德"),
    ("千松坝国家森林公园", "承德"),
    ("京北第一天路", "承德"),
    ("张北草原天路桦皮岭入口", "张家口"),
    ("草原天路野狐岭入口", "张家口"),
    ("崇礼太舞滑雪小镇", "张家口"),
    ("沽源闪电湖", "张家口"),
    ("滦河神韵风景区", "张家口"),
    ("蔚县茶山村", "张家口"),
    ("暖泉古镇", "张家口"),
    ("大同火山群国家地质公园", "大同"),
    ("大同土林", "大同"),
    ("金山岭长城", "承德"),
    ("雾灵山国家级自然保护区", "承德"),
    ("白石山世界地质公园", "保定"),
    ("百花山自然风景区", "北京"),
    ("东灵山风景区", "北京"),
]


def fetch_poi(keyword: str, city: str) -> dict:
    params = {
        "key": AMAP_KEY,
        "keywords": keyword,
        "city": city,
        "citylimit": "false",
        "offset": "5",
        "page": "1",
        "extensions": "base",
    }
    url = "https://restapi.amap.com/v3/place/text?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.load(response)


def main() -> None:
    if not AMAP_KEY:
        raise SystemExit("AMAP_WEB_SERVICE_KEY is not set")

    out_dir = Path("output/maps")
    out_dir.mkdir(parents=True, exist_ok=True)
    all_results = {}

    for keyword, city in QUERIES:
        data = fetch_poi(keyword, city)
        all_results[keyword] = data
        print(f"\nQUERY {keyword} / {city}: status={data.get('status')} info={data.get('info')} count={data.get('count')}")
        for poi in data.get("pois", [])[:5]:
            print(
                " - {name} | {pname}{cityname}{adname} | {location} | {address}".format(
                    name=poi.get("name"),
                    pname=poi.get("pname", ""),
                    cityname=poi.get("cityname", ""),
                    adname=poi.get("adname", ""),
                    location=poi.get("location"),
                    address=poi.get("address"),
                )
            )
        time.sleep(0.7)

    (out_dir / "beijing_6h_poi_search.json").write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
