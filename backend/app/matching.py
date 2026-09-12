"""搭子匹配核心算法。

匹配策略（对应需求文档 2.1 / 2.2）：
- 兴趣搭子   : 仅按标签匹配（低门槛、快速配对）
- 学习搭子   : 基于课程 / 学习方向标签匹配
- 项目搭子   : 标签 + 问卷筛选（提高准入门槛与质量）
"""

from __future__ import annotations

from . import mbti

# ---------------------------------------------------------------
# 匹配类型 -> 是否需要问卷
# ---------------------------------------------------------------
MATCH_TYPES = {
    "interest": {"label": "兴趣搭子", "requires_questionnaire": False},
    "study": {"label": "学习搭子", "requires_questionnaire": False},
    "project": {"label": "项目搭子", "requires_questionnaire": True},
}

# 互补权重（项目搭子看重能力互补而非完全相同）
COMPLEMENTARY_TAGS = {
    "编程": ("产品", "设计", "论文写作", "数据分析"),
    "算法": ("论文写作", "数据分析", "答辩"),
    "前端": ("后端", "设计", "产品"),
    "后端": ("前端", "设计", "产品"),
    "数学建模": ("论文写作", "编程", "数据分析"),
}


def normalize_tags(tags: list[str]) -> list[str]:
    """去空白、去重、统一去空格，便于比较。"""
    seen: set[str] = set()
    out: list[str] = []
    for t in tags or []:
        t = str(t).strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def tag_intersection(me: list[str], other: list[str]) -> set[str]:
    """相似（重合）标签集合。"""
    return set(normalize_tags(me)) & set(normalize_tags(other))


def complement_score(me: list[str], other: list[str]) -> int:
    """互补型匹配：我的标签 <-> 对方标签具有互补关系时加分。"""
    me_s = set(normalize_tags(me))
    other_s = set(normalize_tags(other))
    score = 0
    for mine, goals in COMPLEMENTARY_TAGS.items():
        if mine in me_s:
            score += len(other_s & set(goals))
    return score


def similarity_ratio(a: list[str], b: list[str]) -> float:
    """基于标签重叠的相似度分数（0~100）。"""
    a = set(normalize_tags(a))
    b = set(normalize_tags(b))
    if not a:
        return 0.0
    overlap = len(a & b)
    union = len(a | b)
    if union == 0:
        return 0.0
    # 重合程度 + 覆盖率双因子，避免只重叠一个标签就高分
    jaccard = overlap / union
    coverage = overlap / len(a)
    return round((jaccard * 0.6 + coverage * 0.4) * 100, 1)


def questionnaire_match(me_answers: dict, other_answers: dict) -> float:
    """问卷答案一致性分数（0~100），用于项目搭子的二次筛选。

    answers 形如 {"question_key": value}，value 为字符串或字符串列表。
    """
    if not me_answers or not other_answers:
        return 50.0  # 无问卷数据时给中性分
    keys = set(me_answers.keys()) & set(other_answers.keys())
    if not keys:
        return 50.0
    total = 0.0
    for k in keys:
        a = me_answers.get(k)
        b = other_answers.get(k)
        if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
            if not a or not b:
                continue
            same = len(set(a) & set(b))
            total += same / max(len(set(a) | set(b)), 1) * 100
        elif a is not None and a == b:
            total += 100.0
    return round(total / max(len(keys), 1), 1)


def purpose_match(me_purposes: list[str], other_purposes: list[str]) -> tuple[float, list[str]]:
    """目的匹配度：我的目标目的中有多少与对方目的重合（0~100）。

    返回 (分数, 命中的目的列表)。
    """
    mine = set(normalize_tags(me_purposes))
    others = set(normalize_tags(other_purposes))
    if not mine:
        return 0.0, []
    matched = sorted(mine & others)
    score = round(len(matched) / len(mine) * 100, 1)
    return score, matched


def score_match(me: dict, other: dict, match_type: str,
                use_mbti: bool = True, purposes: list[str] | None = None) -> dict:
    """计算两个用户在某匹配类型下的综合得分及相关明细。

    返回分数范围 0~100（score 字段），数值越高越推荐。
    use_mbti=False 时忽略性格维度；purposes 为「我寻找搭子的目的」列表。
    """
    kind = MATCH_TYPES.get(match_type, MATCH_TYPES["interest"])

    me_tags = normalize_tags(me.get("tags", []))
    other_tags = normalize_tags(other.get("tags", []))

    # 1. 标签相似分
    sim = similarity_ratio(me_tags, other_tags)

    # 2. 互补分（项目搭子权重更高）
    comp = complement_score(me_tags, other_tags)
    # 将互补折算为最多 20 分加成
    comp_scaled = min(comp * 10, 20.0)

    # 3. 问卷分
    q = 0.0
    if kind["requires_questionnaire"]:
        q = questionnaire_match(me.get("questionnaire", {}),
                                other.get("questionnaire", {}))

    # 4. MBTI 性格互补分（作为稳定画像维度）
    mbti_score = mbti.complement_score(me.get("mbti"), other.get("mbti")) if use_mbti else 0.0

    # 5. 目的匹配分（我寻找搭子的目的）
    p_score, p_matched = purpose_match(purposes or [], other.get("purposes", []))

    # 组合加权
    if kind["requires_questionnaire"]:
        # 项目搭子：标签相似 + 标签互补 + 问卷 + MBTI互补 + 目的匹配
        base = (sim * 0.30 + comp_scaled * 0.15 + q * 0.25 + p_score * 0.10
                + (mbti_score * 0.20 if use_mbti else 0.0))
        # use_mbti=False 时重新归一化，避免分数塌缩
        if not use_mbti:
            base = (sim * 0.35 + comp_scaled * 0.20 + q * 0.30 + p_score * 0.15)
    else:
        # 兴趣 / 学习搭子：标签相似 + 目的匹配 + MBTI互补
        if use_mbti:
            base = sim * 0.55 + p_score * 0.15 + mbti_score * 0.30
        else:
            base = sim * 0.85 + p_score * 0.15

    return {
        "match_type": match_type,
        "score": round(min(max(base, 0.0), 100.0), 1),
        "detail": {
            "similarity": sim,
            "complement": round(comp_scaled, 1),
            "questionnaire": q if kind["requires_questionnaire"] else None,
            "shared_tags": sorted(tag_intersection(me_tags, other_tags)),
            "mbti": (other.get("mbti") or None),
            "mbti_score": mbti_score,
            "purpose_score": p_score,
            "matched_purposes": p_matched,
        },
    }


def rank_candidates(me: dict, candidates: list[dict], match_type: str,
                    top_n: int = 10, use_mbti: bool = True,
                    purposes: list[str] | None = None) -> list[dict]:
    """对候选搭子打分并排序，返回前 top_n 名。

    每个候选返回 : {candidate, score, detail}
    use_mbti=False 时匹配不依赖性格维度。
    purposes 为「我寻找搭子的目的」，参与目的匹配度打分。
    """
    scored: list[dict] = []
    for cand in candidates:
        if cand.get("id") == me.get("id"):
            continue  # 跳过自己
        result = score_match(me, cand, match_type, use_mbti=use_mbti,
                             purposes=purposes)
        scored.append(
            {
                "candidate": cand,
                **result,
            }
        )
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]