"""MBTI 性格测试题库（28 题精简版）。

来源：同济大学浙江学院《自我性格探索—MBTI 性格测试》精简版。
每题两个选项，选项标注维度字母：E/I、S/N、T/F、J/P。
已修正原网页第 8 题维度标注笔误（A=按当天心情去做 P，B=照拟好的程序表去做 J）。
"""

from __future__ import annotations

# 维度字母顺序，用于计分与比较
DIM_ORDER = ["E", "I", "S", "N", "T", "F", "J", "P"]

# 四对维度：用于合成类型（平分时的默认值）
DIM_PAIRS = [
    ("E", "I", "N"),  # 精力来源：平分取 N 不存在，占位（E/I 平分场景需求文档未给出，取 E）
    ("S", "N", "N"),
    ("T", "F", "F"),
    ("J", "P", "P"),
]

QUIZ: list[dict] = [
    {"id": 1, "text": "当你要外出一整天，你会", "options": [
        {"option": "A", "text": "计划你要做什么和在什么时候做", "dim": "J"},
        {"option": "B", "text": "说去就去", "dim": "P"},
    ]},
    {"id": 2, "text": "你是否", "options": [
        {"option": "A", "text": "容易让人了解", "dim": "E"},
        {"option": "B", "text": "难于让人了解", "dim": "I"},
    ]},
    {"id": 3, "text": "你认为自己是一个", "options": [
        {"option": "A", "text": "较为随兴所至的人", "dim": "P"},
        {"option": "B", "text": "较为有条理的人", "dim": "J"},
    ]},
    {"id": 4, "text": "假如你是一位老师，你会选教", "options": [
        {"option": "A", "text": "以事实为主的课程", "dim": "S"},
        {"option": "B", "text": "涉及理论的课程", "dim": "N"},
    ]},
    {"id": 5, "text": "处理许多事情上，你会喜欢", "options": [
        {"option": "A", "text": "凭兴所至行事", "dim": "P"},
        {"option": "B", "text": "按照计划行事", "dim": "J"},
    ]},
    {"id": 6, "text": "下面哪个词语更合我心意", "options": [
        {"option": "A", "text": "仁慈慷慨的", "dim": "F"},
        {"option": "B", "text": "意志坚定的", "dim": "T"},
    ]},
    {"id": 7, "text": "按照程序表做事", "options": [
        {"option": "A", "text": "合你心意", "dim": "J"},
        {"option": "B", "text": "令你感到束缚", "dim": "P"},
    ]},
    {"id": 8, "text": "你做事多数是", "options": [
        {"option": "A", "text": "按当天心情去做", "dim": "P"},
        {"option": "B", "text": "照拟好的程序表去做", "dim": "J"},
    ]},
    {"id": 9, "text": "你倾向", "options": [
        {"option": "A", "text": "重视感情多于逻辑", "dim": "F"},
        {"option": "B", "text": "重视逻辑多于感情", "dim": "T"},
    ]},
    {"id": 10, "text": "与很多人一起会", "options": [
        {"option": "A", "text": "令你活力倍增", "dim": "E"},
        {"option": "B", "text": "常常令你心力憔悴", "dim": "I"},
    ]},
    {"id": 11, "text": "当你有一份特别的任务，你会喜欢", "options": [
        {"option": "A", "text": "开始前小心组织计划", "dim": "J"},
        {"option": "B", "text": "边做边找须做什么", "dim": "P"},
    ]},
    {"id": 12, "text": "在大多数情况下，你会选择", "options": [
        {"option": "A", "text": "顺其自然", "dim": "P"},
        {"option": "B", "text": "按程序表做事", "dim": "J"},
    ]},
    {"id": 13, "text": "你通常", "options": [
        {"option": "A", "text": "与人容易混熟", "dim": "E"},
        {"option": "B", "text": "比较沉静或矜持", "dim": "I"},
    ]},
    {"id": 14, "text": "哪些人会更吸引你？", "options": [
        {"option": "A", "text": "一个思想敏捷及非常聪颖的人", "dim": "N"},
        {"option": "B", "text": "实事求是、具丰富常识的人", "dim": "S"},
    ]},
    {"id": 15, "text": "大多数人会说你是一个", "options": [
        {"option": "A", "text": "重视自我隐私的人", "dim": "I"},
        {"option": "B", "text": "非常坦率开放的人", "dim": "E"},
    ]},
    {"id": 16, "text": "在一大群人当中，通常是", "options": [
        {"option": "A", "text": "你介绍大家认识", "dim": "E"},
        {"option": "B", "text": "别人介绍你", "dim": "I"},
    ]},
    {"id": 17, "text": "哪个是较高的赞誉，或称许为", "options": [
        {"option": "A", "text": "能干的", "dim": "T"},
        {"option": "B", "text": "富有同情心", "dim": "F"},
    ]},
    {"id": 18, "text": "你喜欢花很多的时间", "options": [
        {"option": "A", "text": "一个人独处", "dim": "I"},
        {"option": "B", "text": "合别人在一起", "dim": "E"},
    ]},
    {"id": 19, "text": "一般来说，你和哪些人比较合得来？", "options": [
        {"option": "A", "text": "富于想象力的人", "dim": "N"},
        {"option": "B", "text": "现实的人", "dim": "S"},
    ]},
    {"id": 20, "text": "你宁愿被人认为是一个", "options": [
        {"option": "A", "text": "实事求是的人", "dim": "S"},
        {"option": "B", "text": "机灵的人", "dim": "N"},
    ]},
    {"id": 21, "text": "哪个是较高的赞誉，或称许为？", "options": [
        {"option": "A", "text": "一贯感性的人", "dim": "F"},
        {"option": "B", "text": "一贯理性的人", "dim": "T"},
    ]},
    {"id": 22, "text": "你会跟哪些人做朋友？", "options": [
        {"option": "A", "text": "常提出新主意的人", "dim": "N"},
        {"option": "B", "text": "脚踏实地的人", "dim": "S"},
    ]},
    {"id": 23, "text": "要作决定时，你认为比较重要的是", "options": [
        {"option": "A", "text": "据事实衡量", "dim": "T"},
        {"option": "B", "text": "考虑他人的感受和意见", "dim": "F"},
    ]},
    {"id": 24, "text": "要做许多人也做的事，你比较喜欢", "options": [
        {"option": "A", "text": "按照一般认可的方法去做", "dim": "S"},
        {"option": "B", "text": "构想一个自己的想法", "dim": "N"},
    ]},
    {"id": 25, "text": "在社交聚会中，你", "options": [
        {"option": "A", "text": "有时感到郁闷", "dim": "I"},
        {"option": "B", "text": "常常乐在其中", "dim": "E"},
    ]},
    {"id": 26, "text": "下面哪个词语更合我心意", "options": [
        {"option": "A", "text": "实际", "dim": "T"},
        {"option": "B", "text": "多愁善感", "dim": "F"},
    ]},
    {"id": 27, "text": "你通常较喜欢的科目是", "options": [
        {"option": "A", "text": "讲授概念和原则的", "dim": "N"},
        {"option": "B", "text": "讲授事实和数据的", "dim": "S"},
    ]},
    {"id": 28, "text": "你是否经常让", "options": [
        {"option": "A", "text": "你的情感支配你的理智", "dim": "F"},
        {"option": "B", "text": "你的理智主宰你的情感", "dim": "T"},
    ]},
]

# 校验：题目数
assert len(QUIZ) == 28, "MBTI 题库应为 28 题"


def get_quiz() -> list[dict]:
    return QUIZ