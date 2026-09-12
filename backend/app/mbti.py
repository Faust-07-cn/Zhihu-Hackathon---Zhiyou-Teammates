"""MBTI 计算与互补匹配逻辑。

计分：统计 8 个字母得分，然后按维度对比较（高者胜出，平分取默认字母），
合成四字母类型，如 E + N + F + P = ENFP。

互补模型：E 与 I 互补、S 与 N 互补、T 与 F 互补、J 与 P 互补。
各维度对互补权重不同（见下），表示「认知风格差异」对合作互补的贡献度。
"""

from __future__ import annotations

from .mbti_quiz import QUIZ

# 维度互补权重（%）
COMPLEMENT_WEIGHTS = {
    ("E", "I"): 15,
    ("I", "E"): 15,
    ("S", "N"): 40,
    ("N", "S"): 40,
    ("T", "F"): 30,
    ("F", "T"): 30,
    ("J", "P"): 15,
    ("P", "J"): 15,
}

# 每对维度从一个字母到其对立字母的映射
OPPOSITES = {
    "E": "I", "I": "E",
    "S": "N", "N": "S",
    "T": "F", "F": "T",
    "J": "P", "P": "J",
}

# 合成类型时，每对维度从左到右的默认字母（平分时采用默认）
PAIR_DEFAULTS = [
    ("E", "I", "E"),
    ("S", "N", "N"),
    ("T", "F", "F"),
    ("J", "P", "P"),
]

# 合法 MBTI 字母集合
VALID_LETTERS = {"E", "I", "S", "N", "T", "F", "J", "P"}


def validate_mbti(mbti: str) -> bool:
    """校验是否为合法类型（形如 INTJ / ENFP）。"""
    return bool(mbti) and len(mbti) == 4 and all(ch in VALID_LETTERS for ch in mbti)


def parse_dim(mbti: str) -> list[str]:
    """把 'INTJ' 拆为 4 个维度字母，顺序固定 E/I, S/N, T/F, J/P。

    输入需已通过 validate_mbti，否则返回空列表。
    """
    valid = validate_mbti(mbti)
    if not valid:
        return []
    result = []
    for a, b, _ in PAIR_DEFAULTS:
        if a in mbti:
            result.append(a)
        elif b in mbti:
            result.append(b)
    if len(result) != 4:
        return []
    return result


def compute_type(answers: dict) -> str:
    """根据答案（{题目id: 选项字母}）统计分数并合成 MBTI 类型。

    answers 形如 {1: "A", 2: "B", ...}，值为选项的 option 字段（A/B）。
    """
    scores = {ch: 0 for ch in "EI SN TF JP".replace(" ", "")}

    for q in QUIZ:
        qid = q["id"]
        chosen = answers.get(qid) or answers.get(str(qid))
        if not chosen:
            continue
        for opt in q["options"]:
            if opt["option"] == chosen:
                scores[opt["dim"]] += 1
                break

    result = []
    for a, b, default in PAIR_DEFAULTS:
        if scores[a] > scores[b]:
            result.append(a)
        elif scores[b] > scores[a]:
            result.append(b)
        else:
            result.append(default)
    return "".join(result)


def complement_score(mbti_a: str, mbti_b: str) -> float:
    """计算两个 MBTI 类型的互补得分（0~100）。

    同字母（一致）计 0，互补字母按权重加分；所有互补权重求和后归一化到 0~100。
    """
    if not mbti_a or not mbti_b:
        return 0.0
    a = parse_dim(mbti_a)
    b = parse_dim(mbti_b)
    if not a or not b:
        return 0.0

    total_weight = 0.0
    for ca, cb in zip(a, b):
        total_weight += COMPLEMENT_WEIGHTS.get((ca, cb), 0.0)
    return round(min(total_weight, 100.0), 1)


def dims_scores(mbti: str) -> dict:
    """返回类型的各维度字母对照（用于展示，非分数）。"""
    dims = parse_dim(mbti)
    if not dims:
        return {}
    return {"E/I": dims[0], "S/N": dims[1], "T/F": dims[2], "J/P": dims[3]}