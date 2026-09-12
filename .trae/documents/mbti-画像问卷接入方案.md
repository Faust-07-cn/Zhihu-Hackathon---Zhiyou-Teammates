# 校园搭子 · MBTI 画像问卷接入方案

## Context（为什么做）

当前匹配 `backend/app/matching.py` 仅基于**标签相似 + 能力互补 + 问卷**打分，缺乏稳定的用户性格画像，匹配推荐精度有限。本需求引入 **MBTI 性格测试（28 题精简版）** 作为用户画像维度，让「先答后匹配」的平台流程能依据性格互补度推荐搭档。

已确认的设计决策：
- **互补类型优先**：MBTI 结果以「维度互补」方式参与匹配打分（非相同优先、非仅展示）。
- **先答后匹配**：用户在进入搭子匹配前需先完成 MBTI 问卷；已掌握自身 MBTI 的用户可直接填写类型跳过 28 题。

题库来源：`MBTI题库_精简版28题.md`（启用题干 + 选项 + 每选项对应的维度字母 E/I/S/N/T/F/J/P）。

## 匹配规则设计（可解释的 MBTI 互补模型）

MBTI 四个维度各自互补（两端相异即补满分值），四维度权重不同 —— 反映「认知风格差异」对合作互补的贡献度：

| 维度对 | 互补判定 | 权重 |
|--------|----------|------|
| S / N（感觉↔直觉：信息获取） | 相异即互补 | 40 |
| T / F（思考↔情感：决策方式） | 相异即互补 | 30 |
| E / I（外倾↔内倾：精力来源） | 相异即互补 | 15 |
| J / P（判断↔知觉：生活态度） | 相异即互补 | 15 |

`complement_score(mbti_a, mbti_b)` = 相异维度权重之和 / 100（取值范围 0~100）。
维度顺序固定为 E/I, S/N, T/F, J/P，便于按位比较。一致维度计 0，互补维度计权重。

### 综合打分整合（修改 `matching.score_match`）

在现有 `similarity + complement + questionnaire` 基础上增加 `mbti` 维度，并按场景调整权重：

- **interest / study**（低门槛）：`similarity*0.6 + mbti_mutual*0.4`
- **project**（高质量筛选）：`similarity*0.30 + tag_complement*0.15 + questionnaire*0.30 + mbti*0.25`

归一化后仍为 0~100，`detail` 增加 `mbti` 与 `mbti_score`，供前端展示「性格互补」。

## 后端改动

### 1. 新增题库数据 `backend/app/mbti_quiz.py`
- 从 md 解析为结构化数据，形如：
  ```python
  QUIZ = [
      {"id": 1, "text": "当你要外出一整天，你会", "options": [
          {"option": "A", "text": "计划你要做什么和在什么时候做", "dim": "J"},
          {"option": "B", "text": "说去就去", "dim": "P"},
      ]},
      ...
  ]
  ```
- `DIM_ORDER = ["E","I","S","N","T","F","J","P"]` 便于统计。

### 2. 新增逻辑 `backend/app/mbti.py`
- `compute_type(answers: dict[int, str]) -> str`：按 28 题逐题累加每个选中选项的维度字母（8 字母计分），再按计分规则判定四维度，合成 4 字母类型（E/I、S/N 平分取 N、T/F 平分取 F、J/P 平分取 P）。
- `validate_mbti(mbti: str) -> bool`：校验是否为合法类型（合法字母组合）。
- `complement_score(a: str, b: str) -> float`：MBTI 互补模型（见上表）。
- `parse_dim(mbti: str) -> list[str]`：把 "INTJ" 拆为按 DIM 权重比较的结构。

### 3. 用户池 `backend/app/users.py`
- 每个演示用户补充 `"mbti"` 字段（如 `"INTJ"`），保证演示时有互补差异：
  - u01 阿晚=INTJ、u05 黎觞=ENTJ（互补给算法/编程项目）
  - u02 南风=INFP、u04 细雪=ISFJ、u03 阿澈=ENFP、u06 星野=ESTJ
