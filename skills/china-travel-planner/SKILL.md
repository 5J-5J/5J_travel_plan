---
name: china-travel-planner
description: Plan China travel itineraries with current online research, especially Gaode/Amap map data for POIs, routing, travel times, opening hours, logistics, and annotated route maps using Amap static basemaps plus Amap driving-route polylines. Also use Xiaohongshu notes for recent traveler experience, food, photo spots, queues, pitfalls, and local tips. Use when the user asks for a trip plan, itinerary, travel route, destination research, city guide, budget-aware travel schedule, family/couple/friends travel plan, China domestic travel advice, route visualization, map marking, driving route overlay, or verification of attractions/restaurants/hotels/transport.
---

# China Travel Planner

## Overview

Create practical China travel plans by combining structured map/logistics data with social travel notes. Prefer current sources over memory, distinguish verified facts from recommendations, and produce an itinerary that fits the user's dates, people, destination, budget, pace, and preferences.

## First Steps

1. Extract or ask for the missing essentials: travel dates or duration, destination(s), origin if routing matters, number and type of travelers, budget, pace, interests, hotel area if known, transport preferences, dietary/accessibility constraints, and must-see or must-avoid places.
2. If the trip depends on current availability, opening hours, prices, crowding, closures, transport schedules, weather, platform notes, or policy restrictions, browse or use available connectors before planning.
3. Run `scripts/check_travel_env.py` when Gaode/Amap access or Xiaohongshu login access may be needed. Ask the user for missing credentials only when the task cannot be completed with public web search or current browser access.
4. Read `references/source-playbook.md` before doing source-heavy planning, authenticity checks, or platform-specific research.

## Source Strategy

Use Gaode/Amap first for geography and logistics:

- POI search, address disambiguation, coordinates, categories, nearby clusters, opening-hour snippets, ratings if available, and route estimates.
- Driving, public transit, walking, cycling, and taxi-distance checks.
- Spatial sanity checks: avoid plans that zigzag across a city, overload distant attractions, or ignore peak commute friction.
- Annotated map images when the user asks for route maps, marked POIs, driving route overlays, or map screenshots. Prefer `scripts/amap_route_polyline_map.py` for deterministic Amap basemap + Amap driving polyline rendering.

Use Xiaohongshu as experience evidence, not as a single source of truth:

- Search for recent notes about queues, photo spots, food quality, booking friction, scams, closures, seasonal conditions, crowding, and "避雷"/"避坑".
- Cross-check repeated claims across multiple notes and with map/official sources where possible.
- Treat influencer-heavy, old, vague, or copied notes as weak evidence.

Use official or primary sources when stakes are high:

- Scenic-area official sites/accounts for opening hours, ticket booking, closure notices, child/senior policies, and capacity limits.
- Railway/airline/metro/bus official channels for transport when exact schedules matter.
- Weather and government advisories for safety-sensitive outdoor plans.

## Planning Workflow

1. Frame the trip constraints.
   Convert user preferences into explicit planning rules: daily start/end times, maximum transit tolerance, meal style, rest needs, shopping/nightlife interest, kid/elder constraints, and budget bands.
2. Build a candidate map.
   Research attractions, restaurants, neighborhoods, hotels, and transit hubs. Group candidates by geography and opening windows.
3. Verify and score.
   Score each candidate for fit, recency of evidence, logistics, uniqueness, crowd risk, cost, and backup value. Discard places with unresolved contradictions unless clearly labeled optional.
4. Design the itinerary.
   Cluster each day by area, keep transit realistic, reserve meals near the route, add buffers, and include Plan B options for weather, closures, fatigue, or crowds.
5. Estimate budget.
   Break down transport, lodging, tickets, meals, local transfers, shopping/activities, and contingency. Label assumptions and ranges.
6. Deliver a usable plan.
   Include day-by-day schedule, addresses/areas, transit method and approximate time, booking reminders, food options, budget table, packing or prep notes, and source-confidence notes.

## Amap Route Annotation Maps

Use `scripts/amap_route_polyline_map.py` when the user asks to draw or update a map with marked places, route corridors, or driving lines. The script fetches an Amap static basemap, fetches Amap driving-route polylines for configured route segments, projects them onto the basemap, and draws labels, numbered markers, route lines, and an optional legend panel.

