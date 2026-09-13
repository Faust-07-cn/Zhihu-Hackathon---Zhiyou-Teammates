"""知乎内容接入层（当前为演示 Mock，已按真实接口字段预留替换点）。

当前实现：内置演示用的「知乎画像」Mock 数据，字段结构对齐知乎开放平台真实响应，
         上游（matching.py / routers）只依赖本模块的函数与字段名，后续替换为真实接口
         时不需要改动上游数据结构。

真实接口（数据结构已预留，接入时替换 _MOCK 查询为真实 HTTP 调用即可）：
1. 授权用户基础信息   GET https://openapi.zhihu.com/user
       Header: Authorization: Bearer <oauth_access_token>
       字段: uid / hash_id / fullname / gender / headline / description / avatar_path / url
2. 用户创作列表       GET https://developer.zhihu.com/api/v1/user/contents
       Header: Authorization: Bearer <access_secret> + X-OAuth-Token: <oauth_access_token>
       字段: Items[].{ContentType, Url, CreatedAt, LikeCount, CommentCount,
                      FavoriteCount, Title, Summary}
3. 用户近期收藏       GET https://developer.zhihu.com/api/v1/user/collections
       字段: Items[].{...同上, FavTime, Favlists}
   鉴权与分页约定见知乎开放平台「用户数据 API」文档。

注意：uid 在真实接口中是 int64，可能超过 JS 安全整数范围，接入时需无损解析并以字符串传递。
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

# 数据来源标记：接入真实接口后置为 "zhihu_openapi"
SOURCE_MOCK = "mock"


def _item(content_type: str, title: str, summary: str, url: str,
          created_at: int, like: int = 0, comment: int = 0, favorite: int = 0) -> dict:
    """构造一条内容，字段名对齐 /api/v1/user/contents 的 ContentItem。"""
    return {
        "ContentType": content_type,      # answer | article | zvideo | pin | question
        "Url": url,
        "CreatedAt": created_at,          # 秒级时间戳
        "LikeCount": like,
        "CommentCount": comment,
        "FavoriteCount": favorite,
        "Title": title,
        "Summary": summary,
    }


def _collection_item(base: dict, fav_time: int, favlist: str) -> dict:
    """收藏内容：在 ContentItem 基础上追加 FavTime / Favlists（对齐 CollectionContentItem）。

    真实响应中收藏项作者字段为可选（Author），此处省略以兼容缺失字段。
    """
    return {**base, "FavTime": fav_time, "Favlists": [{"UrlToken": 0, "Title": favlist, "Url": ""}]}


# ---------------------------- 演示用知乎画像 Mock ----------------------------
# 说明：这组数据仅用于黑客松 Demo，页面上会标注「演示数据」，不代表真实知乎账号内容。
ZHIHU_PROFILES: dict[str, dict] = {
    "u01": {
        "source": SOURCE_MOCK,
        "profile": {
            "uid": 1001,
            "hash_id": "mock-u01",
            "fullname": "阿晚",
            "headline": "算法竞赛 / ACM 爱好者",
            "description": "计科在读，主攻算法与数据结构，打过两年校赛。",
            "avatar_path": "",
            "url": "https://www.zhihu.com/people/mock-u01",
        },
        "topics": ["算法", "ACM 竞赛", "数学建模", "动态规划", "编程"],
        "contents": [
            _item("answer", "ACM 校赛组队应该注意什么？",
                  "从分工、训练节奏和补题复盘三个角度说说我的经验。",
                  "https://www.zhihu.com/answer/1001", 1757000000, 236, 48, 120),
            _item("article", "动态规划：从记忆化搜索到状态压缩",
                  "用一个背包例子串起 DP 的常见优化路径。",
                  "https://zhuanlan.zhihu.com/p/1002", 1756600000, 158, 22, 96),
        ],
        "collections": [
            _collection_item(
                _item("article", "2026 美赛 MCM/ICM 题型评析",
                      "今年题型的难点与选题建议。",
                      "https://zhuanlan.zhihu.com/p/2001", 1757200000, 412, 66, 528),
                1757500000, "竞赛收藏夹"),
        ],
    },
    "u02": {
        "source": SOURCE_MOCK,
        "profile": {
            "uid": 1002,
            "hash_id": "mock-u02",
            "fullname": "南风",
            "headline": "数学建模 / 论文写作",
            "description": "信息学院，做建模和论文写作，偏好长期合作。",
            "avatar_path": "",
            "url": "https://www.zhihu.com/people/mock-u02",
        },
        "topics": ["数学建模", "论文写作", "数据分析", "美赛", "编程"],
        "contents": [
            _item("article", "数学建模论文排版的 10 个细节",
                  "摘要、图表、公式编号的规范写法。",
                  "https://zhuanlan.zhihu.com/p/2002", 1756800000, 176, 30, 143),
        ],
        "collections": [
            _collection_item(
                _item("article", "2026 美赛 MCM/ICM 题型评析",
                      "今年题型的难点与选题建议。",
                      "https://zhuanlan.zhihu.com/p/2001", 1757200000, 412, 66, 528),
                1757420000, "建模学习"),
        ],
    },
    "u03": {
        "source": SOURCE_MOCK,
        "profile": {
            "uid": 1003,
            "hash_id": "mock-u03",
            "fullname": "阿澈",
            "headline": "UI 设计 / 答辩展示",
            "description": "设计学院，做界面与答辩材料，喜欢和产品、开发一起组队。",
            "avatar_path": "",
            "url": "https://www.zhihu.com/people/mock-u03",
        },
        "topics": ["UI 设计", "产品设计", "答辩", "用户体验"],
        "contents": [
            _item("answer", "零基础如何入门 UI 设计？",
                  "从临摹、组件规范到作品集的整理顺序。",
                  "https://www.zhihu.com/answer/1003", 1756500000, 302, 57, 210),
        ],
        "collections": [
            _collection_item(
                _item("answer", "产品经理校招需要哪些能力？",
                      "需求分析、数据意识与跨团队协作的侧重点。",
                      "https://www.zhihu.com/answer/1006", 1757300000, 388, 91, 264),
                1757480000, "产品入门"),
        ],
    },
    "u04": {
        "source": SOURCE_MOCK,
        "profile": {
            "uid": 1004,
            "hash_id": "mock-u04",
            "fullname": "细雪",
            "headline": "英语学习 / 翻译",
            "description": "外国语学院，做英语写作与翻译，习惯每日打卡。",
            "avatar_path": "",
            "url": "https://www.zhihu.com/people/mock-u04",
        },
        "topics": ["英语学习", "翻译", "写作", "考研"],
        "contents": [
            _item("article", "六级 600 分备考计划（附每日打卡表）",
                  "词汇、听力、阅读、写作四块的分配方式。",
                  "https://zhuanlan.zhihu.com/p/2004", 1756400000, 246, 44, 178),
        ],
        "collections": [
            _collection_item(
                _item("article", "考研英语一 136 分经验分享",
                      "阅读精读与作文模板的自查方法。",
                      "https://zhuanlan.zhihu.com/p/2005", 1757350000, 512, 88, 402),
                1757460000, "考研资料"),
        ],
    },
    "u05": {
        "source": SOURCE_MOCK,
        "profile": {
            "uid": 1005,
            "hash_id": "mock-u05",
            "fullname": "黎觞",
            "headline": "嵌入式 / 软硬结合项目",
            "description": "机械学院，做嵌入式方向的软硬结合项目，能带队。",
            "avatar_path": "",
            "url": "https://www.zhihu.com/people/mock-u05",
        },
        "topics": ["嵌入式", "编程", "竞赛", "硬件"],
        "contents": [
            _item("article", "嵌入式项目如何选型：从需求反推方案",
                  "主控、传感器与通信方式的取舍思路。",
                  "https://zhuanlan.zhihu.com/p/2006", 1756700000, 132, 19, 87),
        ],
        "collections": [
            _collection_item(
                _item("answer", "ACM 校赛组队应该注意什么？",
                      "从分工、训练节奏和补题复盘三个角度说说我的经验。",
                      "https://www.zhihu.com/answer/1001", 1757000000, 236, 48, 120),
                1757440000, "编程学习"),
        ],
    },
    "u06": {
        "source": SOURCE_MOCK,
        "profile": {
            "uid": 1006,
            "hash_id": "mock-u06",
            "fullname": "星野",
            "headline": "产品 / 商业分析",
            "description": "经管学院，偏产品与商业分析，也在准备考研。",
            "avatar_path": "",
            "url": "https://www.zhihu.com/people/mock-u06",
        },
        "topics": ["产品", "商业分析", "答辩", "数据分析", "考研"],
        "contents": [
            _item("answer", "产品经理校招需要哪些能力？",
                  "需求分析、数据意识与跨团队协作的侧重点。",
                  "https://www.zhihu.com/answer/1006", 1757300000, 388, 91, 264),
        ],
        "collections": [
            _collection_item(
                _item("article", "考研英语一 136 分经验分享",
                      "阅读精读与作文模板的自查方法。",
                      "https://zhuanlan.zhihu.com/p/2005", 1757350000, 512, 88, 402),
                1757470000, "考研资料"),
        ],
    },
}


def get_profile(user_id: str) -> dict:
    """返回用户的知乎画像。

    真实接入时在此调用：
        GET https://openapi.zhihu.com/user                （基础信息）
        GET https://developer.zhihu.com/api/v1/user/contents   （创作）
        GET https://developer.zhihu.com/api/v1/user/collections（近期收藏）
    并保持返回结构不变：{source, profile, topics, contents, collections}。
    """
    profile = ZHIHU_PROFILES.get(user_id)
    if not profile:
        return {"source": SOURCE_MOCK, "profile": {}, "topics": [], "contents": [], "collections": []}
    return profile


def _all_items(profile: dict) -> list[dict]:
    """把创作与收藏合并成统一列表，并标记来源类型（创作 / 收藏）。"""
    items = [{**it, "_kind": "创作"} for it in profile.get("contents", [])]
    items += [{**it, "_kind": "收藏"} for it in profile.get("collections", [])]
    return items


def shared_with(me_id: str, other_id: str) -> dict:
    """计算两人的共同知乎兴趣。

    返回 {"topics": [...], "contents": [{kind, content_type, title, url, excerpt}]}
    - topics：共同关注的话题
    - contents：标题相同的内容（回答 / 文章 / 收藏）
    """
    a = get_profile(me_id)
    b = get_profile(other_id)
    topics = sorted(set(a.get("topics", [])) & set(b.get("topics", [])))

    b_items = _all_items(b)
    contents: list[dict] = []
    seen: set[str] = set()
    for item in _all_items(a):
        title = item.get("Title") or ""
        if not title or title in seen:
            continue
        for other in b_items:
            if other.get("Title") == title:
                seen.add(title)
                contents.append({
                    "kind": item.get("_kind", ""),
                    "content_type": item.get("ContentType", ""),
                    "title": title,
                    "url": item.get("Url", ""),
                    "excerpt": item.get("Summary", ""),
                })
                break
    return {"topics": topics, "contents": contents}


# ---------------------------- 知乎搜索（真实接口 + Mock 降级） ----------------------------
# 真实接口：GET https://developer.zhihu.com/api/v1/content/zhihu_search
#   Header: Authorization: Bearer <access_secret> + X-Request-Timestamp: <unix_seconds>
#   Query : Query（必填）、Count（默认 10，最大 10）
# 响应：{Code, Message, Data:{HasMore, SearchHashId, Items[], EmptyReason}}
# Item 字段：Title/ContentType/ContentID/ContentText/Url/CommentCount/VoteUpCount/
#           AuthorName/AuthorAvatar/AuthorBadge/AuthorBadgeText/EditTime/AuthorityLevel/RankingScore
#
# 凭据未配置（ZHIHU_ACCESS_SECRET 为空）或真实调用失败时，返回与真实字段对齐的内置 Mock，
# 保证演示在前端始终可走通；拿到 Access Secret 后只需设置环境变量即切换为真实调用。


def _search_item(title: str, url: str, content_type: str, content_text: str,
                 author_name: str, vote_up: int, content_id: str) -> dict:
    """构造一条 zhihu_search 的 Item，字段名与真实响应一致。"""
    return {
        "Title": title,
        "ContentType": content_type,
        "ContentID": content_id,
        "ContentText": content_text,
        "Url": url,
        "CommentCount": 0,
        "VoteUpCount": vote_up,
        "AuthorName": author_name,
        "AuthorAvatar": "",
        "AuthorBadge": "",
        "AuthorBadgeText": "",
        "EditTime": 0,
        "AuthorityLevel": "2",
        "RankingScore": 0.0,
    }


# 演示用搜索库：按关键词命中相关的知乎内容（与用户画像 Mock 保持一致）
_MOCK_SEARCH_LIBRARY: list[dict] = [
    {"kws": ["数学建模", "美赛", "建模"], "item": _search_item(
        "2026 美赛 MCM/ICM 题型评析", "https://zhuanlan.zhihu.com/p/2001", "Article",
        "今年题型的难点与选题建议。", "竞赛漫谈", 412, "s2001")},
    {"kws": ["算法", "acm", "竞赛"], "item": _search_item(
        "ACM 校赛组队应该注意什么？", "https://www.zhihu.com/answer/1001", "Answer",
        "从分工、训练节奏和补题复盘三个角度说说我的经验。", "阿晚", 236, "s1001")},
    {"kws": ["动态规划", "dp"], "item": _search_item(
        "动态规划：从记忆化搜索到状态压缩", "https://zhuanlan.zhihu.com/p/1002", "Article",
        "用一个背包例子串起 DP 的常见优化路径。", "阿晚", 158, "s1002")},
    {"kws": ["英语", "六级", "考研"], "item": _search_item(
        "六级 600 分备考计划（附每日打卡表）", "https://zhuanlan.zhihu.com/p/2004", "Article",
        "词汇、听力、阅读、写作四块的分配方式。", "细雪", 246, "s2004")},
    {"kws": ["组队", "搭子", "项目", "产品"], "item": _search_item(
        "产品经理校招需要哪些能力？", "https://www.zhihu.com/answer/1006", "Answer",
        "需求分析、数据意识与跨团队协作的侧重点。", "星野", 388, "s1006")},
]

_MOCK_SEARCH_FALLBACK: list[dict] = [
    _search_item("校园搭子：怎么找一起备战的同学", "https://www.zhihu.com/question/demo1", "Question",
                 "从目标、时间、能力三个维度对号入座。", "校园百科", 0, "s9001"),
    _search_item("保研 vs 就业，大三下学期应该怎么选？", "https://www.zhihu.com/question/demo2", "Question",
                 "结合自身情况拆解两条路的取舍。", "校园百科", 0, "s9002"),
]


def _mock_search(query: str, count: int) -> list[dict]:
    q = (query or "").lower()
    matched = [entry["item"] for entry in _MOCK_SEARCH_LIBRARY
               if any(k in q for k in entry["kws"])]
    items = matched or _MOCK_SEARCH_FALLBACK
    return [{**item, "Url": "", "source": SOURCE_MOCK} for item in items[:count]]


class SearchUnavailable(Exception):
    pass


def _failure_reason(code, message="") -> str:
    # 上游文案仅用于分类；对客户端只返回固定枚举，不能泄露上游异常或凭据。
    text = f"{code} {message}".lower()
    if str(code) == "429" or any(s in text for s in ("quota", "rate_limit", "rate limit", "额度", "配额", "频率", "限流")):
        return "quota_exceeded"
    if str(code) in ("401", "403") or any(s in text for s in ("auth", "token", "secret", "鉴权", "认证", "凭据")):
        return "auth_failed"
    return "upstream_error"


def _real_search(query: str, count: int, secret: str) -> list[dict]:
    params = urllib.parse.urlencode({"Query": query, "Count": count})
    url = f"https://developer.zhihu.com/api/v1/content/zhihu_search?{params}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {secret}",
        "X-Request-Timestamp": str(int(time.time())),
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("Code") != 0:
        raise SearchUnavailable(_failure_reason(data.get("Code"), data.get("Message", "")))
    items = data["Data"]["Items"]
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise SearchUnavailable("upstream_error")
    return items


def search_zhihu(query: str, count: int = 10) -> dict:
    """站内搜索：优先调用真实接口，未配置凭据或失败时回退 Mock。

    返回 {"source": "mock"|"zhihu", "items": [Item...]}，Item 字段对齐 zhihu_search 响应。
    """
    query = query.strip()
    if not query:
        raise ValueError("搜索关键词不能为空")
    count = min(max(int(count or 10), 1), 10)
    secret = os.environ.get("ZHIHU_ACCESS_SECRET", "").strip()
    if not secret:
        reason = "missing_credentials"
    else:
        try:
            return {"source": "zhihu", "items": _real_search(query, count, secret)}
        except urllib.error.HTTPError as exc:
            reason = _failure_reason(exc.code)
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            reason = "network_error"
        except SearchUnavailable as exc:
            reason = exc.args[0]
        except Exception:
            reason = "upstream_error"
    return {"source": "mock", "items": _mock_search(query, count), "fallback_reason": reason}
