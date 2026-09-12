"""MBTI 画像问卷 API 路由。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import mbti
from ..mbti_quiz import get_quiz
from ..users import get_user, set_user_mbti

router = APIRouter(prefix="/api/mbti", tags=["mbti"])


class QuizSubmit(BaseModel):
    user_id: str
    answers: dict  # {题目id: "A"/"B"}


class DirectSubmit(BaseModel):
    user_id: str
    mbti: str


@router.get("/quiz")
def quiz():
    """返回 28 题全文，供前端渲染问卷。"""
    return {"total": len(get_quiz()), "items": get_quiz()}


@router.post("/quiz")
def submit_quiz(body: QuizSubmit):
    """提交问卷，计算并写入用户的 MBTI 类型。"""
    user = get_user(body.user_id)
    if not user:
        raise HTTPException(404, f"用户不存在: {body.user_id}")
    result_type = mbti.compute_type(body.answers)
    if not mbti.validate_mbti(result_type):
        raise HTTPException(400, f"无法从答案解析出合法类型: {result_type}")
    set_user_mbti(body.user_id, result_type)
    return {
        "user_id": body.user_id,
        "mbti": result_type,
        "dims": mbti.dims_scores(result_type),
        "complement_ready": True,
    }


@router.post("/direct")
def direct(body: DirectSubmit):
    """用户已知自身 MBTI，直接设置类型（跳过答题）。"""
    t = body.mbti.strip().upper()
    if not mbti.validate_mbti(t):
        raise HTTPException(400, f"非法 MBTI 类型: {body.mbti}（示例 INTJ / ENFP）")
    if not set_user_mbti(body.user_id, t):
        raise HTTPException(404, f"用户不存在: {body.user_id}")
    return {
        "user_id": body.user_id,
        "mbti": t,
        "dims": mbti.dims_scores(t),
        "complement_ready": True,
    }


@router.get("/{user_id}")
def get_profile(user_id: str):
    """查询当前用户画像（含 MBTI）。"""
    user = get_user(user_id)
    if not user:
        raise HTTPException(404, f"用户不存在: {user_id}")
    m = user.get("mbti")
    return {
        "user_id": user["id"],
        "name": user["name"],
        "mbti": m,
        "dims": mbti.dims_scores(m) if m else None,
        "complement_ready": bool(m),
    }