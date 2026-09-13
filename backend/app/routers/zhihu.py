"""知乎内容 API 路由（站内搜索代理）。

真实调用知乎开放平台 zhihu_search 接口；未配置 Access Secret 或调用失败时，
由 zhihu.search_zhihu() 返回与真实字段对齐的演示 Mock，前端始终可走通。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import zhihu

router = APIRouter(prefix="/api/zhihu", tags=["zhihu"])


@router.get("/search")
def search(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    count: int = Query(10, ge=1, le=10, description="返回数量"),
):
    """知乎站内搜索。返回 {source, items}，items 字段对齐 zhihu_search 响应。"""
    if not query.strip():
        raise HTTPException(400, "搜索关键词不能为空")
    return zhihu.search_zhihu(query, count)
