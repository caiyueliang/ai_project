from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date, datetime
from .models import UserRole, BacktestStatus

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class FundBase(BaseModel):
    code: str
    name: str
    fund_type: Optional[str] = None

class FundResponse(FundBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FundListItem(FundBase):
    id: int
    nav: Optional[float] = None
    nav_date: Optional[date] = None
    daily_change_pct: Optional[float] = None


class FundListResponse(BaseModel):
    total: int
    items: List[FundListItem]

class FundNavResponse(BaseModel):
    nav_date: date
    nav: float
    accumulated_nav: Optional[float] = None

    class Config:
        from_attributes = True

class FundDetailResponse(FundResponse):
    navs: List[FundNavResponse] = []

class BacktestCreate(BaseModel):
    fund_codes: List[str]
    start_date: date
    end_date: date
    strategy_params: dict

class BacktestResponse(BaseModel):
    task_id: str
    status: BacktestStatus
    created_at: datetime

    class Config:
        from_attributes = True
