import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Iterable, List, Optional

import requests


@dataclass(frozen=True)
class FundNavPoint:
    nav_date: date
    nav: Decimal
    accumulated_nav: Optional[Decimal] = None
    daily_change_pct: Optional[Decimal] = None


_JSONP_RE = re.compile(r"^[^(]*\((.*)\)\s*;?\s*$", re.DOTALL)


def _to_decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    s = str(value).strip()
    if s == "" or s in {"--", "-"}:
        return None
    return Decimal(s)


def _loads_maybe_jsonp(text: str) -> dict:
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)
    match = _JSONP_RE.match(text)
    if not match:
        raise ValueError("Unexpected response format")
    return json.loads(match.group(1))


def parse_eastmoney_lsjz(payload: dict) -> List[FundNavPoint]:
    data = payload.get("Data") or {}
    items = data.get("LSJZList") or []
    navs: List[FundNavPoint] = []
    for item in items:
        nav_date_str = item.get("FSRQ")
        if not nav_date_str:
            continue
        navs.append(
            FundNavPoint(
                nav_date=date.fromisoformat(nav_date_str),
                nav=_to_decimal(item.get("DWJZ")) or Decimal("0"),
                accumulated_nav=_to_decimal(item.get("LJJZ")),
                daily_change_pct=_to_decimal(item.get("JZZZL")),
            )
        )
    return navs


def fetch_fund_nav_history(
    fund_code: str,
    start_date: date,
    end_date: date,
    page_size: int = 100,
    session: Optional[requests.Session] = None,
) -> List[FundNavPoint]:
    sess = session or requests.Session()
    url = "https://api.fund.eastmoney.com/f10/lsjz"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://fundf10.eastmoney.com/jjjz_{fund_code}.html",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    page_index = 1
    all_points: List[FundNavPoint] = []
    while True:
        params = {
            "fundCode": fund_code,
            "pageIndex": page_index,
            "pageSize": page_size,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }
        resp = sess.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        payload = _loads_maybe_jsonp(resp.text)

        points = parse_eastmoney_lsjz(payload)
        if not points:
            break
        all_points.extend(points)

        total_count = (payload.get("TotalCount") or 0) or 0
        if page_index * page_size >= int(total_count):
            break
        page_index += 1

    unique = {p.nav_date: p for p in all_points}
    return [unique[d] for d in sorted(unique.keys())]

