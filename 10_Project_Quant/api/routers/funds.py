from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, database
from .. import schemas
from ..schemas import FundDetailResponse
from ..services.eastmoney import fetch_fund_nav_history

router = APIRouter(prefix="/api/funds", tags=["funds"])

@router.get("/", response_model=schemas.FundListResponse)
def read_funds(
    skip: int = 0, 
    limit: int = 100, 
    type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    db: Session = Depends(database.get_db)
):
    return crud.get_fund_list(
        db,
        skip=skip,
        limit=limit,
        fund_type=type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

@router.get("/{code}", response_model=FundDetailResponse)
def read_fund(code: str, limit: int = 180, db: Session = Depends(database.get_db)):
    fund = crud.get_fund_by_code(db, code=code)
    if fund is None:
        raise HTTPException(status_code=404, detail="Fund not found")
    navs = crud.get_fund_navs(db, fund_id=fund.id, limit=limit)
    return {
        "id": fund.id,
        "code": fund.code,
        "name": fund.name,
        "fund_type": fund.fund_type,
        "created_at": fund.created_at,
        "navs": navs,
    }

@router.post("/sync")
def sync_funds(days: int = Query(default=30, ge=1, le=3650), db: Session = Depends(database.get_db)):
    funds = crud.get_funds(db, skip=0, limit=10000)
    if not funds:
        return {"status": "noop", "message": "No funds in database. Please add funds first."}

    end = date.today()
    start = end - timedelta(days=days)

    total_inserted = 0
    per_fund = []
    for fund in funds:
        points = fetch_fund_nav_history(fund.code, start_date=start, end_date=end)
        inserted = crud.upsert_fund_navs(db, fund_id=fund.id, points=points)
        total_inserted += inserted
        per_fund.append({"code": fund.code, "inserted": inserted, "fetched": len(points)})

    return {"status": "success", "inserted": total_inserted, "details": per_fund}
