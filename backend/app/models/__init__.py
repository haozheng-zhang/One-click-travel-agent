"""
----------------------------已弃置----------------------------

数据模型模块
"""

from pydantic import BaseModel, Field
from typing import Optional, List, dict, Any
from datetime import datetime


class UserProfile(BaseModel):
    """用户信息"""
    user_id: str
    name: str
    avatar: Optional[str] = None
    phone: str
    email: str
    preferences: dict[str, Any] = Field(default_factory=dict)


class Traveler(BaseModel):
    """出行人信息"""
    name: str
    id_number: str
    phone: str
    age: Optional[int] = None


class ItineraryItem(BaseModel):
    """行程项"""
    time: str  # HH:MM
    title: str
    location: str
    description: Optional[str] = None
    action: Optional[str] = None  # 如: 查看详情, 改签, 联系客服


class ItineraryCard(BaseModel):
    """行程卡片 - 展示给用户的统一行程视图"""
    trip_id: str
    title: str
    origin: str
    destination: str
    departure_date: str  # YYYY-MM-DD
    return_date: str  # YYYY-MM-DD
    
    # 订单信息
    transport_order: Optional[dict[str, Any]] = None  # 车票/机票信息
    hotels: [dict[str, Any]] = Field(default_factory=list)  # 酒店列表
    tickets: [dict[str, Any]] = Field(default_factory=list)  # 门票列表
    
    # 日程
    itinerary: [ItineraryItem] = Field(default_factory=list)
    
    # 状态
    status: str  # draft, confirmed, in_progress, completed
    created_at: datetime
    updated_at: datetime
