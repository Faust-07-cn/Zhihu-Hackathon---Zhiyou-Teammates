"""知乎 OAuth 登录与会话核心层（真实 + Mock 降级）。

设计对齐 app/zhihu.py 的 Mock 降级模式：
- 配置了 ZHIHU_OAUTH_APP_ID / APP_KEY 时走真实知乎授权；
- 凭据缺失或 ZHIHU_OAUTH_FORCE_MOCK=1 时进入 Mock 模式，
  用假账号走通「登录 → 回调 → 建档 → 会话」的同一代码路径。

安全要求（对齐知乎开放平台黑客松 OAuth 文档）：
- state 密码学安全随机、服务端保存、短 TTL、原子消费防重放；
- app_key 只存在于后端环境变量，绝不进入 URL / 日志 / 前端；
- OAuth access_token 只留服务端，浏览器仅持有 HttpOnly Cookie 会话标识。
"""

from __future__ import annotations

import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------- 配置读取 ----------------------------

def _load_dotenv() -> None:
    """读取 backend/.env（已被 .gitignore 忽略），不引入额外依赖。"""
    p = Path(__file__).resolve().parent.parent / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

APP_ID = os.environ.get("ZHIHU_OAUTH_APP_ID", "").strip()
APP_KEY = os.environ.get("ZHIHU_OAUTH_APP_KEY", "").strip()
REDIRECT_URI = os.environ.get(
    "ZHIHU_OAUTH_REDIRECT_URI", "http://localhost:8001/api/zhihu/callback"
).strip()
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:8000").rstrip("/")
SESSION_TTL = int(os.environ.get("ZHIHU_OAUTH_SESSION_TTL", "604800"))
STATE_TTL = 300  # state 有效期 5 分钟

AUTHORIZE_URL = "https://openapi.zhihu.com/authorize"
TOKEN_URL = "https://openapi.zhihu.com/access_token"
USERINFO_URL = "https://openapi.zhihu.com/user"

COOKIE_NAME = "zhihu_session"

# 登录后允许跳转的前端页面（防开放重定向）
ALLOWED_REDIRECTS = {
    "/",
    "/index.html",
    "/pages/me.html",
    "/pages/requests.html",
    "/pages/forum.html",
    "/pages/mbti.html",
}

# 进程内存储：仅适用于单进程 Demo（与官方文档一致）；多实例部署需换 Redis/DB。
_STATES: dict[str, dict] = {}    # state -> {"expires": float, "redirect_to": str, "frontend_origin": str}
_SESSIONS: dict[str, dict] = {}  # sid -> {"user_id": str, "auth_source": str, "created_at": float, "expires_at": float}


class OAuthError(Exception):
    """上游失败。args[0] 为分类枚举：missing_credentials/auth_failed/network_error/upstream_error。"""


# ---------------------------- 模式与 Mock 账号 ----------------------------

def mock_mode() -> bool:
    """凭据未配置或强制 Mock 时返回 True（对齐 zhihu.search_zhihu 的降级结构）。"""
    forced = os.environ.get("ZHIHU_OAUTH_FORCE_MOCK", "") in ("1", "true", "True")
    return (not APP_ID or not APP_KEY) or forced


# 模拟知乎账号：uid 用字符串（真实接口 uid 为 int64，避免 JS 精度问题）
MOCK_OAUTH_ACCOUNTS: list[dict] = [
    {
        "uid": "99001",
        "hash_id": "mock-oauth-1",
        "fullname": "浮士德",
        "school": "某大学 · 计算机学院",
        "headline": "校园搭子 Demo 演示用户",
        "description": "通过 Mock 知乎登录创建的演示账号。",
        "avatar_path": "",
        "url": "https://www.zhihu.com/people/mock-oauth-1",
    },
    {
        "uid": "99002",
        "hash_id": "mock-oauth-2",
        "fullname": "林间",
        "school": "某大学 · 信息学院",
        "headline": "算法 / 开源爱好者",
        "description": "Mock 登录演示账号。",
        "avatar_path": "",
        "url": "https://www.zhihu.com/people/mock-oauth-2",
    },
]


def mock_identity(code: str) -> dict:
    """把 mock 授权码（mock-{uid}）映射到假账号；未命中回退第一个。"""
    if code and code.startswith("mock-"):
        uid = code[len("mock-"):]
        for acct in MOCK_OAUTH_ACCOUNTS:
            if acct["uid"] == uid:
                return acct
    return MOCK_OAUTH_ACCOUNTS[0]


# ---------------------------- state：生成 / 校验 / 原子消费 ----------------------------

def normalize_redirect_to(path: str) -> str:
    if path in ALLOWED_REDIRECTS:
        return path
    return "/pages/me.html"


