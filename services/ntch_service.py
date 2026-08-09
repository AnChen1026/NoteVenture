import json
import os
from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests

# ========= 兩廳院 API 與快取設定 ===========

GRAPHQL_URL = "https://npac-ntch.org/tms/graphql"
COVER_BASE_URL = "https://vfms.npac-ntch.org/vfms-files/"
PROGRAM_PAGE_BASE = "https://npac-ntch.org/programs/"

# 快取約 6 小時（秒）
CACHE_TTL_SECONDS = 6 * 60 * 60
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
CACHE_PATH = os.path.join(CACHE_DIR, "ntch_music_programs.json")

# 標題／簡介／分類含這些關鍵字，視為音樂相關節目
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

# 官網節目列表 GraphQL 查詢
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


# ======================================================
# 取得台灣時間的今天日期
# ======================================================
def _taiwan_today() -> date:
    return datetime.now(timezone(timedelta(hours=8))).date()


# ======================================================
# 確保快取資料夾存在
# ======================================================
def _ensure_cache_dir() -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)


# ======================================================
# 讀取尚未過期的快取；沒有或過期就回 None
# ======================================================
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

    # 舊快取可能沒有時區，當成 UTC
    if fetched_dt.tzinfo is None:
        fetched_dt = fetched_dt.replace(tzinfo=timezone.utc)

    age = (datetime.now(timezone.utc) - fetched_dt.astimezone(timezone.utc)).total_seconds()
    if age > CACHE_TTL_SECONDS:
        return None
    return payload


# ======================================================
# 寫入節目快取並回傳完整結果
# ======================================================
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


# ======================================================
# 判斷節目是否為音樂相關
# ======================================================
def _is_music_related(program: dict[str, Any]) -> bool:
    parts = [str(program.get("title") or ""), str(program.get("brief") or "")]
    for category in program.get("categories") or []:
        parts.append(str(category.get("name") or ""))
    text = " ".join(parts).lower()
    return any(keyword.lower() in text for keyword in MUSIC_KEYWORDS)


# ======================================================
# 把 API 日期轉成台灣本地 YYYY-MM-DD
# ======================================================
def _format_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        local_dt = dt.astimezone(timezone(timedelta(hours=8)))
        return local_dt.strftime("%Y-%m-%d")
    except ValueError:
        return value[:10]


# ======================================================
# 組成海報完整網址
# ======================================================
def _cover_url(cover: str | None) -> str | None:
    if not cover:
        return None
    if cover.startswith("http://") or cover.startswith("https://"):
        return cover
    return COVER_BASE_URL + cover.lstrip("/")


# ======================================================
# 把 API 單筆節目轉成前端需要的欄位
# ======================================================
def _normalize_program(program: dict[str, Any]) -> dict[str, Any]:
    categories = program.get("categories") or []
    # 優先用主分類
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


# ======================================================
# 向兩廳院 GraphQL 抓取指定日期區間的節目
# ======================================================
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

    # 分頁抓取，最多約 120 筆避免過度請求
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


# ======================================================
# 取得近一個月音樂相關節目（有快取；失敗時可回退舊快取）
# ======================================================
def get_upcoming_music_programs(force_refresh: bool = False) -> dict[str, Any]:
    # 未要求強制刷新時，先用有效快取
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
        # 即時抓取失敗時，盡量回傳舊快取
        if os.path.isfile(CACHE_PATH):
            try:
                with open(CACHE_PATH, "r", encoding="utf-8") as f:
                    stale = json.load(f)
                stale["source"] = f"cache-fallback ({error})"
                return stale
            except (OSError, json.JSONDecodeError):
                pass
        raise
