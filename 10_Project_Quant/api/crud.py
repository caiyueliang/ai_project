from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas
from passlib.context import CryptContext

from .services.eastmoney import FundNavPoint

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_funds(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    fund_type: Optional[str] = None,
    search: Optional[str] = None
):
    query = db.query(models.Fund)
    if fund_type:
        query = query.filter(models.Fund.fund_type == fund_type)
    if search:
        query = query.filter(models.Fund.name.contains(search) | models.Fund.code.contains(search))
    return query.offset(skip).limit(limit).all()


def get_fund_list(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    fund_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
):
    query = db.query(models.Fund)
    if fund_type:
        query = query.filter(models.Fund.fund_type == fund_type)
    if search:
        query = query.filter(models.Fund.name.contains(search) | models.Fund.code.contains(search))

    total = query.count()
    funds = query.offset(skip).limit(limit).all()

    items: List[dict] = []
    for fund in funds:
        navs = (
            db.query(models.FundNav)
            .filter(models.FundNav.fund_id == fund.id)
            .order_by(models.FundNav.nav_date.desc())
            .limit(2)
            .all()
        )
        latest = navs[0] if len(navs) >= 1 else None
        prev = navs[1] if len(navs) >= 2 else None

        nav_val = float(latest.nav) if latest and latest.nav is not None else None
        nav_date_val = latest.nav_date if latest else None

        daily_change_pct = None
        if latest and prev and latest.nav and prev.nav:
            prev_nav = Decimal(prev.nav)
            if prev_nav != 0:
                daily_change_pct = float((Decimal(latest.nav) - prev_nav) / prev_nav * Decimal("100"))

        items.append(
            {
                "id": fund.id,
                "code": fund.code,
                "name": fund.name,
                "fund_type": fund.fund_type,
                "nav": nav_val,
                "nav_date": nav_date_val,
                "daily_change_pct": daily_change_pct,
            }
        )

    if sort_by in {"nav", "daily_change_pct", "code", "name"}:
        reverse = sort_order.lower() != "asc"
        items.sort(key=lambda x: (x.get(sort_by) is None, x.get(sort_by)), reverse=reverse)

    return {"total": total, "items": items}

def get_fund_by_code(db: Session, code: str):
    return db.query(models.Fund).filter(models.Fund.code == code).first()


def get_fund_navs(db: Session, fund_id: int, limit: int = 180):
    navs = (
        db.query(models.FundNav)
        .filter(models.FundNav.fund_id == fund_id)
        .order_by(models.FundNav.nav_date.desc())
        .limit(limit)
        .all()
    )
    navs.reverse()
    return navs


def upsert_fund_navs(db: Session, fund_id: int, points: List[FundNavPoint]) -> int:
    if not points:
        return 0

    dates = [p.nav_date for p in points]
    existing = (
        db.query(models.FundNav.nav_date)
        .filter(models.FundNav.fund_id == fund_id)
        .filter(models.FundNav.nav_date.in_(dates))
        .all()
    )
    existing_dates = {row[0] for row in existing}

    inserted = 0
    for p in points:
        if p.nav_date in existing_dates:
            continue
        db.add(
            models.FundNav(
                fund_id=fund_id,
                nav_date=p.nav_date,
                nav=p.nav,
                accumulated_nav=p.accumulated_nav,
            )
        )
        inserted += 1
    if inserted:
        db.commit()
    return inserted

def create_backtest(db: Session, backtest: schemas.BacktestCreate, user_id: int, task_id: str):
    db_backtest = models.Backtest(
        user_id=user_id,
        task_id=task_id,
        strategy_params=backtest.strategy_params,
        start_date=backtest.start_date,
        end_date=backtest.end_date,
        fund_codes=backtest.fund_codes,
        status=models.BacktestStatus.pending
    )
    db.add(db_backtest)
    db.commit()
    db.refresh(db_backtest)
    return db_backtest
