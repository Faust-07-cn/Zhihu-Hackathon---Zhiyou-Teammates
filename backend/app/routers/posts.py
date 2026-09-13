"""讨论区帖子 API 路由。

提供发帖与帖子列表；发帖时可将通过知乎搜索引用的内容挂在 `zhihu_refs` 上。
"""
from __future__ import annotations

from typing import Literal
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import posts
from ..users import get_user

router = APIRouter(prefix="/api/posts", tags=["posts"])


class ZhihuRef(BaseModel):
    title: str = ""
    url: str = ""
    author_name: str = ""
    content_type: str = ""
    source: Literal["mock", "zhihu"] = "mock"


class CommentBody(BaseModel):
    user_id: str
    content: str


class LikeBody(BaseModel):
    user_id: str


class CreatePostBody(BaseModel):
    user_id: str
    request: dict | None = None
    title: str
    content: str = ""
    channel: str = "搭子"
    tags: list[str] = Field(default_factory=list)
    zhihu_refs: list[ZhihuRef] = Field(default_factory=list)


@router.get("")
def list_all(channel: str | None = None):
    """帖子列表，可按频道过滤（空 / all 表示全部）。"""
    return {"items": posts.list_posts(channel)}


@router.get("/{post_id}")
def detail(post_id: str):
    post = posts.get_post(post_id)
    if not post:
        raise HTTPException(404, "帖子不存在")
    return {"post": post, "comments": posts.list_comments(post_id)}


@router.post("/{post_id}/comments")
def comment(post_id: str, body: CommentBody):
    user = get_user(body.user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    item = posts.add_comment(post_id, body.user_id, user["name"], body.content)
    if not item:
        raise HTTPException(400, "评论不能为空或帖子不存在")
    return item


@router.post("/{post_id}/like")
def like(post_id: str, body: LikeBody):
    if not get_user(body.user_id):
        raise HTTPException(404, "用户不存在")
    result = posts.toggle_like(post_id, body.user_id)
    if not result:
        raise HTTPException(404, "帖子不存在")
    return {"liked": result[0], "likes": result[1]}


@router.post("")
def create(body: CreatePostBody):
    username_owner = get_user(body.user_id)
    if not username_owner:
        raise HTTPException(404, f"用户不存在: {body.user_id}")
    title = body.title.strip()
    if not title:
        raise HTTPException(400, "标题不能为空")
    refs = [r.model_dump() for r in body.zhihu_refs]
    for ref in refs:
        if ref["source"] == "mock":
            ref["url"] = ""
        elif ref["url"]:
            try:
                url = urlsplit(ref["url"])
                host = url.hostname or ""
                valid = (url.scheme == "https" and not url.username and not url.password
                         and (host == "zhihu.com" or host.endswith(".zhihu.com")))
            except ValueError:
                valid = False
            if not valid:
                raise HTTPException(400, "引用链接仅允许 HTTPS 知乎地址")
    return posts.create_post(
        author_id=username_owner["id"],
        author=username_owner["name"],
        school=username_owner["school"],
        title=title,
        content=body.content.strip(),
        channel=body.channel,
        tags=[t.strip() for t in body.tags if t.strip()],
        zhihu_refs=refs,
        request=body.request,
    )
