"""MBTI 性格测试题库（28 题精简版）。

每题两个选项，选项标注维度字母：E/I、S/N、T/F、J/P。
每对维度各 7 题，保证四对维度题量均衡。
"""

from __future__ import annotations

# 维度字母顺序，用于计分与比较
DIM_ORDER = ["E", "I", "S", "N", "T", "F", "J", "P"]

# 四对维度：用于合成类型（平分时的默认值，与 mbti.PAIR_DEFAULTS 保持一致）
DIM_PAIRS = [
    ("E", "I", "E"),
    ("S", "N", "N"),
    ("T", "F", "F"),
    ("J", "P", "P"),
]

QUIZ: list[dict] = [
    {"id": 1, "text": "要外出一整天，你更可能", "options": [
        {"option": "A", "text": "提前想好去哪、几点做什么", "dim": "J"},
        {"option": "B", "text": "说走就走，到了再看", "dim": "P"},
    ]},
    {"id": 2, "text": "在别人眼里，你", "options": [
        {"option": "A", "text": "比较容易被人了解", "dim": "E"},
        {"option": "B", "text": "不太容易被人了解", "dim": "I"},
    ]},
    {"id": 3, "text": "你觉得自己更接近", "options": [
        {"option": "A", "text": "随性的人，想到什么做什么", "dim": "P"},
        {"option": "B", "text": "有条理的人，喜欢把事情安排清楚", "dim": "J"},
    ]},
    {"id": 4, "text": "假如你是老师，你更愿意教", "options": [
        {"option": "A", "text": "以事实和案例为主的课", "dim": "S"},
        {"option": "B", "text": "以理论和原理为主的课", "dim": "N"},
    ]},
    {"id": 5, "text": "同一时间有很多事要处理，你倾向于", "options": [
        {"option": "A", "text": "看当下状态，先做想做的", "dim": "P"},
        {"option": "B", "text": "按计划一件件推进", "dim": "J"},
    ]},
    {"id": 6, "text": "下面哪个词更贴近你", "options": [
        {"option": "A", "text": "仁慈、慷慨", "dim": "F"},
        {"option": "B", "text": "坚定、有主见", "dim": "T"},
    ]},
    {"id": 7, "text": "对于按日程表做事，你的感觉是", "options": [
        {"option": "A", "text": "挺好，正合我意", "dim": "J"},
        {"option": "B", "text": "有点被束缚", "dim": "P"},
    ]},
    {"id": 8, "text": "做事的时候，你通常是", "options": [
        {"option": "A", "text": "看当天心情决定怎么做", "dim": "P"},
        {"option": "B", "text": "照着事先定好的流程走", "dim": "J"},
    ]},
    {"id": 9, "text": "做判断时，你更看重", "options": [
        {"option": "A", "text": "感情和感受", "dim": "F"},
        {"option": "B", "text": "逻辑和道理", "dim": "T"},
    ]},
    {"id": 10, "text": "和很多人待在一起，通常", "options": [
        {"option": "A", "text": "让你更有活力", "dim": "E"},
        {"option": "B", "text": "让你觉得有点累", "dim": "I"},
    ]},
    {"id": 11, "text": "接到一项特别的任务，你更喜欢", "options": [
        {"option": "A", "text": "动手前先把计划理清楚", "dim": "J"},
        {"option": "B", "text": "先做起来，边做边看要补什么", "dim": "P"},
    ]},
    {"id": 12, "text": "大多数情况下，你会选择", "options": [
        {"option": "A", "text": "顺其自然", "dim": "P"},
        {"option": "B", "text": "按计划来", "dim": "J"},
    ]},
    {"id": 13, "text": "和陌生人相处时，你通常", "options": [
        {"option": "A", "text": "很快就能聊熟", "dim": "E"},
        {"option": "B", "text": "比较安静、慢热", "dim": "I"},
    ]},
    {"id": 14, "text": "下面哪种人更吸引你", "options": [
        {"option": "A", "text": "思维敏捷、点子多的人", "dim": "N"},
        {"option": "B", "text": "实事求是、常识丰富的人", "dim": "S"},
    ]},
    {"id": 15, "text": "身边的人大多觉得你", "options": [
        {"option": "A", "text": "比较注重个人空间和隐私", "dim": "I"},
        {"option": "B", "text": "坦率直接，有什么说什么", "dim": "E"},
    ]},
    {"id": 16, "text": "在一大群人里，通常是", "options": [
        {"option": "A", "text": "你主动把大家介绍到一起", "dim": "E"},
        {"option": "B", "text": "别人来介绍你", "dim": "I"},
    ]},
    {"id": 17, "text": "下面哪句夸奖更让你受用", "options": [
        {"option": "A", "text": "你很有能力", "dim": "T"},
        {"option": "B", "text": "你很有同理心", "dim": "F"},
    ]},
    {"id": 18, "text": "你更愿意把大量时间花在", "options": [
        {"option": "A", "text": "一个人独处", "dim": "I"},
        {"option": "B", "text": "和别人相处", "dim": "E"},
    ]},
    {"id": 19, "text": "一般来说，你和哪种人更合得来", "options": [
        {"option": "A", "text": "想象力丰富的人", "dim": "N"},
        {"option": "B", "text": "务实、接地气的人", "dim": "S"},
    ]},
    {"id": 20, "text": "你更希望别人觉得你", "options": [
        {"option": "A", "text": "实事求是", "dim": "S"},
        {"option": "B", "text": "机灵、有想法", "dim": "N"},
    ]},
    {"id": 21, "text": "下面哪句评价你更喜欢", "options": [
        {"option": "A", "text": "你很感性、有人情味", "dim": "F"},
        {"option": "B", "text": "你很理性、讲道理", "dim": "T"},
    ]},
    {"id": 22, "text": "你更容易和哪种人成为朋友", "options": [
        {"option": "A", "text": "常提出新点子的人", "dim": "N"},
        {"option": "B", "text": "脚踏实地的人", "dim": "S"},
    ]},
    {"id": 23, "text": "做决定时，你认为更重要的是", "options": [
        {"option": "A", "text": "依据事实和数据", "dim": "T"},
        {"option": "B", "text": "考虑他人的感受和意见", "dim": "F"},
    ]},
    {"id": 24, "text": "做一件很多人都做过的事，你更倾向", "options": [
        {"option": "A", "text": "按大家普遍认可的方法做", "dim": "S"},
        {"option": "B", "text": "自己重新想一套做法", "dim": "N"},
    ]},
    {"id": 25, "text": "在聚会场合，你", "options": [
        {"option": "A", "text": "有时会觉得有点闷", "dim": "I"},
        {"option": "B", "text": "常常很享受其中", "dim": "E"},
    ]},
    {"id": 26, "text": "下面哪个词更合你心意", "options": [
        {"option": "A", "text": "实际", "dim": "T"},
        {"option": "B", "text": "多愁善感", "dim": "F"},
    ]},
    {"id": 27, "text": "你更喜欢哪类课程", "options": [
        {"option": "A", "text": "讲概念和原理的", "dim": "N"},
        {"option": "B", "text": "讲事实和数据的", "dim": "S"},
    ]},
    {"id": 28, "text": "做判断时，你更常让", "options": [
        {"option": "A", "text": "情感影响你的结论", "dim": "F"},
        {"option": "B", "text": "理智主导你的选择", "dim": "T"},
    ]},
]

# 校验：题目数
assert len(QUIZ) == 28, "MBTI 题库应为 28 题"


def get_quiz() -> list[dict]:
    return QUIZ
