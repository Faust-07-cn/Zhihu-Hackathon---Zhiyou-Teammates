"""搭子请求（搭子广场）数据层。

内存态实现，后续可替换为数据库。
请求状态机：open（开放中）→ matched（已成组）；closed 为手动关闭（预留）。
"""

from __future__ import annotations

from datetime import datetime

from . import questionnaires as qn_store
from .db import load, save

# 预置演示请求（含 1 条带意向的，方便演示"接受"流程）
REQUESTS: list[dict] = [
    {
        "id": "r01",
        "user_id": "u02",
        "title": "数学建模美赛找队友（编程/写作）",
        "match_type": "project",
        "purposes": ["竞赛组队"],
        "tags": ["数学建模", "论文写作", "数据分析"],
        "desc": "准备打明年美赛，需要一个会编程建模的队友，另一个负责论文排版写作，时间投入可保证。",
        "status": "open",
        "intents": ["u01"],
        "matched_user_id": None,
        "created_at": "2026-09-13 09:30",
        "requires_questionnaire": True,
        "questionnaire_id": "q01",
        "answers": {"u01": {"1": 1, "2": 1, "3": 1}},
        "answer_scores": {"u01": 100.0},
    },
    {
        "id": "r02",
        "user_id": "u05",
        "title": "嵌入式/软硬结合项目搭子",
        "match_type": "project",
        "purposes": ["竞赛组队"],
        "tags": ["嵌入式", "编程", "硬件"],
        "desc": "做一个智能硬件小项目，缺个懂硬件画板的，我自己写代码。",
        "status": "open",
        "intents": [],
        "matched_user_id": None,
        "created_at": "2026-09-13 08:50",
        "requires_questionnaire": False,
        "questionnaire_id": None,
        "answers": {},
        "answer_scores": {},
    },
    {
        "id": "r03",
        "user_id": "u04",
        "title": "一起备考六级/雅思，每日打卡",
        "match_type": "study",
        "purposes": ["结伴学习"],
        "tags": ["英语", "课程"],
        "desc": "找个英语搭子互相监督，每天打卡背单词+刷题，周末可以线下图书馆。",
        "status": "open",
        "intents": [],
        "matched_user_id": None,
        "created_at": "2026-09-13 08:10",
        "requires_questionnaire": False,
        "questionnaire_id": None,
        "answers": {},
        "answer_scores": {},
    },
    {
        "id": "r04",
        "user_id": "u06",
        "title": "求一个摄影搭子，周末扫街",
        "match_type": "interest",
        "purposes": ["兴趣交流"],
        "tags": ["摄影", "生活"],
        "desc": "周末想找人一起扫街拍照，新手老手都欢迎，纯粹兴趣。",
        "status": "open",
        "intents": [],
        "matched_user_id": None,
        "created_at": "2026-09-12 20:00",
        "requires_questionnaire": False,
        "questionnaire_id": None,
        "answers": {},
        "answer_scores": {},
    },
    # 以下 3 条为「发起搭子」演示补齐：保证每个演示账号都有可响应的开放请求
    {
        "id": "r05",
        "user_id": "u01",
        "title": "找算法搭子一起刷题备战校赛",
        "match_type": "study",
        "purposes": ["竞赛组队", "结伴学习"],
        "tags": ["算法", "数据结构"],
        "desc": "每周固定刷题+复盘，希望找能坚持、愿意交流思路的搭子。",
        "status": "open",
        "intents": [],
        "matched_user_id": None,
        "created_at": "2026-09-13 10:10",
        "requires_questionnaire": False,
        "questionnaire_id": None,
        "answers": {},
        "answer_scores": {},
    },
    {
        "id": "r06",
        "user_id": "u02",
        "title": "找数据分析搭子做课程项目（长期）",
        "match_type": "project",
        "purposes": ["竞赛组队"],
        "tags": ["数据分析", "论文写作"],
        "desc": "课程项目偏数据分析方向，希望长期稳定推进，可先线上沟通。",
        "status": "open",
        "intents": [],
        "matched_user_id": None,
        "created_at": "2026-09-13 10:40",
        "requires_questionnaire": False,
        "questionnaire_id": None,
        "answers": {},
        "answer_scores": {},
    },
    {
        "id": "r07",
        "user_id": "u03",
        "title": "想找前后端一起做课程设计",
        "match_type": "project",
        "purposes": ["竞赛组队", "兴趣交流"],
        "tags": ["UI", "设计", "产品"],
        "desc": "我负责界面与答辩材料，想找能写前后端的同学一起完成课程设计。",
        "status": "open",
        "intents": [],
        "matched_user_id": None,
        "created_at": "2026-09-13 11:05",
        "requires_questionnaire": False,
        "questionnaire_id": None,
        "answers": {},
        "answer_scores": {},
    },
]


