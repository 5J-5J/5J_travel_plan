# Source Playbook

## Search Checklist

For each destination or day plan, gather evidence from at least two source families when feasible:

- Gaode/Amap: location, route time, nearby clustering, POI identity, area names, distance sanity.
- Xiaohongshu: recent traveler notes, queues, photo positions, restaurant fit, pitfalls, practical tips.
- Official/primary sources: opening hours, ticket policy, booking windows, transport schedules, seasonal closure.
- General web/review sources: backup when Xiaohongshu or Gaode access is unavailable.

Prefer recent material. For Xiaohongshu, prioritize notes from the last 3-12 months, adjusting for seasonality. A winter ski note is weak evidence for summer; a spring flower note may be valuable only for the same bloom window.

## Gaode/Amap Workflow

Use available tools in this order:

1. If `AMAP_WEB_SERVICE_KEY` exists, use Amap Web Service endpoints for structured checks. Treat this as the normal Gaode credential. Common endpoints include place text search, around search, geocoding, direction, distance, and weather. Browse official docs if endpoint parameters may have changed.
2. If API access is unavailable, use Gaode web pages or general browser/search results for POI and route checks.
3. Record enough route context to make the itinerary auditable: start area, destination, mode, approximate duration, and any long transfer warnings.

For route planning:

- Cluster POIs by district/metro line/river side/mountain area before assigning days.
- Keep city days to 2-4 major stops plus meals; keep family/elder days lighter.
- Avoid backtracking unless the user explicitly wants a famous dinner, show, or night view.
- Add buffer around airports, railway stations, scenic areas, museums, and peak commute windows.

## Xiaohongshu Workflow

Use Xiaohongshu for qualitative planning signals:

- Query patterns: `目的地 行程 天数`, `目的地 避坑`, `景点 排队`, `景点 预约`, `餐厅 名称 体验`, `亲子/老人/情侣 目的地`, `月份 目的地`.
- Extract repeated claims rather than isolated opinions.
- Separate subjective taste ("好拍", "氛围好") from operational facts ("周一闭馆", "现场不能买票").
- Prefer notes with concrete dates, receipts, route screenshots, queue times, original photos, detailed cost breakdowns, and comment discussion.
- Down-rank notes that are ad-like, lack specifics, use identical wording across accounts, omit date/context, or conflict with official facts.

Access order:

1. Prefer an existing user-authorized browser session when available.
2. Use `XHS_COOKIE` only when the user explicitly provides or configures it for research use; never print it back.
3. Use `XHS_SERVICE_ENDPOINT` and `XHS_SERVICE_TOKEN` only as an optional user-provided bridge, not as an assumed public Xiaohongshu API.

If logged-in or cookie-backed access is unavailable:

- Use search-engine indexed notes, snippets, and accessible web pages.
- Tell the user the Xiaohongshu sample may be incomplete.
- Ask for a user-provided link or exported notes only when the plan depends on unavailable content.

## Authenticity Heuristics

Classify each important claim:

- High confidence: confirmed by official source or multiple current independent sources, and consistent with map logistics.
- Medium confidence: repeated by several recent travelers but not official, or supported by one structured source.
- Low confidence: single anecdote, old note, influencer-style recommendation, unverifiable claim, or contradictory evidence.

Flag contradictions explicitly:

- "官方页面显示 X，但近期笔记多人反馈 Y."
- "高德路线约 X 分钟，笔记中常见体感为 Y，建议按更保守值排."
- "该餐厅热度高但负面集中在排队/服务，适合作为备选而非核心安排."

## Budget Bands

Unless the user provides a strict budget, present ranges:

- Economy: public transport, budget meals, limited paid attractions.
- Standard: metro/taxi mix, normal restaurants, key tickets.
- Comfortable: taxis/charter options, better restaurants, shows or private experiences.

Always list assumptions: hotel level, room sharing, children/seniors discounts, city transfer mode, ticket season, and meal count.

## Itinerary Template

Use this structure for detailed plans:

```markdown
## 方案概览

- 时间/人数:
- 旅行节奏:
- 推荐住宿区域:
- 预算预估:
- 核心路线:

## 每日行程

### D1 日期/主题

| 时段 | 安排 | 交通与耗时 | 费用 | 备注 |
|---|---|---|---|---|
| 上午 |  |  |  |  |
| 午餐 |  |  |  |  |
| 下午 |  |  |  |  |
| 晚上 |  |  |  |  |

## 预订与准备

| 项目 | 建议时间 | 依据/风险 |
|---|---|---|

## 预算

| 类别 | 低配 | 标准 | 舒适 | 假设 |
|---|---:|---:|---:|---|

## 证据与可信度

| 结论 | 来源类型 | 可信度 | 说明 |
|---|---|---|---|

## 备选方案
```

Keep the final plan concise enough to use on a phone, but include enough detail that the user can execute it without doing fresh research.
