"""搭子匹配核心算法（可解释加权模型）。

设计目标：让用户能看懂「分数从哪里来」，并让知乎内容成为推荐理由的一部分。

加权维度（WEIGHTS）：
    目标 40% + 时间 25% + 能力 20% + 合作方式 10% + 性格互补 5%
- 目标    ：双方寻找搭子的目的重合度（竞赛组队 / 结伴学习 / 兴趣交流 …）
- 时间    ：每周可投入时长接近度 + 可约时段重合 + 长期/短期一致
- 能力    ：技能标签相似度 + 互补性（项目搭子再叠加问卷自评一致性）
- 合作方式：线上/线下偏好、主导/协作、回复与见面习惯、地点是否方便
- 性格    ：MBTI 互补（辅助参考，权重最低；任一方无画像时该维度自动移除并重新归一化）

说明：MBTI 不再主导推荐，仅在双方都有画像时提供 5% 的辅助信号。
知乎特色：共同话题与共同内容（回答/文章/收藏）进入 detail.shared_zhihu_contents，
并生成自然语言 detail.reasons，数据来源见 zhihu.py（当前为演示 Mock，已预留真实接口）。
"""

from __future__ import annotations

from . import mbti, zhihu

# ---------------------------------------------------------------
# 匹配类型 -> 是否需要问卷
# ---------------------------------------------------------------
MATCH_TYPES = {
    "interest": {"label": "兴趣搭子", "requires_questionnaire": False},
    "study": {"label": "学习搭子", "requires_questionnaire": False},
    "project": {"label": "项目搭子", "requires_questionnaire": True},
}

# 加权模型权重（合计 1.0）
WEIGHTS = {
    "goal": 0.40,
    "time": 0.25,
    "ability": 0.20,
    "style": 0.10,
    "mbti": 0.05,
}
DIM_LABELS = {
    "goal": "目标",
    "time": "时间",
    "ability": "能力",
    "style": "合作",
    "mbti": "性格",
}
DIM_ORDER = ["goal", "time", "ability", "style", "mbti"]

# 互补权重（项目搭子看重能力互补而非完全相同）
COMPLEMENTARY_TAGS = {
    "编程": ("产品", "设计", "论文写作", "数据分析"),
    "算法": ("论文写作", "数据分析", "答辩"),
    "前端": ("后端", "设计", "产品"),
    "后端": ("前端", "设计", "产品"),
    "数学建模": ("论文写作", "编程", "数据分析"),
}

