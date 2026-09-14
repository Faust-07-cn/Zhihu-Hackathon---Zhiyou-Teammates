# OAuth 登录同步调试

状态：[OPEN]

## 假设
1. 前端部署的是旧版本或浏览器缓存。
2. `/api/auth/me` 请求未携带 `zhihu_session` Cookie。
3. OAuth 回调后的进程内会话丢失。
4. CORS 允许来源与实际前端域名不一致。

## 运行时证据
待收集。
