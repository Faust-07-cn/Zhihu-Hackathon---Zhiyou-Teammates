# 校园搭子 · 校园社交平台

> 知乎黑客松 2026 校园新锐季 Demo
>
> 面向校园场景，以**搭子匹配**和**校园讨论**为核心的社交平台。让「竞赛组队、课程互助、兴趣同好」更高效地被找到、被信任、被连接。

---

## 核心功能

### 1. 搭子匹配系统
- **三类搭子**：兴趣搭子 / 学习搭子 / 项目搭子（竞赛等）
- **多因子匹配算法**：标签相似度、能力互补、MBTI 性格互补、问卷一致性加权计算匹配度
- 首页展示「为你推荐搭子」，按匹配度排序

### 2. 搭子广场（类闲鱼请求流）
- 用户**自主发布搭子请求**：标题、类型、目的、标签、描述
- 意向者**表达意向**，发布者查看意向者画像与匹配分后**接受**，建立搭子关系
- 广场列表按「与我的匹配度」降序，支持按类型 / 目的筛选

### 3. 自定义问卷筛选
- 发布者可**设计单选题问卷**，并标记每题期望答案（如：每周可投入时间、擅长角色）
- 意向者必须**先填写问卷**才能表达意向，问卷命中率计入匹配分
- 提高项目搭子的准入门槛，筛出高质量队友

### 4. MBTI 性格画像
- 精简版 28 题 MBTI 问卷，用户使用前先作答确定画像；已知结果可跳过直接填写
- MBTI 用于匹配加分与个人主页展示

### 5. 校园讨论区
- 整合课程评价、学习经验、生活资讯等校园刚需话题的 UGC 内容流

### 6. 可信度体系
- 用户主页展示**搭子信评分**与 **LV 等级**，降低组队协作的信任成本

---

## 技术架构

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | 原生 HTML / CSS / JavaScript | 知乎设计语言（品牌蓝 #0084FF），静态多页应用，响应式布局 |
| 后端 | Python + FastAPI + uvicorn | RESTful API，CORS 已开启 |
| 数据 | 内存态存储 | 便于演示，接口预留数据库替换空间 |
| 预览 | Node.js 静态服务器 | 本地预览前端页面 |

---

## 目录结构

```
知乎黑客松/
├── frontend/                  # 前端（静态页面）
│   ├── index.html             # 首页（推荐流 + 搭子推荐）
│   ├── pages/
│   │   ├── requests.html      # 搭子广场（发布 / 意向 / 问卷）
│   │   ├── forum.html         # 讨论区
│   │   ├── mbti.html          # MBTI 问卷
│   │   └── me.html            # 我的（画像 / 可信度 / 我的请求）
│   ├── css/style.css          # 全局样式（知乎设计语言）
│   ├── js/app.js              # 前端交互逻辑
│   └── server.js              # 本地静态服务器（端口 8000）
├── backend/                   # 后端（FastAPI）
│   ├── run.py                 # 启动入口
│   ├── requirements.txt       # 依赖
│   └── app/
│       ├── main.py            # 应用入口（路由注册 / CORS）
│       ├── matching.py        # 匹配算法
│       ├── users.py           # 用户数据层
│       ├── requests.py        # 搭子请求数据层
│       ├── questionnaires.py  # 自定义问卷数据层
│       ├── mbti.py / mbti_quiz.py  # MBTI 题库与画像
│       └── routers/           # API 路由（match / mbti / requests）
└── *.md                       # 需求 / 流程 / 题库等文档
```

---

## 快速启动

### 1. 启动后端（FastAPI，端口 8001）

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

> Windows 上 `--reload` 可能无法检测文件变更，改代码后请手动重启后端。

### 2. 启动前端静态服务器（端口 8000）

```bash
cd frontend
node server.js
```

### 3. 访问

浏览器打开 **http://localhost:8000**（首页），API 文档见 http://localhost:8001/docs。

> 前后端分端口部署，前端通过 `http://localhost:8001` 跨域调用 API。

---

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/match/{user_id}` | 搭子匹配推荐（按类型 / top_n） |
| GET | `/api/requests?user_id=` | 搭子广场列表（按匹配度降序） |
| POST | `/api/requests` | 发布搭子请求（可携带问卷） |
| POST | `/api/requests/questionnaires` | 创建自定义问卷 |
| GET | `/api/requests/questionnaires/{qid}` | 查询问卷详情 |
| POST | `/api/requests/{id}/intent` | 表达意向（需问卷的先提交答案） |
| DELETE | `/api/requests/{id}/intent` | 取消意向 |
| POST | `/api/requests/{id}/accept` | 发布者接受意向者 |
| GET | `/api/requests/mine/{user_id}` | 我的请求（发布 + 意向） |
| GET | `/api/mbti/quiz` | 获取 MBTI 题库 |
| POST | `/api/mbti/result` | 提交答案计算 MBTI 结果 |

---

## 匹配算法

多因子加权计算用户与请求发布者（或用户之间）的匹配度：

- **标签匹配**：标签集合的 Jaccard 相似度 + 覆盖率
- **能力互补**：擅长的差异标签作为互补加分
- **问卷一致性**：命中发布者期望答案的比例（0~100）
- **MBTI 互补**：性格维度互补加分（未画像时降级为纯标签匹配，不阻塞浏览）

---

## 演示数据说明

- 后端内置多组演示用户、搭子请求与一份美赛队友筛选问卷（`q01`）
- 数据保存在内存中，重启后端即恢复初始状态
- 当前为单机 Demo，接口已按用户体系设计，可平滑替换为数据库与登录鉴权

---

## License

仅用于知乎黑客松 2026 校园新锐季参赛演示。
