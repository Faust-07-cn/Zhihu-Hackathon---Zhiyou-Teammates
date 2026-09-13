"""讨论区帖子本地存储（内存，不持久化）。

帖子为「站内发帖」的本地数据；其中的 `zhihu_refs` 是发帖时通过知乎搜索 API
引用到的知乎内容（回答/文章），用于体现「发帖接入知乎」的能力。真实接入后
可替换 `list_posts()` / `create_post()` 为数据库实现，数据结构保持不变。
"""

from __future__ import annotations
import copy
from .db import load, save

# 帖子字段说明：
#   id         帖子唯一标识
#   title      标题
#   excerpt    正文（摘要）
#   author     作者昵称
#   author_id  作者 user id（对应 users.py）
#   school     作者院系
#   tags       标签
#   channel    频道：搭子 / 课程 / 竞赛 / 生活
#   request    可转搭子的配置（None 表示纯内容帖，不显示「申请成为搭子」）
#   zhihu_refs 引用的知乎内容 [{title, url, author_name, content_type}]
#   likes/comments/time 展示字段
POSTS: list[dict] = []
COMMENTS: dict[str, list[dict]] = {}
LIKES: dict[str, set[str]] = {}


def _seed() -> list[dict]:
    """演示种子帖子，与首页推荐流内容保持一致。"""
    return [
        {
            "id": "p1",
            "title": "求队伍一起冲击 2026 美赛 M 奖，已有两位队友",
            "excerpt": "我们是一支新的队伍，想找一位擅长论文写作/建模的搭档补足团队拼图。周一三五晚有空，进度透明。",
            "author": "阿晚",
            "author_id": "u01",
            "school": "计算机学院",
            "tags": ["项目搭子", "数学建模", "组队"],
            "channel": "竞赛",
            "request": {"match_type": "project", "purposes": ["竞赛组队"]},
            "zhihu_refs": [],
            "likes": 132,
            "comments": 46,
            "time": "12 分钟前",
        },
        {
            "id": "p2",
            "title": "《操作系统》期末复习经验：别只看 PPT",
            "excerpt": "把重点放在三阶段：概念梳理 → 模拟卷 → 错题复盘。这里分享一份我自己整理的思维导图。",
            "author": "南风",
            "author_id": "u02",
            "school": "信息学院",
            "tags": ["课程评价", "学习经验"],
            "channel": "课程",
            "request": None,
            "zhihu_refs": [],
            "likes": 98,
            "comments": 23,
            "time": "1 小时前",
        },
        {
            "id": "p3",
            "title": "想找个志同道合的朋友一起做课程项目",
            "excerpt": "方向是前后端分离的小型管理系统，希望能力互补、能长期坚持。感兴趣的同学评论区聊聊。",
            "author": "阿澈",
            "author_id": "u03",
            "school": "设计学院",
            "tags": ["学习搭子", "项目", "前后端"],
            "channel": "搭子",
            "request": {"match_type": "project", "purposes": ["结伴学习"]},
            "zhihu_refs": [],
            "likes": 76,
            "comments": 31,
            "time": "3 小时前",
        },
        {
            "id": "p4",
            "title": "校园网爬梯子买书攻略 & 二手书流转群",
            "excerpt": "汇总了各书院二手书交易群号和靠谱平台，方便大家省钱又环保。持续更新，欢迎补充。",
            "author": "细雪",
            "author_id": "u04",
            "school": "外国语学院",
            "tags": ["生活资讯", "校园百科"],
            "channel": "生活",
            "request": None,
            "zhihu_refs": [],
            "likes": 210,
            "comments": 64,
            "time": "5 小时前",
        },
    ]


def _init() -> None:
    if not POSTS:
        POSTS.extend(load("posts", copy.deepcopy(_seed())))
    save("posts", POSTS)


def _new_id() -> str:
    return f"p{len(POSTS) + 1}"


def list_posts(channel: str | None = None) -> list[dict]:
    """返回帖子列表，按热度排序。"""
    _init()
    rows = list(POSTS) if channel in (None, "", "all") else [p for p in POSTS if p.get("channel") == channel]
    return sorted(rows, key=lambda p: p.get("likes", 0) * 2 + p.get("comments", 0), reverse=True)


def get_post(post_id: str) -> dict | None:
    _init()
    return next((p for p in POSTS if p["id"] == post_id), None)


def add_comment(post_id: str, user_id: str, author: str, content: str) -> dict | None:
    post = get_post(post_id)
    if not post or not content.strip():
        return None
    item = {"id": f"c{sum(len(v) for v in COMMENTS.values()) + 1}", "user_id": user_id, "author": author, "content": content.strip(), "time": "刚刚", "replies": []}
    COMMENTS.setdefault(post_id, []).append(item)
    post["comments"] = len(COMMENTS[post_id])
    save("posts", POSTS)
    return item


def list_comments(post_id: str) -> list[dict]:
    return COMMENTS.get(post_id, [])


def toggle_like(post_id: str, user_id: str) -> tuple[bool, int] | None:
    post = get_post(post_id)
    if not post:
        return None
    users = LIKES.setdefault(post_id, set())
    liked = user_id in users
    users.discard(user_id) if liked else users.add(user_id)
    post["likes"] = max(0, post.get("likes", 0) + (-1 if liked else 1))
    save("posts", POSTS)
    return not liked, post["likes"]


def create_post(*, author_id: str, author: str, school: str, title: str,
                content: str, channel: str, tags: list[str],
                zhihu_refs: list[dict], request: dict | None = None) -> dict:
    """创建一条新帖子（插入最前）。"""
    _init()
    post = {
        "id": _new_id(),
        "title": title,
        "excerpt": content,
        "author": author,
        "author_id": author_id,
        "school": school,
        "tags": tags or [],
        "channel": channel or "搭子",
        "request": request,
        "zhihu_refs": zhihu_refs or [],
        "likes": 0,
        "comments": 0,
        "time": "刚刚",
    }
    POSTS.insert(0, post)
    save("posts", POSTS)
    return post