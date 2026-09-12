"""搭子请求（搭子广场）API 路由。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import matching, questionnaires as qn_store, requests as req_store
from ..users import get_user

router = APIRouter(prefix="/api/requests", tags=["requests"])


class RequestCreate(BaseModel):
    user_id: str
    title: str
    match_type: str
    purposes: list[str] = []
    tags: list[str] = []
    desc: str = ""
    requires_questionnaire: bool = False
    questionnaire_id: str | None = None


class QuestionnaireCreate(BaseModel):
    title: str
    request_id: str = ""
    questions: list[dict]


class IntentBody(BaseModel):
    user_id: str
    answers: dict | None = None


class AcceptBody(BaseModel):
    user_id: str          # 发布者
    accepted_user_id: str # 被接受者


def _score_for_me(me: dict, req: dict) -> tuple[float, dict]:
    """计算"我"与该请求（发布者）的匹配度。

    未画像时（me 无 mbti）降级为纯标签匹配，不阻塞浏览。
    """
    owner = get_user(req["user_id"])
    if not owner:
        return 0.0, {}
    use_mbti = bool(me.get("mbti"))
    result = matching.score_match(
        me, owner, req["match_type"],
        use_mbti=use_mbti, purposes=req["purposes"],
    )
    return result["score"], result["detail"]


@router.get("")
def list_requests(user_id: str, match_type: str = "", purpose: str = ""):
    """搭子广场列表，按与我匹配度降序。"""
    me = get_user(user_id)
    if not me:
        raise HTTPException(404, f"用户不存在: {user_id}")

    rows = []
    for req in req_store.list_requests():
        if match_type and req["match_type"] != match_type:
            continue
        if purpose and not (purpose in req["purposes"]):
            continue
        score, detail = _score_for_me(me, req)
        owner = get_user(req["user_id"])
        rows.append({
            "request": req,
            "owner": owner or {"id": req["user_id"], "name": "未知"},
            "matched_person": get_user(req["matched_user_id"]) if req.get("matched_user_id") else None,
            "match_score": round(score, 1),
            "detail": detail,
            "is_owner": req["user_id"] == user_id,
            "has_intent": user_id in req["intents"],
        })
    rows.sort(key=lambda r: r["match_score"], reverse=True)
    return {"count": len(rows), "items": rows}


@router.post("")
def create_request(body: RequestCreate):
    """发布搭子请求。"""
    if not get_user(body.user_id):
        raise HTTPException(404, f"用户不存在: {body.user_id}")
    if not body.title.strip():
        raise HTTPException(400, "标题不能为空")
    if body.match_type not in matching.MATCH_TYPES:
        raise HTTPException(400, f"不支持的搭子类型: {body.match_type}")
    if body.requires_questionnaire:
        if not body.questionnaire_id or not qn_store.get_questionnaire(body.questionnaire_id):
            raise HTTPException(400, "请先设计并保存问卷")
    req = req_store.create_request(
        body.user_id, body.title.strip(), body.match_type,
        body.purposes, body.tags, body.desc.strip(),
        requires_questionnaire=body.requires_questionnaire,
        questionnaire_id=body.questionnaire_id,
    )
    return {"ok": True, "request": req}


@router.post("/questionnaires")
def create_questionnaire(body: QuestionnaireCreate):
    """创建自定义问卷（发布者设计），返回问卷对象。"""
    title = (body.title or "").strip()
    if not title:
        raise HTTPException(400, "问卷标题不能为空")
    ok, msg = qn_store.validate_questions(body.questions)
    if not ok:
        raise HTTPException(400, msg)
    qn = qn_store.create_questionnaire(body.request_id.strip(), title, body.questions)
    return {"ok": True, "questionnaire": qn}


@router.get("/questionnaires/{qid}")
def get_questionnaire(qid: str):
    """查询问卷详情（供意向者填写）。"""
    qn = qn_store.get_questionnaire(qid)
    if not qn:
        raise HTTPException(404, f"问卷不存在: {qid}")
    return qn


@router.post("/{req_id}/intent")
def add_intent(req_id: str, body: IntentBody):
    """表达意向。需问卷的请求须先提交问卷答案。"""
    req = req_store.get_request(req_id)
    if not req:
        raise HTTPException(404, "请求不存在")
    answer_score = None
    if req.get("requires_questionnaire"):
        if not body.answers:
            raise HTTPException(400, "请先完成问卷再表达意向")
        ok, msg, answer_score = req_store.submit_answers(req_id, body.user_id, body.answers)
        if not ok:
            raise HTTPException(400, msg)
    ok, msg = req_store.add_intent(req_id, body.user_id)
    if not ok:
        raise HTTPException(400, msg)
    req = req_store.get_request(req_id)
    return {"ok": True, "intents": req["intents"], "answer_score": answer_score}


@router.delete("/{req_id}/intent")
def remove_intent(req_id: str, user_id: str):
    """取消意向。"""
    ok, msg = req_store.cancel_intent(req_id, user_id)
    if not ok:
        raise HTTPException(400, msg)
    req = req_store.get_request(req_id)
    return {"ok": True, "intents": req["intents"]}


@router.post("/{req_id}/accept")
def accept(req_id: str, body: AcceptBody):
    """发布者接受某意向者，建立搭子关系。"""
    ok, msg = req_store.accept_intent(req_id, body.user_id, body.accepted_user_id)
    if not ok:
        raise HTTPException(400, msg)
    req = req_store.get_request(req_id)
    return {"ok": True, "request": req}


@router.get("/mine/{user_id}")
def my_requests(user_id: str):
    """我的请求：我发布的 + 我表达意向的，附带意向者信息。"""
    if not get_user(user_id):
        raise HTTPException(404, f"用户不存在: {user_id}")

    def _with_people(req: dict) -> dict:
        item = dict(req)
        item["owner"] = get_user(req["user_id"]) or {"id": req["user_id"], "name": "未知"}
        item["intent_people"] = [
            {
                **(
                    get_user(uid)
                    or {"id": uid, "name": "未知"}
                ),
                "answers": (req.get("answers") or {}).get(uid),
                "answer_score": (req.get("answer_scores") or {}).get(uid),
            }
            for uid in req["intents"]
        ]
        if req["matched_user_id"]:
            item["matched_person"] = get_user(req["matched_user_id"]) or {
                "id": req["matched_user_id"], "name": "未知",
            }
        return item

    published = [r for r in req_store.list_requests() if r["user_id"] == user_id]
    interested = [r for r in req_store.list_requests()
                  if r["user_id"] != user_id and user_id in r["intents"]]

    return {
        "user_id": user_id,
        "published": [_with_people(r) for r in published],
        "interested": [_with_people(r) for r in interested],
    }