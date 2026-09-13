"""轻量内存用户库。开发/MVP 阶段用 Mock 数据，后续替换为数据库。

注意：本文件仅用于本地演示，不持久化。接入数据库后直接替换
`list_users()` 与 `get_user()` 的实现即可。

「知乎画像」不放在这里，统一由 zhihu.py 提供（含真实接口预留），便于替换数据源。
"""

from __future__ import annotations
import copy
from .db import load, save

# 一套用于演示的候选用户池
# availability：时间安排（每周可投入时长 / 可约时段 / 长期或短期）
# collab      ：合作方式（线上线下偏好 / 主导协作 / 回复与见面习惯 / 地点）
USERS: list[dict] = [
    {
        "id": "u01",
        "name": "阿晚",
        "school": "计算机学院",
        "level": "LV 5",
        "score": 92,
        "mbti": "INTJ",
        "purposes": ["竞赛组队", "结伴学习"],
        "tags": ["算法", "编程", "竞赛", "数据结构"],
        "availability": {
            "weekly_hours": 15,
            "slots": ["工作日晚上", "周末"],
            "term": "长期",
        },
        "collab": {
            "channel": "线下优先",
            "role": "主导",
            "reply": "及时",
            "meeting": "高频",
            "city": "成都",
            "campus": "主校区",
            "online_ok": True,
        },
        "questionnaire": {
            "方向": "算法 / ACM 竞赛",
            "可投入时间": 15,
            "队长经验": True,
            "技能": ["编程", "算法"],
        },
    },
    {
        "id": "u02",
        "name": "南风",
        "school": "信息学院",
        "level": "LV 4",
        "score": 88,
        "mbti": "INFP",
        "purposes": ["竞赛组队", "结伴学习"],
        "tags": ["数学建模", "论文写作", "数据分析"],
        "availability": {
            "weekly_hours": 12,
            "slots": ["工作日晚上", "周末"],
            "term": "长期",
        },
        "collab": {
            "channel": "线下优先",
            "role": "协作",
            "reply": "日常",
            "meeting": "按需",
            "city": "成都",
            "campus": "主校区",
            "online_ok": True,
        },
        "questionnaire": {
            "方向": "数学建模 / 论文",
            "可投入时间": 12,
            "队长经验": False,
            "技能": ["论文写作", "数据分析"],
        },
    },
    {
        "id": "u03",
        "name": "阿澈",
        "school": "设计学院",
        "level": "LV 4",
        "score": 85,
        "mbti": "ENFP",
        "purposes": ["竞赛组队", "兴趣交流"],
        "tags": ["UI", "设计", "答辩", "产品"],
        "availability": {
            "weekly_hours": 10,
            "slots": ["工作日晚上"],
            "term": "短期",
        },
        "collab": {
            "channel": "均可",
            "role": "协作",
            "reply": "及时",
            "meeting": "按需",
            "city": "成都",
            "campus": "分校区",
            "online_ok": True,
        },
        "questionnaire": {
            "方向": "UI 设计 / 答辩",
            "可投入时间": 10,
            "队长经验": True,
            "技能": ["设计", "产品"],
        },
    },
    {
        "id": "u04",
        "name": "细雪",
        "school": "外国语学院",
        "level": "LV 3",
        "score": 80,
        "mbti": "ISFJ",
        "purposes": ["结伴学习", "兴趣交流"],
        "tags": ["写作", "翻译", "课程", "英语"],
        "availability": {
            "weekly_hours": 8,
            "slots": ["周末"],
            "term": "长期",
        },
        "collab": {
            "channel": "线上优先",
            "role": "协作",
            "reply": "日常",
            "meeting": "按需",
            "city": "成都",
            "campus": "主校区",
            "online_ok": True,
        },
        "questionnaire": {
            "方向": "英语写作 / 翻译",
            "可投入时间": 8,
            "队长经验": False,
            "技能": ["写作"],
        },
    },
    {
        "id": "u05",
        "name": "黎觞",
        "school": "机械学院",
        "level": "LV 4",
        "score": 87,
        "mbti": "ENTJ",
        "purposes": ["竞赛组队", "日常陪伴"],
        "tags": ["编程", "嵌入式", "竞赛", "项目"],
        "availability": {
            "weekly_hours": 14,
            "slots": ["工作日晚上", "周末"],
            "term": "长期",
        },
        "collab": {
            "channel": "线下优先",
            "role": "主导",
            "reply": "及时",
            "meeting": "高频",
            "city": "成都",
            "campus": "主校区",
            "online_ok": True,
        },
        "questionnaire": {
            "方向": "嵌入式 / 软硬结合",
            "可投入时间": 14,
            "队长经验": True,
            "技能": ["编程", "硬件"],
        },
    },
    {
        "id": "u06",
        "name": "星野",
        "school": "经管学院",
        "level": "LV 3",
        "score": 79,
        "mbti": "ESTJ",
        "purposes": ["竞赛组队", "考研搭子"],
        "tags": ["产品", "答辩", "商业分析", "数据分析"],
        "availability": {
            "weekly_hours": 11,
            "slots": ["工作日晚上", "周末"],
            "term": "短期",
        },
        "collab": {
            "channel": "均可",
            "role": "均可",
            "reply": "日常",
            "meeting": "按需",
            "city": "成都",
            "campus": "主校区",
            "online_ok": True,
        },
        "questionnaire": {
            "方向": "产品 / 商业分析",
            "可投入时间": 11,
            "队长经验": False,
            "技能": ["数据分析", "产品"],
        },
    },
]


def _users():
    data = load("users", None)
    if data is None:
        data = copy.deepcopy(USERS)
        save("users", data)
    return data


def list_users() -> list[dict]:
    return _users()


def get_user(user_id: str) -> dict | None:
    return next((u for u in _users() if u["id"] == user_id), None)


def set_user_mbti(user_id: str, mbti: str) -> bool:
    """写入用户 MBTI（内存态）。返回是否成功。"""
    user = get_user(user_id)
    if not user:
        return False
    user["mbti"] = mbti
    save("users", _users())
    return True


def update_user_profile(user_id: str, data: dict) -> dict | None:
    user = get_user(user_id)
    if not user:
        return None
    for key in ("name", "school", "tags", "purposes", "availability", "collab", "questionnaire"):
        if key in data:
            user[key] = data[key]
    save("users", _users())
    return user