- 增加 `set_user_mbti(user_id, mbti)`（内存写入，MVP 阶段足够，持久化后续接入）。

### 4. 匹配入口 `backend/app/routers/match.py`
- `rank` 返回的每个候选 detail 增加 `mbti`（用户类型）与 `mbti_score`。
- `rank` 增加 `mbti_filter`（可选）：传入 `none` 时不依赖 MBTI 参与打分（兼容后续可选场景）。

### 5. 新增 MBTI 路由 `backend/app/routers/mbti.py`（`prefix="/api/mbti"`）
- `GET /quiz` → 返回 28 题全文（供前端填空，无鉴权）。
- `POST /quiz` `{user_id, answers}` → 计算类型并写入用户，返回 `{mbti, dims:{E:I...}, complement_ready:true}`。
- `POST /direct` `{user_id, mbti}` → 已知类型直接设置（跳过答题）。
- `GET /{user_id}` → 查询当前用户画像（含 mbti、维度得分）。

注册到 `backend/app/main.py`。

## 前端改动

### 1. 新增问卷页 `frontend/pages/mbti.html`
- 顶部：标题 + 「我已知自己的 MBTI，直接填」按钮。
- 主体：28 题选择题（单页滚动，每题 A/B 单选），底部「提交并查看类型」。
- 提交后调用 `POST /api/mbti/quiz`，展示结果（类型 + 四维度得分条），并写入 `localStorage` 标记已答。
- 已知 MBTI 时输入 4 字母并 `POST /api/mbti/direct`。

### 2. 匹配页 `frontend/pages/match.html`
- 入口处读取 `localStorage['mbti']`：为空则展示「请先完成性格画像」引导卡片 + 跳转问卷按钮（实现「先答后匹配」）。
- 有 MBTI 后展示当前类型，并调用真实 `GET /api/match/{user_id}`（替换 Mock）。

### 3. 共享逻辑 `frontend/js/app.js`
- 新增 `MBTI` 交互：读取/写入 `localStorage`、`data-mbti` 渲染、维度条显示。
- 匹配结果渲染加入性格互补分数/标签。

### 4. 个人页 `frontend/pages/me.html`
- 展示当前用户 MBTI 类型与维度分布（画像区），入口指向 mbti.html 可重新测试。

> 说明：前端演示用户与后端内存用户（实为 `u01`）需保持一致；`app.js` 统一用 `localStorage['currentUserId']`（默认 `u01`）驱动所有 API 调用，便于切换。

## 需要复用/修改的现有文件

- 修改：`backend/app/matching.py`（@score_match 增 MBTI 加权）
- 修改：`backend/app/users.py`（加 mbti 字段 + set_user_mbti）
- 修改：`backend/app/routers/match.py`（detail 增 mbti）
- 修改：`backend/app/main.py`（注册 mbti router）
- 新增：`backend/app/mbti.py`、`backend/app/mbti_quiz.py`、`backend/app/routers/mbti.py`
- 新增：`frontend/pages/mbti.html`
- 修改：`frontend/pages/match.html`、`frontend/pages/me.html`、`frontend/js/app.js`

## 验证方式

1. 后端单测（不写 pytest，用临时脚本在 `backend/` 下 `python -m uvicorn` 前直接 import 验证）：
   - `compute_type` 用一组 sample answers 输出合法 4 字母类型，且与人工计分一致。
   - `complement_score("INTJ","ENTJ")` 应 > `complement_score("INTJ","INFP")`（验证互补模型方向）。
2. API（起 8001）：
   - `GET /api/mbti/quiz` 返回 28 题。
   - `POST /api/mbti/quiz` 带 answers → 返回类型。
   - `POST /api/mbti/direct` 带 `{mbti:"INTJ"}` → 写入成功。
   - `GET /api/match/u01?match_type=project` → 每个候选含 `mbti` 与 `mbti_score`，且互补型候选排名靠前。
3. 前端（起 8000）：打开 `match.html` 走「未答 → 引导问卷 → 答题 → 回匹配页出结果」全流程；控制台无报错、通过 `browser_evaluate` 校验 feed/result 渲染。