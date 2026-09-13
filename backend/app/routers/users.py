"""演示用户 API 路由。

提供当前内存用户池的公开信息，供前端「演示账号切换」与「我的」名片使用。
知乎画像来自 zhihu.py（当前为演示 Mock，字段已按真实接口预留）。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import zhihu
from ..users import get_user, list_users, update_user_profile

router = APIRouter(prefix="/api/users", tags=["users"])


class ProfileUpdate(BaseModel):
    name: str | None = None
    school: str | None = None
    tags: list[str] | None = None
    purposes: list[str] | None = None
    availability: dict | None = None
    collab: dict | None = None
    questionnaire: dict | None = None


def _public(user: dict) -> dict:
    profile = zhihu.get_profile(user["id"])
    meta = profile.get("profile", {})
    return {
        "id": user["id"],
        "name": user["name"],
        "school": user["school"],
        "level": user.get("level"),
        "score": user.get("score"),
        "mbti": user.get("mbti"),
        "tags": user.get("tags", []),
        "purposes": user.get("purposes", []),
        "availability": user.get("availability", {}),
        "collab": user.get("collab", {}),
        # 知乎画像摘要（source 为 mock 时前端会标注「演示数据」）
        "zhihu": {
            "source": profile.get("source", ""),
            "fullname": meta.get("fullname", ""),
            "headline": meta.get("headline", ""),
            "url": meta.get("url", ""),
            "topics": profile.get("topics", []),
        },
    }


@router.get("")
def list_all():
    """演示账号列表（用于切换当前登录身份）。"""
    return {"items": [_public(u) for u in list_users()]}


@router.put("/{user_id}")
def update(user_id: str, body: ProfileUpdate):
    user = update_user_profile(user_id, body.model_dump(exclude_none=True))
    if not user:
        raise HTTPException(404, f"用户不存在: {user_id}")
    return _public(user)


@router.get("/{user_id}")
def one(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(404, f"用户不存在: {user_id}")
    return _public(user)
