"""自定义问卷（搭子请求问卷筛选）数据层。

内存态实现，与 requests.py 相同模式，后续可替换为数据库。
问卷仅支持单选题型；每题 2~6 个选项，发布者可标记「期望答案」（选项下标列表）。
"""

from __future__ import annotations

# 问卷库: qid -> 问卷对象
QUESTIONNAIRES: dict[str, dict] = {}

# 起始值覆盖预置问卷占用（q01），保证新问卷 id 不冲突
_id_counter = 1


def _new_id() -> str:
    global _id_counter
    _id_counter += 1
    return f"q{_id_counter:02d}"


def create_questionnaire(request_id: str, title: str, questions: list[dict]) -> dict:
    """创建问卷，返回问卷对象。questions 需已通过校验。"""
    q = {
        "id": _new_id(),
        "title": title,
        "request_id": request_id,
        "questions": questions,
    }
    QUESTIONNAIRES[q["id"]] = q
    return q


def get_questionnaire(qid: str) -> dict | None:
    return QUESTIONNAIRES.get(qid)


def validate_questions(questions: list[dict]) -> tuple[bool, str]:
    """校验题目结构：至少 1 题，每题有题干、2~6 个选项；
    若有 expected，必须是合法选项下标列表。返回 (是否合法, 提示)。"""
    if not questions:
        return False, "问卷至少需要 1 道题"
    for q in questions:
        text = (q.get("text") or "").strip()
        options = [str(o).strip() for o in (q.get("options") or []) if str(o).strip()]
        if not text:
            return False, "题目不能为空"
        if not (2 <= len(options) <= 6):
            return False, f"题目「{text}」需要 2~6 个选项"
        expected = q.get("expected") or []
        for idx in expected:
            if not isinstance(idx, int) or not (0 <= idx < len(options)):
                return False, f"题目「{text}」存在非法期望答案"
    return True, "ok"


def score_answers(questionnaire: dict, answers: dict) -> float:
    """问卷匹配分（0~100）：命中期望答案的题数 ÷ 有期望答案的题数 × 100。

    无期望答案或未作答时返回 50.0 中性分（与 matching.questionnaire_match 一致）。
    """
    if not questionnaire:
        return 50.0
    scored = 0
    hits = 0
    for q in questionnaire.get("questions", []):
        expected = q.get("expected") or []
        if not expected:
            continue
        scored += 1
        ans = answers.get(str(q["id"]))
        if ans is not None and ans in expected:
            hits += 1
    if scored == 0:
        return 50.0
    return round(hits / scored * 100, 1)


# ---------------- 预置演示问卷 ----------------
# r01（数学建模美赛找队友）附带的种子问卷：期望答案见每题 expected。
QUESTIONNAIRES["q01"] = {
    "id": "q01",
    "title": "美赛队友筛选",
    "request_id": "r01",
    "questions": [
        {
            "id": "1",
            "text": "你每周能投入多少时间备赛？",
            "options": ["5 小时以下", "5~10 小时", "10 小时以上"],
            "expected": [1, 2],
        },
        {
            "id": "2",
            "text": "你希望承担的角色？",
            "options": ["编程建模", "论文写作", "数据分析"],
            "expected": [1, 2],
        },
        {
            "id": "3",
            "text": "是否参加过数学建模类竞赛？",
            "options": ["有", "没有"],
            "expected": [0, 1],
        },
    ],
}
