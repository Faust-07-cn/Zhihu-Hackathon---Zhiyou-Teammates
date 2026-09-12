"""搭子匹配 API 路由。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import matching
from ..users import get_user, list_users

router = APIRouter(prefix="/api/match", tags=["match"])


@router.get("/types")
def match_types():
    """返回支持匹配的类型（含是否需问卷），供前端渲染选择。"""
    return [{"key": k, **v} for k, v in matching.MATCH_TYPES.items()]


@router.get("/{user_id}")
def rank(user_id: str, match_type: str = "interest", top_n: int = 5,
         mbti_filter: str = "", purpose: str = ""):
    """为指定用户计算候选搭子排名。

    - match_type : interest | study | project
    - top_n      : 返回前 N 名
    - mbti_filter: "none" 时不使用 MBTI 参与打分（兼容未画像场景）
    - purpose    : 我寻找搭子的目的，逗号分隔多个（如 "竞赛组队,结伴学习"）
    """
    if match_type not in matching.MATCH_TYPES:
        raise HTTPException(400, f"不支持的匹配类型: {match_type}")

    me = get_user(user_id)
    if not me:
        raise HTTPException(404, f"用户不存在: {user_id}")

    use_mbti = mbti_filter != "none"
    purposes = [p.strip() for p in purpose.split(",") if p.strip()]
    candidates = list_users()
    results = matching.rank_candidates(me, candidates, match_type, top_n=top_n,
                                       use_mbti=use_mbti, purposes=purposes)
    return {
        "me": {"id": me["id"], "name": me["name"], "mbti": me.get("mbti")},
        "match_type": match_type,
        "use_mbti": use_mbti,
        "purposes": purposes,
        "count": len(results),
        "results": results,
    }