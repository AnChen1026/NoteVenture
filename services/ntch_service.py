"""
兩廳院（NPAC-NTCH）近一個月音樂節目資料。

說明：
- 官網節目頁為前端 SPA，實際資料來自官方 GraphQL：https://npac-ntch.org/tms/graphql
- 本服務以 requests 呼叫該 API，再篩選「音樂相關」節目，並做檔案快取避免頻繁請求。
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests

GRAPHQL_URL = "https://npac-ntch.org/tms/graphql"
COVER_BASE_URL = "https://vfms.npac-ntch.org/vfms-files/"
PROGRAM_PAGE_BASE = "https://npac-ntch.org/programs/"

# 快取約 6 小時（秒）
CACHE_TTL_SECONDS = 6 * 60 * 60
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
CACHE_PATH = os.path.join(CACHE_DIR, "ntch_music_programs.json")

MUSIC_KEYWORDS = (
    "音樂",
    "爵士",
    "合唱",
    "管絃",
    "管弦",
    "鋼琴",
    "聲樂",
    "室內樂",
    "交響",
    "歌劇",
    "音樂劇",
    "樂團",
    "演奏",
    "音樂會",
    "小提琴",
    "大提琴",
    "吉他",
    "打擊",
    "recital",
    "concert",
    "jazz",
    "orchestra",
    "piano",
    "choir",
)

PROGRAMS_QUERY = """
query Programs($startFrom: DateOnly, $endOn: DateOnly, $limit: Int, $offset: Int) {
  programs(startFrom: $startFrom, endOn: $endOn, limit: $limit, offset: $offset) {
    id
    title
    cover
    startFrom
    endOn
    type
    brief
    categories { code name isMain }
  }
}
"""


def _taiwan_today() -> date:
    return datetime.now(timezone(timedelta(hours=8))).date()


def _ensure_cache_dir() -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)


def _read_cache() -> dict[str, Any] | None:
    if not os.path.isfile(CACHE_PATH):
        return None
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    fetched_at = payload.get("fetched_at")
    if not fetched_at:
        return None
    try:
        fetched_dt = datetime.fromisoformat(fetched_at)
    except ValueError:
        return None

    if fetched_dt.tzinfo is None:
        fetched_dt = fetched_dt.replace(tzinfo=timezone.utc)

    age = (datetime.now(timezone.utc) - fetched_dt.astimezone(timezone.utc)).total_seconds()
    if age > CACHE_TTL_SECONDS:
        return None
    return payload


def _write_cache(items: list[dict[str, Any]], source: str) -> dict[str, Any]:
    _ensure_cache_dir()
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "count": len(items),
        "data": items,
    }
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


def _is_music_related(program: dict[str, Any]) -> bool:
    parts = [str(program.get("title") or ""), str(program.get("brief") or "")]
    for category in program.get("categories") or []:
        parts.append(str(category.get("name") or ""))
    text = " ".join(parts).lower()
    return any(keyword.lower() in text for keyword in MUSIC_KEYWORDS)


def _format_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        local_dt = dt.astimezone(timezone(timedelta(hours=8)))
        return local_dt.strftime("%Y-%m-%d")
    except ValueError:
        return value[:10]


def _cover_url(cover: str | None) -> str | None:
    if not cover:
        return None
    if cover.startswith("http://") or cover.startswith("https://"):
        return cover
    return COVER_BASE_URL + cover.lstrip("/")


def _normalize_program(program: dict[str, Any]) -> dict[str, Any]:
    categories = program.get("categories") or []
    main_category = next((c for c in categories if c.get("isMain")), None)
    if main_category is None and categories:
        main_category = categories[0]

    program_id = str(program.get("id") or "")
    return {
        "id": program_id,
        "title": program.get("title") or "",
        "brief": program.get("brief") or "",
        "start_date": _format_date(program.get("startFrom")),
        "end_date": _format_date(program.get("endOn")),
        "category": (main_category or {}).get("name") or "",
        "categories": [c.get("name") for c in categories if c.get("name")],
        "cover_url": _cover_url(program.get("cover")),
        "url": PROGRAM_PAGE_BASE + program_id if program_id else "",
    }


def _fetch_programs_from_api(start_day: date, end_day: date) -> list[dict[str, Any]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://npac-ntch.org",
        "Referer": "https://npac-ntch.org/programs",
        "X-Language": "zh-TW",
    }

    collected: list[dict[str, Any]] = []
    offset = 0
    limit = 40

    while offset < 120:
        payload = {
            "operationName": "Programs",
            "variables": {
                "startFrom": start_day.isoformat(),
                "endOn": end_day.isoformat(),
                "limit": limit,
                "offset": offset,
            },
            "query": PROGRAMS_QUERY,
        }
        response = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=25)
        response.raise_for_status()
        body = response.json()
        if body.get("errors"):
            raise RuntimeError(str(body["errors"][0].get("message") or "GraphQL error"))

        batch = ((body.get("data") or {}).get("programs")) or []
        if not batch:
            break
        collected.extend(batch)
        if len(batch) < limit:
            break
        offset += limit

    return collected


def get_upcoming_music_programs(force_refresh: bool = False) -> dict[str, Any]:
    """
    取得近一個月音樂相關節目。
    回傳：{ fetched_at, source, count, data: [...] }
    """
    if not force_refresh:
        cached = _read_cache()
        if cached is not None:
            return cached

    start_day = _taiwan_today()
    end_day = start_day + timedelta(days=30)

    try:
        raw_programs = _fetch_programs_from_api(start_day, end_day)
        music_programs = [
            _normalize_program(item)
            for item in raw_programs
            if _is_music_related(item)
        ]
        # 依開始日期排序
        music_programs.sort(key=lambda item: item.get("start_date") or "")
        return _write_cache(music_programs, source="npac-ntch.org/tms/graphql")
    except Exception as error:
        # 若即時抓取失敗，盡量回退舊快取
        if os.path.isfile(CACHE_PATH):
            try:
                with open(CACHE_PATH, "r", encoding="utf-8") as f:
                    stale = json.load(f)
                stale["source"] = f"cache-fallback ({error})"
                return stale
            except (OSError, json.JSONDecodeError):
                pass
        raise
