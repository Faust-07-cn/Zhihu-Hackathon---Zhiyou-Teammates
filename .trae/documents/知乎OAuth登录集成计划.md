# 知乎 OAuth 登录 + 注册/身份展示 实施计划

## Context（背景）

用户要求"从头走一遍流程，将注册页展示为我"：在校园搭子应用中接入知乎 Hackathon OAuth 登录，登录后身份卡（[data-identity]，位于 index.html 与 pages/me.html）展示当前知乎用户本人，并支持"完善资料"（注册）步骤。当前应用仅有演示账号池（u01-u06）与演示账号切换器，me.html 中明确标注"此处后续接入知乎 OAuth 登录"。

已确认的决策：
1. **redirect_uri 尚未确定** → 用环境变量配置，默认 `http://localhost:8001/api/zhihu/callback`，本轮不做真实授权测试。
2. **需要 Mock 登录兜底**（App Key 未配置或未登记时走假账号完成全流程），沿用项目 `backend/app/zhihu.py` 的 Mock 降级模式。
3. **登录后以知乎身份为主**：登录后身份卡显示知乎用户并隐藏演示账号切换器；未登录时保留演示账号。

遵循官方 [hackathon-oauth.md](c:\Users\Faust\.trae-cn\builtin_skills\zhihu\references\hackathon-oauth.md) 安全要求：state 必须密码学随机、服务端保存、短 TTL、原子消费防重放；app_key 只存后端环境变量；OAuth token 只留服务端；浏览器仅持有 HttpOnly Cookie 会话标识；用户亲自完成知乎登录。

## 文件清单

### 新增
| 文件 | 说明 |
|---|---|
| `backend/app/auth.py` | OAuth/会话核心层：env 读取、state/session 进程内存储、urllib 换 token/取用户、Mock 账号、cookie 助手 |
| `backend/app/routers/auth.py` | 路由：login / mock_authorize / callback / me / logout（两个 router：`/api/auth` 与 `/api/zhihu`） |
| `backend/.env.example` | 环境变量模板（`.env` 已被 .gitignore 忽略） |

### 修改
| 文件 | 改动 |
|---|---|
| `backend/app/main.py` | 注册新增两个 router |
| `backend/app/users.py` | 新增 `upsert_user()` 自动建档 |
| `backend/app/routers/users.py` | `_public()` 增加 `zhihu_identity`（source=oauth/mock）分支 |
| `frontend/js/app.js` | 登录态检测、身份卡登录/登出按钮、切换器隐藏、注册预填、`api()` 带 cookie |
| `frontend/pages/me.html` | 编辑资料 modal 增加"昵称/学校"输入框；占位文案更新 |

不改动：`backend/app/routers/zhihu.py`、`backend/app/zhihu.py`（搜索与内容层）；OAuth 回调注册在 `/api/zhihu/callback`，与既有 `/api/zhihu/search` 共存。

## 后端设计

### `backend/app/auth.py`（核心层，仿照 zhihu.py 结构）
- 配置读取：`ZHIHU_OAUTH_APP_ID` / `APP_KEY` / `REDIRECT_URI`（默认 localhost:8001/api/zhihu/callback）/ `FRONTEND_ORIGIN`（默认 localhost:8000）/ `SESSION_TTL`（默认 604800）
- 微型 .env 加载器（模块导入时读 `backend/.env`，~15 行，不引入 python-dotenv）
- `mock_mode()`：无凭据或 `ZHIHU_OAUTH_FORCE_MOCK=1` 时返回 True
- `MOCK_OAUTH_ACCOUNTS`：2 个假账号（uid 用字符串，规避 int64 精度），含 fullname/headline/school 等
- state：`new_state(redirect_to, origin)`（`secrets.token_urlsafe(24)`，TTL 300s，存进程内 `_STATES`）、`consume_state(state)`（`dict.pop` 原子消费防重放）、`peek_state(state)`（mock 授权页存在性检查）
- 会话：`create_session/get_session/destroy_session`（进程内 `_SESSIONS`，sid=token_urlsafe(32)，HttpOnly cookie 承载）+ 懒清理 `_prune()`
- 真实 HTTP（urllib，无新依赖）：`exchange_token(code)` POST access_token 表单（app_id/app_key/grant_type/redirect_uri/code）；`fetch_userinfo(token)` GET /user，`Authorization: Bearer`
- 身份映射：`user_id_for(identity)` → `zhihu_{uid}`；`identity_to_user_fields()` 构造 user 字段（name=school 空时需用户补填）
- 前端 origin 推导：Origin → Referer → env 默认；open redirect 防护：`ALLOWED_REDIRECTS` 白名单