Requirements:

- Read `AMAP_WEB_SERVICE_KEY` from the environment.
- Use Amap/GCJ-02 coordinates from POI search or Amap geocoding whenever possible, so points, polylines, and static map tiles align.
- Ensure Python can import `PIL`/`Pillow`.

Workflow:

1. Build a JSON config with `origin`, `points`, `routes`, `center`, `zoom`, optional `title`, `subtitle`, `panel`, label offsets (`dx`, `dy`), and colors.
2. Run:

```bash
python scripts/amap_route_polyline_map.py --config map_config.json --output output/map.png --route-data output/map_routes.json
```

Use `--config -` to read JSON from stdin, and `--refresh-routes` when the route cache should be ignored.
When labels contain Chinese or other non-ASCII text on Windows/PowerShell, prefer a UTF-8 JSON file with `--config map_config.json`; stdin pipes may garble text depending on console encoding.

Minimal config shape:

```json
{
  "title": "路线图",
  "subtitle": "高德底图 + 驾车 polyline",
  "center": [116.0, 40.8],
  "zoom": 7,
  "origin": {"code": "京", "name": "北京", "lon": 116.397428, "lat": 39.909230, "label": "北京出发", "color": "#111827"},
  "points": [
    {"code": "1", "name": "目的地", "lon": 116.26, "lat": 42.60, "label": "1 目的地 5.8h", "color": "#E76F00"}
  ],
  "routes": [
    {"name": "主线", "color": "#E76F00", "codes": ["京", "1"]}
  ],
  "panel": {
    "title": "路线说明",
    "rows": [{"text": "橙：北京 -> 目的地", "color": "#E76F00"}]
  }
}
```

Validation:

- Always visually inspect the generated PNG before delivery.
- Adjust `dx`/`dy`, `center`, `zoom`, `label_size`, or panel position when labels overlap or important markers are hidden.
- State that Amap route duration and polyline are static API results and final navigation should use Amap App real-time routing on the travel day.

## Output Standards

Produce Chinese output by default unless the user requests another language.

For full itineraries, include:

- Summary: route theme, pace, total estimated budget, and best hotel area.
- Daily plan: morning/afternoon/evening blocks with estimated travel time and meal options.
- Map logic: why places are grouped together and where long transfers occur.
- Booking list: tickets, reservations, transport, hotels, and deadlines.
- Budget: low/normal/comfortable ranges when exact prices are uncertain.
- Evidence notes: cite or link key sources when browsing; say what was confirmed by Gaode, Xiaohongshu, official pages, or inference.
- Risks and backups: closures, bad weather, traffic, crowds, sold-out tickets, and alternatives.

Do not invent access to Xiaohongshu, Gaode, private accounts, API results, or live web pages. If access is blocked, state that clearly and use available alternatives.

## Credentials And Access

Never ask the user to paste secrets unless they are required for the specific task. Prefer environment variables, local credential stores, or browser sessions.

Use this credential model:

- Gaode/Amap: one Web Service API key. Read it from `AMAP_WEB_SERVICE_KEY`.
- Xiaohongshu: a user-authorized web login session, normally represented by browser state or a cookie. Read a provided cookie from `XHS_COOKIE` only when the user has explicitly authorized that use.

Recognized optional environment variables:

- `AMAP_WEB_SERVICE_KEY`: Gaode/Amap Web Service API key.
- `XHS_COOKIE`: Xiaohongshu Web login cookie for a user-authorized research session.
- `XHS_SERVICE_ENDPOINT`: Optional user-provided bridge service for Xiaohongshu search, only if the user's setup has one.
- `XHS_SERVICE_TOKEN`: Optional token for the above bridge service.

If no Xiaohongshu login cookie, browser session, or user-provided bridge is available, use browser-based search or general web search for indexed Xiaohongshu notes when accessible. Follow website terms, rate limits, and privacy boundaries.

## Using Bundled Resources

- Use `scripts/check_travel_env.py` to report which optional credentials are configured without printing secret values.
- Use `scripts/amap_route_polyline_map.py` to create annotated Amap basemap images with Amap driving-route polylines.
- Read `references/source-playbook.md` for source-specific query patterns, authenticity heuristics, and delivery templates.
