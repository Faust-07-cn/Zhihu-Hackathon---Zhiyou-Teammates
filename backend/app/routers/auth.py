"""知乎 OAuth 登录路由：发起登录 / 模拟授权页 / 回调 / 登录态 / 登出。

路由分两组：
- /api/auth/*       登录入口与登录态（login / me / logout）
- /api/zhihu/*      知乎回调（callback）与 Mock 授权页（mock_authorize）
"""
from __future__ import annotations

import urllib.parse

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse

from .. import auth, users
from ..routers.users import _public

router = APIRouter(prefix="/api/auth", tags=["auth"])
zhihu_router = APIRouter(prefix="/api/zhihu", tags=["auth"])


@router.get("/login")
def login(request: Request, redirect_to: str = "/pages/me.html"):
    """发起登录：真实模式 302 到知乎授权页；Mock 模式 302 到模拟授权页。"""
    redirect_to = auth.normalize_redirect_to(redirect_to)
    origin = auth.frontend_origin(request)
    state = auth.new_state(redirect_to, origin)
    if auth.mock_mode():
        return RedirectResponse(f"/api/zhihu/mock_authorize?state={state}", status_code=302)
    params = urllib.parse.urlencode({
        "redirect_uri": auth.REDIRECT_URI,
        "app_id": auth.APP_ID,
        "response_type": "code",
        "state": state,
    })
    return RedirectResponse(f"{auth.AUTHORIZE_URL}?{params}", status_code=302)


@zhihu_router.get("/mock_authorize")
def mock_authorize(state: str = ""):
    """模拟知乎授权页（仅 Mock 模式可达）。"""
    if not auth.mock_mode():
        raise HTTPException(404, "Not Found")
    if not auth.peek_state(state):
        return PlainTextResponse("登录状态已失效，请返回页面重新登录。", status_code=400)
    cards = "".join(
        f'<a class="card" href="/api/zhihu/callback?authorization_code=mock-{acct["uid"]}&state={state}">'
        f'{acct["fullname"]}<br><small>{acct["headline"]}</small></a>'
        for acct in auth.MOCK_OAUTH_ACCOUNTS
    )
    return HTMLResponse(
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>模拟知乎登录</title>"
        "<style>body{font-family:sans-serif;max-width:420px;margin:80px auto;line-height:1.6}"
        ".card{display:block;border:1px solid #ccc;border-radius:8px;padding:16px;margin:12px 0;"
        "text-decoration:none;color:#333}.card:hover{background:#f6f6f6}</style></head><body>"
        f"<h3>模拟知乎授权（Mock，未配置 App Key）</h3>{cards}"
        "<p style='color:#888;font-size:12px'>选择任一账号模拟完成知乎登录</p></body></html>"
    )


@zhihu_router.get("/callback")
def callback(authorization_code: str = "", code: str = "", state: str = ""):
    """知乎回调：校验 state → 换 token/取用户（或取 Mock 账号）→ 建档 → 建会话 → 种 cookie → 重定向。"""
    consumed = auth.consume_state(state)
    if consumed is None:
        return PlainTextResponse("登录状态已失效或已使用，请返回页面重新登录。", status_code=400)
    redirect_to, origin = consumed
    auth_code = authorization_code or code  # 实测主参数为 authorization_code，兼容 code
    try:
        if auth.mock_mode():
            identity, source = auth.mock_identity(auth_code), "mock"
        else:
            token = auth.exchange_token(auth_code)
            identity, source = auth.fetch_userinfo(token), "oauth"
        user_id = auth.user_id_for(identity)
        user, created = users.upsert_user(user_id, auth.identity_to_user_fields(identity, source))
        sid = auth.create_session(user_id, source)
    except auth.OAuthError:
        return RedirectResponse(
            auth.build_frontend_url(origin, redirect_to, {"oauth": "error"}), status_code=302
        )
    resp = RedirectResponse(
        auth.build_frontend_url(origin, redirect_to, {"oauth": "new" if created else "1"}),
        status_code=302,
    )
    resp.set_cookie(
        auth.COOKIE_NAME, sid,
        httponly=True, samesite="lax", max_age=auth.SESSION_TTL, path="/",
    )
    return resp


@router.get("/me")
def me(request: Request):
    """当前登录态：已登录返回用户公开信息，否则 authenticated=false。"""
    sid = request.cookies.get(auth.COOKIE_NAME)
    if not sid:
        return {"authenticated": False, "user": None}
    session = auth.get_session(sid)
    if not session:
        return {"authenticated": False, "user": None}
    user = users.get_user(session["user_id"])
    if not user:
        return {"authenticated": False, "user": None}
    pub = _public(user)
    needs_profile = not (user.get("school") or user.get("tags"))
    return {"authenticated": True, "auth_source": session["auth_source"], "user": pub, "needs_profile": needs_profile}


@router.post("/logout")
def logout(request: Request, response: Response):
    """登出：销毁会话并清除 Cookie（POST 防图片标签式登出）。"""
    sid = request.cookies.get(auth.COOKIE_NAME)
    if sid:
        auth.destroy_session(sid)
    response.delete_cookie(auth.COOKIE_NAME, path="/")
    return {"ok": True}