### `backend/app/routers/auth.py`
- `GET /api/auth/login?redirect_to=`：生成 state；Mock → 302 `/api/zhihu/mock_authorize?state=`；真实 → 302 知乎 authorize URL（**绝不带 app_key**）
- `GET /api/zhihu/mock_authorize?state=`（仅 Mock 可达）：渲染内联 HTML 模拟授权页，展示 2 个假账号卡片，链接到 `/api/zhihu/callback?authorization_code=mock-{uid}&state=`
- `GET /api/zhihu/callback?authorization_code=&state=`：`consume_state` 校验（失败返回 400 文案）→ Mock 取假账号 / 真实换 token+取用户 → `users.upsert_user` 建档 → `create_session` → `set_cookie(zhihu_session, HttpOnly, SameSite=Lax, max_age=TTL, path=/)` → 302 回前端 `?oauth=new`（新用户）或 `?oauth=1`
- `GET /api/auth/me`：读 cookie → 返回 `{authenticated, auth_source, user(_public), needs_profile}` 或 `{authenticated: false}`
- `POST /api/auth/logout`：销毁会话 + delete_cookie

### `backend/app/users.py`
- 新增 `upsert_user(user_id, data) -> (user, created)`：查找用户池，不存在则创建（id=`zhihu_{uid}`、name=fullname、level=LV 1、score=60、tags=[]、zhihu_identity），存在则更新 name/school/tags/zhihu_identity，`save("users", users)` 持久化

### `backend/app/routers/users.py`
- `_public()`：有 `zhihu_identity` 时 zhihu 摘要直接取自该字段（source=oauth/mock），否则走既有 `zhihu.get_profile` Mock 路径

### `backend/app/main.py`
- `from .routers import auth as oauth_router; app.include_router(oauth_router.router); app.include_router(oauth_router.zhihu_router)`

## 前端设计（`frontend/js/app.js`，行号已核实）

| 位置 | 改动 |
|---|---|
| L9-27 | `api()` 统一加 `credentials: "include"`；新增 `let authUser` / `initAuth()` 拉取 `/api/auth/me` |
| L12-14 | `currentUser()` 优先返回 `authUser ? authUser.id : localStorage...`，既有调用点自动以知乎身份运行 |
| L42-66 | `initAccountSwitcher()`：`authUser` 存在时不渲染；列表过滤掉 `zhihu_` 前缀用户 |
| L764-772 | `renderIdentity()` 三分支：已登录 → `identityHTML(authUser)` + 完善资料/退出登录按钮；未登录 → 演示身份 + "使用知乎账号登录" `<a href="${API_BASE}/api/auth/login?redirect_to=...">`（整页跳转以携带 Referer 推导前端源） |
| L774-798 | `identityHTML()`：source=oauth 时显示"已通过知乎登录"徽标；mbti 用 `authUser ? u.mbti : ...` 防演示 localStorage 污染 |
| L745-762 | `initProfileEditor()`：modal 增加昵称/学校字段；authUser 时直接 fill 知乎资料；保存时 name/school 一并提交，OAuth 用户把返回写回 `authUser` |
| L885-899 | DOMContentLoaded 首行 `await initAuth()`，再执行其余初始化 |
| 新增 | `logout()`（POST /api/auth/logout + reload）；`handleOAuthFlags()`（`?oauth=error` 弹提示；`?oauth=new` 自动打开资料 modal） |

### `frontend/pages/me.html`
- 编辑资料 modal（L80 单行 HTML）内、`data-profile-tags` 前插入昵称（`data-profile-name`）、学校（`data-profile-school`）两个 form-item
- L74-77 占位文案改为："已接入知乎 OAuth 登录：登录后身份卡展示知乎身份，未登录时使用演示账号。"

### `frontend/index.html`
- 身份卡全由 JS 渲染，无需功能性改动

## 配置（`.env.example`）
```
ZHIHU_OAUTH_APP_ID=
ZHIHU_OAUTH_APP_KEY=
ZHIHU_OAUTH_REDIRECT_URI=http://localhost:8001/api/zhihu/callback
FRONTEND_ORIGIN=http://localhost:8000
ZHIHU_OAUTH_FORCE_MOCK=0
ZHIHU_OAUTH_SESSION_TTL=604800
```
执行时创建本地 `backend/.env`（gitignore 已排除），按用户提供的信息填入 App ID 591 与 App Key。

## 验证步骤（Mock 模式端到端）

1. 后端 `cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8001`（不配凭据）；前端 `node server.js`；打开 http://localhost:8000
2. 未登录：身份卡显示演示账号 + "使用知乎账号登录"按钮；导航有演示账号切换器
3. 点登录 → 302 到 mock 授权页 → 选"浮士德" → callback → 302 回 `/pages/me.html?oauth=new`
4. 资料 modal 自动打开，昵称/学校已预填；补标签后保存 → 身份卡显示"浮士德" + "已通过知乎登录"徽标，切换器消失
5. 全站身份生效：搭子广场/推荐/发帖均以 `zhihu_99001` 运行
6. DevTools 确认 `zhihu_session` Cookie 为 HttpOnly；`/api/auth/me` 返回 `authenticated: true`
7. 退出登录 → 回未登录态（切换器恢复）
8. 防重放：新标签页重放 callback URL（含已用 state）→ 返回 400
9. curl 直验：`/api/auth/login` 302；带 cookie 请求 `/api/auth/me` 返回 `authenticated:true`

## 边界与安全
- app_key 只存在于后端环境变量与 POST 表单体，授权 URL/日志/前端不含
- uid 全程字符串化，避免 int64 精度问题
- 进程内 Map 仅适用单进程 Demo；`redirect_to` 白名单防开放重定向
