"""
API 路由初始化
"""

from fastapi import APIRouter
from . import travel_planning

router = APIRouter(prefix="/api/v1", tags=["API v1"])

# 包含子路由
router.include_router(travel_planning.router, prefix="/travel", tags=["旅行规划"])
