import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.services.eastmoney import parse_eastmoney_lsjz


def test_parse_eastmoney_lsjz_basic():
    payload = {
        "Data": {
            "LSJZList": [
                {"FSRQ": "2025-01-03", "DWJZ": "1.2345", "LJJZ": "2.3456", "JZZZL": "0.12"},
                {"FSRQ": "2025-01-02", "DWJZ": "1.2330", "LJJZ": "2.3440", "JZZZL": "-0.08"},
            ]
        },
        "TotalCount": 2,
        "ErrCode": 0,
    }

    points = parse_eastmoney_lsjz(payload)
    assert len(points) == 2
    assert points[0].nav_date.isoformat() == "2025-01-03"
    assert str(points[0].nav) == "1.2345"
    assert str(points[0].accumulated_nav) == "2.3456"
    assert str(points[0].daily_change_pct) == "0.12"