def _new_id() -> str:
    return f"r{len(REQUESTS) + 1:02d}"


_loaded = False

def _ensure_loaded():
    global _loaded
    if not _loaded:
        REQUESTS[:] = load("requests", REQUESTS)
        _loaded = True


def list_requests() -> list[dict]:
    _ensure_loaded()
    return REQUESTS


def get_request(req_id: str) -> dict | None:
    _ensure_loaded()
    return next((r for r in REQUESTS if r["id"] == req_id), None)


def create_request(user_id: str, title: str, match_type: str,
                   purposes: list[str], tags: list[str], desc: str,
                   requires_questionnaire: bool = False,
                   questionnaire_id: str | None = None) -> dict:
    """创建新请求，返回请求对象。"""
    req = {
        "id": _new_id(),
        "user_id": user_id,
        "title": title,
        "match_type": match_type,
        "purposes": [p for p in (purposes or []) if p],
        "tags": [t for t in (tags or []) if t],
        "desc": desc,
        "status": "open",
        "intents": [],
        "matched_user_id": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "requires_questionnaire": bool(requires_questionnaire),
        "questionnaire_id": questionnaire_id,
        "answers": {},
        "answer_scores": {},
    }
    _ensure_loaded()
    REQUESTS.append(req)
    save("requests", REQUESTS)
    return req


def submit_answers(req_id: str, user_id: str, answers: dict) -> tuple[bool, str, float | None]:
    """保存意向者的问卷答案并计算匹配分。返回 (是否成功, 提示, 分数)。

    分数由关联问卷的期望答案计算；无问卷的请求直接成功但不计分。
    """
    req = get_request(req_id)
    if not req:
        return False, "请求不存在", None
    qn = qn_store.get_questionnaire(req["questionnaire_id"]) if req.get("questionnaire_id") else None
    if req.get("requires_questionnaire") and not qn:
        return False, "问卷不存在，无法提交", None
    answers = answers or {}
    expected_ids = {str(q.get("id", i)) for i, q in enumerate(qn.get("questions", []), 1)} if qn else set()
    if qn and set(map(str, answers)) != expected_ids:
        return False, "请完整回答每一道题", None
    for i, q in enumerate(qn.get("questions", []), 1) if qn else []:
        key = str(q.get("id", i))
        value = answers.get(key)
        if not isinstance(value, int) or value < 0 or value >= len(q.get("options", [])):
            return False, f"第{i}题答案超出选项范围", None
    req.setdefault("answers", {})[user_id] = dict(answers)
    score = qn_store.score_answers(qn, answers or {}) if qn else 50.0
    req.setdefault("answer_scores", {})[user_id] = score
    save("requests", REQUESTS)
    return True, "ok", score


def add_intent(req_id: str, user_id: str) -> tuple[bool, str]:
    """表达意向。返回 (是否成功, 提示)。

    规则：请求须存在且 open；发布者不能意向自己的请求；重复意向幂等；
    需问卷的请求须先完成问卷（submit_answers）才能表达意向。
    """
    req = get_request(req_id)
    if not req:
        return False, "请求不存在"
    if req["user_id"] == user_id:
        return False, "不能意向自己发布的请求"
    if req["status"] != "open":
        return False, "该请求已结束"
    if user_id in req["intents"]:
        return False, "已表达过意向"
    if req.get("requires_questionnaire") and user_id not in (req.get("answers") or {}):
        return False, "请先完成问卷再表达意向"
    req["intents"].append(user_id)
    save("requests", REQUESTS)
    return True, "ok"


def cancel_intent(req_id: str, user_id: str) -> tuple[bool, str]:
    """取消意向。"""
    req = get_request(req_id)
    if not req:
        return False, "请求不存在"
    if user_id not in req["intents"]:
        return False, "未表达过意向"
    req["intents"].remove(user_id)
    save("requests", REQUESTS)
    return True, "ok"


def accept_intent(req_id: str, owner_id: str, accepted_user_id: str) -> tuple[bool, str]:
    """发布者从意向列表中选择接受某人，请求转为 matched。

    返回 (是否成功, 提示)。
    """
    req = get_request(req_id)
    if not req:
        return False, "请求不存在"
    if req["user_id"] != owner_id:
        return False, "只有发布者可以接受意向"
    if req["status"] != "open":
        return False, "该请求已结束"
    if accepted_user_id not in req["intents"]:
        return False, "该用户未表达意向"
    req["status"] = "matched"
    req["matched_user_id"] = accepted_user_id
    save("requests", REQUESTS)
    return True, "ok"