# 「都可以」类中性取值：视为与任何偏好都兼容
NEUTRAL_VALUES = {"均可", "不限", "都可以"}


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
    """问卷自评一致性分数（0~100），用于项目搭子的能力维度。

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


# ---------------------------------------------------------------
# 各维度打分：无法计算时返回 None，由归一化逻辑自动剔除该维度
# ---------------------------------------------------------------
def _ratio(a, b, same: float = 1.0, diff: float = 0.4, neutral: set[str] | None = None) -> float | None:
    """两个取值的一致度：任一为空返回 None；命中中性值视为完全兼容。"""
    if not a or not b:
        return None
    neutral = neutral or NEUTRAL_VALUES
    if a in neutral or b in neutral:
        return 1.0
    return same if a == b else diff


def _hours_proximity(a, b) -> float | None:
    """每周可投入时长接近度（0~1）。"""
    try:
        a = float(a or 0)
        b = float(b or 0)
    except (TypeError, ValueError):
        return None
    if a <= 0 or b <= 0:
        return None
    return 1 - abs(a - b) / max(a, b)


def _jaccard(a: list[str], b: list[str]) -> float | None:
    sa, sb = set(normalize_tags(a)), set(normalize_tags(b))
    if not sa or not sb:
        return None
    return len(sa & sb) / len(sa | sb)


def _location_ratio(me_collab: dict, other_collab: dict) -> float | None:
    """地点便利度：同城同校区 > 同城 > 异地且都接受线上 > 异地。"""
    my_city, other_city = me_collab.get("city"), other_collab.get("city")
    if not my_city or not other_city:
        return None
    if my_city == other_city:
        my_campus, other_campus = me_collab.get("campus"), other_collab.get("campus")
        if my_campus and other_campus:
            return 1.0 if my_campus == other_campus else 0.75
        return 0.9
    if me_collab.get("online_ok") and other_collab.get("online_ok"):
        return 0.6
    return 0.2


def _role_ratio(a, b) -> float | None:
    """角色偏好：主导 + 协作视为高互补。"""
    if not a or not b:
        return None
    if a in NEUTRAL_VALUES or b in NEUTRAL_VALUES:
        return 1.0
    if a == b:
        return 1.0
    return 0.85 if {a, b} == {"主导", "协作"} else 0.3


def time_score(me: dict, other: dict) -> float | None:
    """时间维度（0~100）：时长接近度 50% + 时段重合 30% + 长期/短期 20%。"""
    ma = me.get("availability") or {}
    oa = other.get("availability") or {}
    parts: list[tuple[float, float]] = []

    p = _hours_proximity(ma.get("weekly_hours"), oa.get("weekly_hours"))
    if p is not None:
        parts.append((p, 0.5))
    j = _jaccard(ma.get("slots"), oa.get("slots"))
    if j is not None:
        parts.append((j, 0.3))
    t = _ratio(ma.get("term"), oa.get("term"), same=1.0, diff=0.4)
    if t is not None:
        parts.append((t, 0.2))

    if not parts:
        return None
    total_w = sum(w for _, w in parts)
    return round(sum(v * w for v, w in parts) / total_w * 100, 1)


def ability_score(me: dict, other: dict, match_type: str) -> tuple[float, float, float]:
    """能力维度（0~100）：标签相似 60% + 标签互补 40%；项目搭子叠加问卷自评。

    返回 (分数, 相似分, 互补分)。
    """
    sim = similarity_ratio(me.get("tags", []), other.get("tags", []))
    comp = min(complement_score(me.get("tags", []), other.get("tags", [])) * 10, 100.0)
    base = sim * 0.6 + comp * 0.4
    kind = MATCH_TYPES.get(match_type, MATCH_TYPES["interest"])
    if kind["requires_questionnaire"]:
        q = questionnaire_match(me.get("questionnaire", {}), other.get("questionnaire", {}))
        base = base * 0.75 + q * 0.25
    return round(min(base, 100.0), 1), sim, round(comp, 1)


def style_score(me: dict, other: dict) -> float | None:
    """合作方式维度（0~100）：线上线下 / 角色 / 回复 / 见面 / 地点。"""
    mc = me.get("collab") or {}
    oc = other.get("collab") or {}
    parts: list[tuple[float, float]] = []

    for value, weight in (
        (_ratio(mc.get("channel"), oc.get("channel"), diff=0.4), 0.30),
        (_role_ratio(mc.get("role"), oc.get("role")), 0.20),
        (_ratio(mc.get("reply"), oc.get("reply"), diff=0.5), 0.15),
        (_ratio(mc.get("meeting"), oc.get("meeting"), diff=0.5), 0.15),
        (_location_ratio(mc, oc), 0.20),
    ):
        if value is not None:
            parts.append((value, weight))

    if not parts:
        return None
    total_w = sum(w for _, w in parts)
    return round(sum(v * w for v, w in parts) / total_w * 100, 1)


# ---------------------------------------------------------------
# 推荐理由（自然语言，供前端直接展示）
# ---------------------------------------------------------------
def build_reasons(me: dict, other: dict, detail: dict) -> list[str]:
    """根据各维度得分与知乎共同点生成推荐理由，最多 4 条。"""
    reasons: list[str] = []
    dims = detail["dimensions"]

    matched = detail["matched_purposes"]
    if matched:
        reasons.append(f"目标一致：你们都希望「{'、'.join(matched)}」")

    if dims.get("time", 0) >= 65:
        oa = other.get("availability") or {}
        ma = me.get("availability") or {}
        slots = [s for s in (ma.get("slots") or []) if s in (oa.get("slots") or [])]
        seg = f"每周可投入 {oa.get('weekly_hours', '?')} 小时"
        if slots:
            seg += f"，都偏好「{'、'.join(slots)}」"
        reasons.append(f"时间匹配：{seg}")

    shared_tags = detail["shared_tags"]
    if shared_tags:
        reasons.append(f"方向相近：共同标签「{'、'.join(shared_tags[:3])}」")
    elif dims.get("ability", 0) >= 60:
        reasons.append("能力互补：你的技能与 TA 的方向形成互补")

    if dims.get("style", 0) >= 75:
        reasons.append("合作方式接近：线上/线下偏好与投入节奏比较一致")

    if detail["shared_zhihu_topics"]:
        topics = detail["shared_zhihu_topics"][:3]
        reasons.append(f"知乎同好：共同关注「{'、'.join(topics)}」等话题")
    if detail["shared_zhihu_contents"]:
        item = detail["shared_zhihu_contents"][0]
        reasons.append(f"知乎同好：都看过《{item['title']}》")

    return reasons[:4]


def score_match(me: dict, other: dict, match_type: str,
                use_mbti: bool = True, purposes: list[str] | None = None) -> dict:
    """计算两个用户在某匹配类型下的综合得分及可解释明细。

    score 为 0~100 的加权分；某项无法计算（如缺少时间安排、缺少 MBTI）时，
    该维度会被自动剔除并对剩余权重重新归一化，避免分数塌缩。
    purposes 为「我寻找搭子的目的」列表；缺省时使用我画像中的目的。
    """
    my_purposes = purposes if purposes else list(me.get("purposes", []))

    dims: dict[str, float] = {}

    goal, matched_purposes = purpose_match(my_purposes, other.get("purposes", []))
    if my_purposes:
        dims["goal"] = goal

    t = time_score(me, other)
    if t is not None:
        dims["time"] = t

    ability, sim, comp = ability_score(me, other, match_type)
    dims["ability"] = ability

    style = style_score(me, other)
    if style is not None:
        dims["style"] = style

    other_mbti = other.get("mbti") or None
    mbti_score = 0.0
    if use_mbti and me.get("mbti") and other_mbti:
        mbti_score = mbti.complement_score(me.get("mbti"), other_mbti)
        dims["mbti"] = mbti_score

    total_weight = sum(WEIGHTS[k] for k in dims)
    base = sum(dims[k] * WEIGHTS[k] for k in dims) / total_weight if total_weight else 0.0
    score = round(min(max(base, 0.0), 100.0), 1)

    shared = zhihu.shared_with(me.get("id", ""), other.get("id", ""))

    detail = {
        "similarity": sim,
        "complement": comp,
        "shared_tags": sorted(tag_intersection(me.get("tags", []), other.get("tags", []))),
        "mbti": other_mbti,
        "mbti_score": mbti_score,
        "purpose_score": goal,
        "matched_purposes": matched_purposes,
        # 可解释拆解：每一项的得分与实际参与归一化的权重
        "dimensions": {k: dims[k] for k in DIM_ORDER if k in dims},
        "weights": {k: round(WEIGHTS[k] * 100) for k in DIM_ORDER if k in dims},
        "breakdown": [
            {"key": k, "label": DIM_LABELS[k], "score": dims[k], "weight": round(WEIGHTS[k] * 100)}
            for k in DIM_ORDER if k in dims
        ],
        # 知乎特色
        "shared_zhihu_topics": shared["topics"],
        "shared_zhihu_contents": shared["contents"],
        "zhihu_source": zhihu.get_profile(me.get("id", "")).get("source", ""),
    }
    detail["reasons"] = build_reasons(me, other, detail)
    return {"match_type": match_type, "score": score, "detail": detail}


def rank_candidates(me: dict, candidates: list[dict], match_type: str,
                    top_n: int = 10, use_mbti: bool = True,
                    purposes: list[str] | None = None) -> list[dict]:
    """对候选搭子打分并排序，返回前 top_n 名。

    每个候选返回 : {candidate, score, detail}
    use_mbti=False 时匹配不依赖性格维度。
    purposes 为「我寻找搭子的目的」，参与目标维度打分。
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