def new_state(redirect_to: str, frontend_origin: str) -> str:
    _prune()
    state = secrets.token_urlsafe(24)
    _STATES[state] = {
        "expires": time.time() + STATE_TTL,
        "redirect_to": normalize_redirect_to(redirect_to),
        "frontend_origin": frontend_origin.rstrip("/"),
    }
    return state


def consume_state(state: str) -> tuple[str, str] | None:
    """原子消费（dict.pop 单步完成，防重复回调）；缺失、过期返回 None。"""
    _prune()
    entry = _STATES.pop(state, None)
    if not entry or entry["expires"] < time.time():
        return None
    return entry["redirect_to"], entry["frontend_origin"]


def peek_state(state: str) -> bool:
    """mock 授权页只做存在性检查（消费仍发生在 callback）。"""
    _prune()
    entry = _STATES.get(state)
    return bool(entry and entry["expires"] >= time.time())


# ---------------------------- 会话：创建 / 读取 / 销毁 ----------------------------

def create_session(user_id: str, auth_source: str) -> str:
    _prune()
    sid = secrets.token_urlsafe(32)
    _SESSIONS[sid] = {
        "user_id": user_id,
        "auth_source": auth_source,
        "created_at": time.time(),
        "expires_at": time.time() + SESSION_TTL,
    }
    return sid


def get_session(sid: str) -> dict | None:
    _prune()
    session = _SESSIONS.get(sid)
    if not session or session["expires_at"] < time.time():
        _SESSIONS.pop(sid, None)
        return None
    return session


def destroy_session(sid: str) -> None:
    _SESSIONS.pop(sid, None)


def _prune() -> None:
    """懒清理过期条目。"""
    now = time.time()
    for key, entry in list(_STATES.items()):
        if entry["expires"] < now:
            _STATES.pop(key, None)
    for key, entry in list(_SESSIONS.items()):
        if entry["expires_at"] < now:
            _SESSIONS.pop(key, None)


# ---------------------------- 真实 HTTP（urllib，无新依赖） ----------------------------

def exchange_token(code: str) -> str:
    """用 authorization code 换取 OAuth access_token。"""
    if not APP_ID or not APP_KEY:
        raise OAuthError("missing_credentials")
    data = urllib.parse.urlencode({
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise OAuthError(_failure_reason(exc.code)) from exc
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise OAuthError("network_error") from exc
    token = payload.get("access_token") if isinstance(payload, dict) else None
    if not token:
        raise OAuthError("auth_failed")
    return token


def fetch_userinfo(token: str) -> dict:
    """用 OAuth access_token 获取授权用户基础信息。"""
    req = urllib.request.Request(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise OAuthError(_failure_reason(exc.code)) from exc
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise OAuthError("network_error") from exc


def _failure_reason(code) -> str:
    """对客户端只返回固定枚举，不泄露上游异常或凭据。"""
    code = str(code)
    if code == "429":
        return "rate_limited"
    if code in ("401", "403"):
        return "auth_failed"
    return "upstream_error"


# ---------------------------- 身份 → 平台用户映射 ----------------------------

def user_id_for(identity: dict) -> str:
    """登录用户映射为平台 user id：zhihu_{uid}（uid 已字符串化）。"""
    return f"zhihu_{identity['uid']}"


def identity_to_user_fields(identity: dict, source: str) -> dict:
    """构造 upsert 用户字段；school/tags 留空由注册步骤补充。"""
    return {
        "name": identity.get("fullname") or f"知乎用户_{identity['uid']}",
        "school": identity.get("school", ""),
        "tags": [],
        "zhihu_identity": {
            "uid": str(identity["uid"]),
            "hash_id": identity.get("hash_id", ""),
            "fullname": identity.get("fullname", ""),
            "gender": identity.get("gender"),
            "headline": identity.get("headline", ""),
            "description": identity.get("description", ""),
            "avatar_path": identity.get("avatar_path", ""),
            "url": identity.get("url", ""),
            "source": source,  # "mock" | "oauth"
        },
    }


# ---------------------------- 前端 origin 推导与跳转构造 ----------------------------

def frontend_origin(request) -> str:
    """登录时推导前端源：Origin → Referer → env FRONTEND_ORIGIN → 默认值。"""
    for header in ("origin", "referer"):
        value = request.headers.get(header)
        if value:
            parsed = urllib.parse.urlparse(value)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
    return FRONTEND_ORIGIN


def build_frontend_url(origin: str, path: str, params: dict) -> str:
    qs = urllib.parse.urlencode(params)
    separator = "&" if "?" in path else "?"
    return f"{origin}{path}{separator}{qs}"
