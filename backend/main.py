"""
一键出行智能体 - 主程序入口
"""

import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import travel_planning
from app.config import settings

# 加载环境变量 - 优先加载 .env.local，再加载 .env
env_local_path = Path(__file__).parent / ".env.local"
if env_local_path.exists():
    load_dotenv(env_local_path)
else:
    load_dotenv()

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 应用生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    logger.info("🚀 一键出行智能体启动")
    logger.info(f"环境: {settings.ENVIRONMENT}")
    if settings.LLM_API_KEY:
        logger.info("✓ Deepseek API Key 已配置")
    else:
        logger.warning("⚠️  Deepseek API Key 未配置，请在 .env 文件中设置")
    yield
    # 关闭事件
    logger.info("🛑 一键出行智能体关闭")

# 创建 FastAPI 应用
app = FastAPI(
    title="一键出行智能体 API",
    description="聚合所有出行需求的AI助手，第一步：意图解析与核心需求提取",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源，生产环境需要配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(travel_planning.router, prefix="/api/v1", tags=["旅行规划"])

@app.get("/")
async def root():
    """根路由 - 健康检查"""
    return {
        "status": "running",
        "message": "一键出行智能体服务正常运行",
        "version": "0.1.0"
    }

@app.get("/api/v1/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": "2025-03-18"
    }

if __name__ == "__main__":
    import uvicorn
    
    # 读取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"启动服务: {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )
