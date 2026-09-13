"""搭子匹配 API 路由。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import matching, requests as req_store
from ..users import get_user, list_users

router = APIRouter(prefix="/api/match", tags=["match"])


class ConnectBody(BaseModel):
    target_user_id: str


def _candidate_requests(target_user_id: str) -> list[dict]:
    """目标用户当前开放的搭子请求，不需要问卷的排在前面。"""
    rows = [r for r in req_store.list_requests()
            if r["user_id"] == target_user_id and r["status"] == "open"]
    rows.sort(key=lambda r: bool(r.get("requires_questionnaire")))
    return rows


def _connect_state(me_id: str, other_id: str) -> dict:
    """推荐卡上「发起搭子」按钮的状态。"""
    rows = _candidate_requests(other_id)
    if not rows:
        return {"request_id": None, "has_intent": False, "requires_questionnaire": False}
    for r in rows:
        if me_id in r["intents"]:
            return {"request_id": r["id"], "has_intent": True,
                    "requires_questionnaire": bool(r.get("requires_questionnaire"))}
    r = rows[0]
    return {"request_id": r["id"], "has_intent": False,
            "requires_questionnaire": bool(r.get("requires_questionnaire"))}


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
                   缺省时使用我画像中已有的目的，避免目标维度缺省导致分数塌缩
    """
    if match_type not in matching.MATCH_TYPES:
        raise HTTPException(400, f"不支持的匹配类型: {match_type}")

    me = get_user(user_id)
    if not me:
        raise HTTPException(404, f"用户不存在: {user_id}")

    use_mbti = mbti_filter != "none"
    purposes = [p.strip() for p in purpose.split(",") if p.strip()] or list(me.get("purposes", []))
    candidates = list_users()
    results = matching.rank_candidates(me, candidates, match_type, top_n=top_n,
                                       use_mbti=use_mbti, purposes=purposes)

    # 为每张推荐卡补充「发起搭子」按钮所需的状态
    for item in results:
        item["connect"] = _connect_state(user_id, item["candidate"]["id"])

    return {
        "me": {"id": me["id"], "name": me["name"], "mbti": me.get("mbti")},
        "match_type": match_type,
        "use_mbti": use_mbti,
        "purposes": purposes,
        "weights": matching.WEIGHTS,
        "count": len(results),
        "results": results,
    }


@router.post("/{user_id}/connect")
def connect(user_id: str, body: ConnectBody):
    """推荐卡「发起搭子」：在目标用户当前开放的请求上表达意向。

    返回值 mode：
    - intent        ：已成功表达意向（或此前已表达）
    - questionnaire ：目标请求需要先完成问卷，需到搭子广场响应
    - none          ：目标用户暂时没有开放的搭子请求
    """
    me = get_user(user_id)
    if not me:
        raise HTTPException(404, f"用户不存在: {user_id}")
    target = get_user(body.target_user_id)
    if not target:
        raise HTTPException(404, f"用户不存在: {body.target_user_id}")
    if user_id == body.target_user_id:
        raise HTTPException(400, "不能对自己发起搭子")

    rows = _candidate_requests(body.target_user_id)
    if not rows:
        return {"ok": True, "mode": "none",
                "message": f"{target['name']} 暂时没有开放的搭子请求"}

    for r in rows:
        if user_id in r["intents"]:
            return {"ok": True, "mode": "intent", "request_id": r["id"], "already": True}

    # 需要问卷的请求无法在推荐卡上直接响应，引导到搭子广场
    best = rows[0]
    if best.get("requires_questionnaire"):
        return {"ok": True, "mode": "questionnaire", "request_id": best["id"],
                "message": "TA 的搭子请求需要先完成问卷，请到「搭子广场」响应"}

    ok, msg = req_store.add_intent(best["id"], user_id)
    if not ok:
        raise HTTPException(400, msg)
    return {"ok": True, "mode": "intent", "request_id": best["id"]}
