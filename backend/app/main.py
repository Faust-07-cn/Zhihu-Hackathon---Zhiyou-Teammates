"""FastAPI 应用入口。

启动:
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, mbti, match, posts, requests, users, zhihu
from .db import init_db

init_db()

app = FastAPI(title="校园搭子 API", version="0.1.0")

# 允许前端跨域访问（本地开发：前后端分端口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zhiyouteammates.site",
        "https://www.zhiyouteammates.site",
        "https://zhiyouteammates-qawwzpox.edgeone.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(auth.zhihu_router)
app.include_router(match.router)
app.include_router(mbti.router)
app.include_router(requests.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(zhihu.router)


@app.get("/")
def root():
    return {"service": "campus-dazi", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}