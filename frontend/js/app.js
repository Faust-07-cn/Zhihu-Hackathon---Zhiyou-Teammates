/* ============================================================
   校园社交平台 — 共享前端逻辑（骨架阶段）
   当前使用 MOCK 数据渲染，后续替换为后端 API 调用。
   ============================================================ */

"use strict";

/* ---------------- 全局配置 ---------------- */
const API_BASE = "http://localhost:8001";
const CURRENT_USER_ID = localStorage.getItem("currentUserId") || "u01";

function currentUser() {
  return localStorage.getItem("currentUserId") || "u01";
}

function getMbti() {
  return localStorage.getItem("userMbti") || null;
}
function setMbti(m) {
  localStorage.setItem("userMbti", m);
}
function api(path, options) {
  return fetch(API_BASE + path, options).then((r) => {
    if (!r.ok) throw new Error("API " + r.status);
    return r.json();
  });
}

/* ---------------- 工具：头像颜色 ---------------- */
const AVATAR_COLORS = ["#0084ff", "#e8b339", "#f1403c", "#6bc96b", "#9b6cea", "#12b7a3", "#e07b39"];

function hashColor(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) % 997;
  return AVATAR_COLORS[h % AVATAR_COLORS.length];
}

function firstName(name) {
  return name ? name.charAt(0).toUpperCase() : "?";
}

/* ---------------- MOCK 数据 ---------------- */
const MOCK = {
  user: {
    name: "浮士德",
    school: "某大学 · 计算机学院",
    role: "2025 级本科生",
    score: 84,
    level: "LV 4 活跃搭档",
    tags: ["计算机", "算法竞赛", "课程项目"],
  },
  hotList: [
    { text: "如何评价 2026 年全国大学生数学建模竞赛题型？", heat: 1284 },
    { text: "保研 vs 就业，大三下应该怎么选？", heat: 1106 },
    { text: "请求组队打 ACM 校赛，周末可约", heat: 987 },
    { text: "校园食堂有哪些隐藏美味？", heat: 854 },
    { text: "考研数学一 136 分经验分享", heat: 720 },
  ],
  partners: [
    { name: "阿晚", school: "计算机学院", score: 92, tags: ["算法", "组队"], online: true },
    { name: "南风", school: "信息学院", score: 88, tags: ["数学建模", "论文"], online: false },
    { name: "阿澈", school: "设计学院", score: 85, tags: ["UI", "答辩"], online: true },
    { name: "细雪", school: "外国语学院", score: 80, tags: ["写作", "翻译"], online: false },
  ],
  feeds: [
    {
      title: "求队伍一起冲击 2026 美赛 M 奖，已有两位队友",
      excerpt: "我们是一支新的队伍，想找一位擅长论文写作/建模的搭档补足团队拼图。周一三五晚有空，进度透明。",
      author: "阿晚",
      school: "计算机学院",
      tags: ["项目搭子", "数学建模", "组队"],
      likes: 132,
      comments: 46,
      time: "12 分钟前",
    },
    {
      title: "《操作系统》期末复习经验：别只看 PPT",
      excerpt: "把重点放在三阶段：概念梳理 → 模拟卷 → 错题复盘。这里分享一份我自己整理的思维导图。",
      author: "南风",
      school: "信息学院",
      tags: ["课程评价", "学习经验"],
      likes: 98,
      comments: 23,
      time: "1 小时前",
    },
    {
      title: "想找个志同道合的朋友一起做课程项目",
      excerpt: "方向是前后端分离的小型管理系统，希望能力互补、能长期坚持。感兴趣的同学评论区聊聊。",
      author: "阿澈",
      school: "设计学院",
      tags: ["学习搭子", "项目", "前后端"],
      likes: 76,
      comments: 31,
      time: "3 小时前",
    },
    {
      title: "校园网爬梯子买书攻略 & 二手书流转群",
      excerpt: "汇总了各书院二手书交易群号和靠谱平台，方便大家省钱又环保。持续更新，欢迎补充。",
      author: "细雪",
      school: "外国语学院",
      tags: ["生活资讯", "校园百科"],
      likes: 210,
      comments: 64,
      time: "5 小时前",
    },
  ],
};

/* ---------------- 组件渲染 ---------------- */
function renderFeed(list) {
  const wrap = document.querySelector("[data-feed]");
  if (!wrap) return;
  wrap.innerHTML = list
    .map(
      (f) => `
    <article class="feed-item">
      <div class="feed-meta">
        <span class="avatar" style="background:${hashColor(f.author)}">${firstName(f.author)}</span>
        <span>${f.author}</span><span>·</span><span>${f.school}</span>
        <span style="margin-left:auto">${f.time}</span>
      </div>
      <h3 class="feed-title">${f.title}</h3>
      <p class="feed-excerpt">${f.excerpt}</p>
      <div class="feed-tags">${f.tags.map((t) => `<span class="tag">${t}</span>`).join("")}</div>
      <div class="feed-footer">
        <button class="feed-action" data-action="like">👍 ${f.likes}</button>
        <button class="feed-action">💬 评论 ${f.comments}</button>
      </div>
    </article>`
    )
    .join("");
}

function renderHotList() {
  const wrap = document.querySelector("[data-hot]");
  if (!wrap) return;
  wrap.innerHTML = MOCK.hotList
    .map(
      (h, i) => `
    <li>
      <span class="rank-no ${i < 3 ? "top" : ""}">${i + 1}</span>
      <a class="rank-text" href="#">${h.text}</a>
    </li>`
    )
    .join("");
}

function renderPartners() {
  const wrap = document.querySelector("[data-partners]");
  if (!wrap) return;
  wrap.innerHTML = MOCK.partners
    .map(
      (p) => `
    <div class="partner-card">
      <div class="partner-head">
        <span class="avatar" style="background:${hashColor(p.name)}">${firstName(p.name)}</span>
        <span class="partner-name">${p.name}</span>
        <span class="match-score">匹配 ${p.score}%</span>
      </div>
      <div style="color:var(--color-text-secondary);font-size:13px">${p.school}${p.online ? " · 🟢 在线" : " · ⚪ 离线"}</div>
      <div class="partner-tags">${p.tags.map((t) => `<span class="tag">${t}</span>`).join("")}</div>
      <button class="btn btn-primary" style="height:28px;font-size:13px">发起搭子</button>
    </div>`
    )
    .join("");
}

/* 渲染后端匹配结果（GET /api/match/{id}） */
function renderMatchResults(results, selector = "[data-match-results]") {
  const wrap = document.querySelector(selector);
  if (!wrap) return;
  if (!results || !results.length) {
    wrap.innerHTML = `<div style="padding:20px;color:var(--color-text-secondary);text-align:center">暂无匹配结果</div>`;
    return;
  }
  wrap.innerHTML = results
    .map((r) => {
      const c = r.candidate || {};
      const d = r.detail || {};
      const purposeBadges = (d.matched_purposes || [])
        .map((p) => `<span class="purpose-badge">✓ 目的 · ${p}</span>`)
        .join("");
      const mbtiBadge = d.mbti
        ? `<span class="tag" style="background:rgba(241,64,60,.08);color:var(--color-accent)">MBTI ${d.mbti} · 互补 ${d.mbti_score}</span>`
        : "";
      return `
    <div class="partner-card">
      <div class="match-head">
        <span class="avatar" style="background:${hashColor(c.name || "?")}">${firstName(c.name || "?")}</span>
        <div style="flex:1;min-width:0">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="partner-name">${c.name || ""}</span>
            <span style="font-size:12px;color:var(--color-text-muted)">${c.level || ""}</span>
          </div>
          <div class="match-meta">${c.school || ""}${c.score ? ` · 搭子信 ${c.score}` : ""}</div>
        </div>
        <div style="text-align:right">
          <div class="match-score-lg">${r.score}%</div>
          <div class="match-score-label">匹配度</div>
        </div>
      </div>
      ${purposeBadges}
      <div class="partner-tags">
        ${(c.tags || []).map((t) => `<span class="tag">${t}</span>`).join("")}
        ${mbtiBadge}
      </div>
      <button class="btn btn-primary" style="height:28px;font-size:13px;width:100%;margin-top:10px">发起搭子</button>
    </div>`;
    })
    .join("");
}

function renderIdentity() {
  const wrap = document.querySelector("[data-identity]");
  if (!wrap) return;
  const u = MOCK.user;
  const myMbti = getMbti();
  wrap.innerHTML = `
    <div class="identity-avatar">${firstName(u.name)}</div>
    <div class="identity-name">${u.name}</div>
    <div class="identity-meta">${u.school}</div>
    <div class="identity-meta">${u.role}</div>
    <div class="identity-tags">${u.tags.map((t) => `<span class="tag">${t}</span>`).join("")}</div>
    ${myMbti ? `<div class="identity-row"><span class="tag tag-mbti">MBTI ${myMbti}</span></div>` : ""}
    <div class="identity-row">
      <span class="score-badge"><span class="score-num">${u.score}</span> 搭子信评分 · ${u.level}</span>
    </div>
  `;
}

/* 首页"搭子"频道：加载真实匹配结果（与搭子广场同源） */
function loadHomeMatchList() {
  const wrap = document.querySelector("[data-home-match-list]");
  if (!wrap) return;
  api(`/api/match/${currentUser()}?match_type=interest&top_n=5`)
    .then((data) => renderMatchResults(data.results, "[data-home-match-list]"))
    .catch((err) => {
      wrap.innerHTML = `<div style="padding:16px;color:var(--color-accent)">搭子加载失败：${err.message}</div>`;
    });
}

function bindLikes() {
  document.body.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action='like']");
    if (!btn) return;
    const m = btn.textContent.match(/(\d+)/);
    if (m) btn.textContent = `👍 ${Number(m[1]) + 1}`;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderFeed(MOCK.feeds);
  renderHotList();
  renderPartners();   // 先用 Mock 兜底
  renderIdentity();
  bindLikes();
  initMbtiPage();
  initRequestsPage();
  initQuestionnaireModals();
  loadHomePartners(); // 再异步用真实接口覆盖首页推荐
});

/* ---------------- MBTI 问卷页逻辑 ---------------- */
function initMbtiPage() {
  const quizWrap = document.querySelector("[data-quiz]");
  const resultWrap = document.querySelector("[data-quiz-result]");
  const directForm = document.querySelector("[data-direct-form]");
  if (!quizWrap && !directForm) return;

  // 已答过：直接显示结果（若页面有结果容器）
  if (getMbti() && resultWrap) {
    showQuizResult({ mbti: getMbti() });
  }

  // 加载题库
  if (quizWrap) {
    api("/api/mbti/quiz")
      .then((data) => {
        quizWrap.innerHTML = data.items
          .map(
            (q) => `
          <div class="quiz-item" data-q="${q.id}">
            <div class="quiz-q">${q.id}. ${q.text}</div>
            <div class="quiz-options">
              ${q.options
                .map(
                  (o) => `
                <label class="quiz-option" data-opt="${o.option}">
                  <span class="quiz-radio"></span>
                  <span>${o.option}. ${o.text}</span>
                </label>`
                )
                .join("")}
            </div>
          </div>`
          )
          .join("");
        // 选项选择
        quizWrap.addEventListener("click", (e) => {
          const label = e.target.closest(".quiz-option");
          if (!label) return;
          const item = label.closest(".quiz-item");
          item
            .querySelectorAll(".quiz-option")
            .forEach((o) => o.classList.remove("selected"));
          label.classList.add("selected");
        });
      })
      .catch((err) => {
        quizWrap.innerHTML = `<div style="padding:20px;color:var(--color-accent)">题库加载失败：${err.message}</div>`;
      });
  }

  // 提交问卷
  const submitBtn = document.querySelector("[data-submit-quiz]");
  if (submitBtn) {
    submitBtn.addEventListener("click", async () => {
      const items = document.querySelectorAll(".quiz-item");
      const answers = {};
      items.forEach((item) => {
        const sel = item.querySelector(".quiz-option.selected");
        if (sel) answers[Number(item.getAttribute("data-q"))] = sel.getAttribute("data-opt");
      });
      if (Object.keys(answers).length < 28) {
        alert(`还有 ${28 - Object.keys(answers).length} 题未作答`);
        return;
      }
      try {
        const res = await api("/api/mbti/quiz", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: currentUser(), answers }),
        });
        setMbti(res.mbti);
        showQuizResult(res);
        submitBtn.disabled = true;
        submitBtn.textContent = "已提交 ✓";
      } catch (err) {
        alert("提交失败：" + err.message);
      }
    });
  }

  // 已知 MBTI 直接填
  if (directForm) {
    directForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = directForm.querySelector("[data-direct-input]");
      const mbti = (input.value || "").trim().toUpperCase();
      if (!/^[EI]{1}[SN]{1}[TF]{1}[JP]{1}$/.test(mbti)) {
        alert("请输入合法 MBTI，如 INTJ、ENFP");
        return;
      }
      try {
        const res = await api("/api/mbti/direct", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: currentUser(), mbti }),
        });
        setMbti(res.mbti);
        if (resultWrap) showQuizResult(res);
        if (quizWrap) quizWrap.innerHTML = "";
        alert(`已保存你的 MBTI：${res.mbti}，可以开始匹配啦`);
      } catch (err) {
        alert("保存失败：" + err.message);
      }
    });
  }
}

function showQuizResult(res) {
  const resultWrap = document.querySelector("[data-quiz-result]");
  if (!resultWrap) return;
  const dims = res.dims || {};
  const dimMeta = [
    ["E/I", "精力来源"],
    ["S/N", "信息获取"],
    ["T/F", "决策方式"],
    ["J/P", "生活态度"],
  ];
  resultWrap.innerHTML = `
    <div class="mbti-result">
      <div style="color:var(--color-text-secondary)">你的性格类型</div>
      <div class="mbti-type">${res.mbti}</div>
      ${dimMeta
        .map(([key, label]) => {
          const v = dims[key] || "";
          const left = key.split("/")[0];
          const right = key.split("/")[1];
          const pos = v === left ? 10 : 90;
          return `
        <div class="dim-bar">
          <div class="dim-label"><span>${key}</span><span>${label}</span></div>
          <div class="dim-track">
            <div class="dim-fill" style="width:${pos}%"></div>
          </div>
          <div style="font-size:12px;color:var(--color-text-secondary);margin-top:4px">倾向 ${v}</div>
        </div>`;
        })
        .join("")}
      <div style="margin-top:6px;color:var(--color-text-secondary)">
        已同步到你的画像，匹配时会优先推荐性格互补的搭子
      </div>
    </div>
  `;
}

/* ---------------- 首页：真实推荐搭子 ---------------- */
function loadHomePartners() {
  const wrap = document.querySelector("[data-partners]");
  if (!wrap) return;
  api(`/api/match/${currentUser()}?match_type=interest&top_n=4`)
    .then((data) => renderMatchResults(data.results, "[data-partners]"))
    .catch(() => {
      /* 接口失败时保留 Mock 兜底渲染，不阻塞页面 */
    });
}

/* ---------------- 搭子广场页逻辑 ---------------- */
const REQ_TYPE_LABEL = { interest: "兴趣搭子", study: "学习搭子", project: "项目搭子" };

function renderRequestList(items) {
  const wrap = document.querySelector("[data-request-list]");
  if (!wrap) return;
  if (!items || !items.length) {
    wrap.innerHTML = `<div style="padding:24px;text-align:center;color:var(--color-text-secondary)">暂无请求，发布第一个吧</div>`;
    return;
  }
  wrap.innerHTML = items
    .map((it) => {
      const r = it.request || {};
      const owner = it.owner || {};
      const statusBadge =
        r.status === "matched"
          ? `<span class="req-status matched">已成组</span>`
          : `<span class="req-status open">开放中</span>`;

      let actionBtn = "";
      if (r.status === "matched") {
        const withName = it.matched_person ? `已与 ${it.matched_person.name} 成组` : "已成组";
        actionBtn = `<div style="color:var(--color-text-muted);font-size:13px">${withName}</div>`;
      } else if (it.is_owner) {
        actionBtn = `<button class="btn" style="height:28px;font-size:13px" data-action="intents" data-id="${r.id}">查看意向 (${r.intents.length})</button>`;
      } else if (it.has_intent) {
        actionBtn = `<button class="btn" style="height:28px;font-size:13px;border-color:var(--color-accent);color:var(--color-accent)" data-action="cancel-intent" data-id="${r.id}">已表达意向 · 取消</button>`;
      } else {
        actionBtn = `<button class="btn btn-primary" style="height:28px;font-size:13px" data-action="intent" data-id="${r.id}">我有意向</button>`;
      }

      const purposeBadges = (r.purposes || []).map((p) => `<span class="purpose-badge">${p}</span>`).join("");
      const mbtiBadge = it.detail && it.detail.mbti
        ? `<span class="tag" style="background:rgba(241,64,60,.08);color:var(--color-accent)">MBTI ${it.detail.mbti}</span>`
        : "";
      return `
    <div class="req-card">
      <div class="req-head">
        <span class="avatar" style="background:${hashColor(owner.name || "?")}">${firstName(owner.name || "?")}</span>
        <div style="flex:1;min-width:0">
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
            <span class="partner-name">${owner.name || ""}</span>
            <span style="font-size:12px;color:var(--color-text-muted)">${owner.school || ""}</span>
            ${statusBadge}
          </div>
          <div style="font-size:13px;color:var(--color-text-secondary)">${REQ_TYPE_LABEL[r.match_type] || r.match_type} · ${r.created_at}</div>
        </div>
        <div style="text-align:right">
          <div class="match-score-lg">${it.match_score}%</div>
          <div class="match-score-label">匹配度</div>
        </div>
      </div>
      <div style="font-size:15px;font-weight:600;margin:10px 0 4px">${r.title}${r.requires_questionnaire ? `<span class="req-badge">需问卷</span>` : ""}</div>
      <div style="font-size:13px;color:var(--color-text-secondary);line-height:1.6;margin-bottom:10px">${r.desc || ""}</div>
      <div class="partner-tags">
        ${purposeBadges}
        ${(r.tags || []).map((t) => `<span class="tag">${t}</span>`).join("")}
        ${mbtiBadge}
      </div>
      <div style="margin-top:12px">${actionBtn}</div>
    </div>`;
    })
    .join("");
}

function renderMyRequests(data) {
  const wrap = document.querySelector("[data-my-requests]");
  if (!wrap) return;

  const block = (title, list, renderer) => `
    <div style="font-size:15px;font-weight:600;margin:14px 0 8px">${title}（${list.length}）</div>
    ${
      list.length
        ? list.map(renderer).join("")
        : `<div style="color:var(--color-text-muted);font-size:13px;padding:8px 0">暂无</div>`
    }`;

  const publishedCard = (r) => `
    <div class="req-card">
      <div class="req-head">
        <span class="avatar" style="background:${hashColor(r.owner.name || "?")}">${firstName(r.owner.name || "?")}</span>
        <div style="flex:1;min-width:0">
          <div style="font-weight:600">${r.title}</div>
          <div style="font-size:12px;color:var(--color-text-muted)">
            ${r.status === "matched" ? `已成组 · 与 ${r.matched_person ? r.matched_person.name : ""}` : "开放中"}
          </div>
        </div>
        ${r.status === "matched" ? `<span class="req-status matched">已成组</span>` : `<span class="req-status open">开放中</span>`}
      </div>
      <div class="partner-tags">
        ${(r.purposes || []).map((p) => `<span class="purpose-badge">${p}</span>`).join("")}
        ${(r.tags || []).map((t) => `<span class="tag">${t}</span>`).join("")}
      </div>
      ${
        r.status === "open" && r.intent_people && r.intent_people.length
          ? `<div style="margin-top:10px;font-size:13px;color:var(--color-text-secondary)">意向：${r.intent_people.map((p) => p.name).join("、")}</div>`
          : ""
      }
    </div>`;

  const interestedCard = (r) => `
    <div class="req-card">
      <div class="req-head">
        <span class="avatar" style="background:${hashColor(r.owner.name || "?")}">${firstName(r.owner.name || "?")}</span>
        <div style="flex:1;min-width:0">
          <div style="font-weight:600">${r.title}</div>
          <div style="font-size:12px;color:var(--color-text-muted)">${r.owner.name || ""} 发布</div>
        </div>
        ${r.status === "matched" ? `<span class="req-status matched">已成组</span>` : `<span class="req-status open">意向中</span>`}
      </div>
      <div class="partner-tags">
        ${(r.purposes || []).map((p) => `<span class="purpose-badge">${p}</span>`).join("")}
        ${(r.tags || []).map((t) => `<span class="tag">${t}</span>`).join("")}
      </div>
    </div>`;

  wrap.innerHTML =
    block("我发布的请求", data.published, publishedCard) +
    block("我表达意向的", data.interested, interestedCard);
}

function initRequestsPage() {
  const listWrap = document.querySelector("[data-request-list]");
  const myWrap = document.querySelector("[data-my-requests]");
  if (!listWrap && !myWrap) return; // 非广场页

  const filter = { type: "", purpose: "" };
  let lastItems = []; // 最近一次广场列表，供意向流程判断是否需问卷

  const loadSquare = () => {
    const params = new URLSearchParams({ user_id: currentUser() });
    if (filter.type) params.set("match_type", filter.type);
    if (filter.purpose) params.set("purpose", filter.purpose);
    api(`/api/requests?${params.toString()}`)
      .then((data) => {
        lastItems = data.items;
        renderRequestList(data.items);
      })
      .catch((err) => {
        listWrap.innerHTML = `<div style="padding:20px;color:var(--color-accent)">加载失败：${err.message}</div>`;
      });
  };

  const loadMine = () => {
    myWrap.innerHTML = `<div class="match-loading"><div class="spin"></div><div>加载中…</div></div>`;
    api(`/api/requests/mine/${currentUser()}`)
      .then((data) => renderMyRequests(data))
      .catch((err) => {
        myWrap.innerHTML = `<div style="padding:20px;color:var(--color-accent)">加载失败：${err.message}</div>`;
      });
  };

  // 广场 / 我的请求 tab
  document.querySelectorAll("[data-req-tab]").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll("[data-req-tab]").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      const isMine = tab.getAttribute("data-req-tab") === "mine";
      listWrap.style.display = isMine ? "none" : "";
      myWrap.style.display = isMine ? "" : "none";
      if (isMine) loadMine();
    });
  });

  // 类型筛选
  document.querySelectorAll("[data-req-type]").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll("[data-req-type]").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      filter.type = tab.getAttribute("data-req-type");
      loadSquare();
    });
  });

  // 目的筛选（单选）
  document.querySelectorAll("[data-req-purpose]").forEach((tag) => {
    tag.addEventListener("click", () => {
      document.querySelectorAll("[data-req-purpose]").forEach((t) => t.classList.remove("selected"));
      tag.classList.add("selected");
      filter.purpose = tag.getAttribute("data-req-purpose");
      loadSquare();
    });
  });

  // 广场列表按钮：意向 / 取消意向 / 查看意向
  listWrap.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;
    const reqId = btn.getAttribute("data-id");
    const action = btn.getAttribute("data-action");
    const headers = { "Content-Type": "application/json" };
    if (action === "intent") {
      const item = lastItems.find((it) => (it.request || {}).id === reqId);
      if (item && item.request.requires_questionnaire) {
        openQnFillModal(reqId, item.request.questionnaire_id, () => loadSquare());
      } else {
        api(`/api/requests/${reqId}/intent`, {
          method: "POST", headers,
          body: JSON.stringify({ user_id: currentUser() }),
        }).then(loadSquare).catch((err) => alert("操作失败：" + err.message));
      }
    } else if (action === "cancel-intent") {
      api(`/api/requests/${reqId}/intent?user_id=${currentUser()}`, { method: "DELETE" })
        .then(loadSquare).catch((err) => alert("操作失败：" + err.message));
    } else if (action === "intents") {
      showIntents(reqId);
    }
  });

  // 发布模态框
  const publishModal = document.querySelector("[data-publish-modal]");
  if (publishModal) {
    const errEl = document.querySelector("[data-pub-error]");
    const needRadios = document.querySelectorAll('input[name="need_questionnaire"]');
    const qnEditorArea = document.getElementById("questionnaire_editor");
    const savedQnEl = document.querySelector("[data-saved-questionnaire]");
    const resetQn = () => {
      publishQn = null;
      if (savedQnEl) { savedQnEl.style.display = "none"; savedQnEl.textContent = ""; }
    };
    const closePublish = () => {
      publishModal.style.display = "none";
      document.querySelector("[data-pub-title]").value = "";
      document.querySelector("[data-pub-tags]").value = "";
      document.querySelector("[data-pub-desc]").value = "";
      document.querySelectorAll("[data-pub-purposes] [data-purpose]").forEach((t) => t.classList.remove("selected"));
      document.querySelectorAll("[data-pub-types] [data-type]").forEach((c, i) => c.classList.toggle("active", i === 2));
      needRadios.forEach((r) => (r.checked = r.value === "false"));
      if (qnEditorArea) qnEditorArea.style.display = "none";
      resetQn();
      errEl.style.display = "none";
    };
    document.querySelector("[data-open-publish]").addEventListener("click", () => {
      publishModal.style.display = "flex";
    });
    document.querySelector("[data-close-publish]").addEventListener("click", closePublish);
    publishModal.addEventListener("click", (e) => {
      if (e.target === publishModal) closePublish();
    });

    // 是否需要问卷：切换编辑器入口
    needRadios.forEach((radio) => {
      radio.addEventListener("change", () => {
        const need = radio.value === "true";
        if (qnEditorArea) qnEditorArea.style.display = need ? "block" : "none";
        if (!need) resetQn();
      });
    });

    // 打开问卷编辑器
    document.querySelector("[data-open-questionnaire-editor]").addEventListener("click", () => {
      openQnEditor();
    });

    document.querySelectorAll("[data-pub-types] [data-type]").forEach((card) => {
      card.addEventListener("click", () => {
        document.querySelectorAll("[data-pub-types] [data-type]").forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
      });
    });
    document.querySelectorAll("[data-pub-purposes] [data-purpose]").forEach((tag) => {
      tag.addEventListener("click", () => tag.classList.toggle("selected"));
    });

    document.querySelector("[data-submit-publish]").addEventListener("click", () => {
      const title = document.querySelector("[data-pub-title]").value.trim();
      if (!title) {
        errEl.textContent = "请填写标题";
        errEl.style.display = "";
        return;
      }
      const typeEl = document.querySelector("[data-pub-types] [data-type].active");
      const type = typeEl ? typeEl.getAttribute("data-type") : "interest";
      const purposes = Array.from(document.querySelectorAll("[data-pub-purposes] [data-purpose].selected"))
        .map((el) => el.getAttribute("data-purpose"));
      const tags = document.querySelector("[data-pub-tags]").value.split(/[,，]/).map((s) => s.trim()).filter(Boolean);
      const desc = document.querySelector("[data-pub-desc]").value.trim();
      const requires_questionnaire = document.querySelector('input[name="need_questionnaire"]:checked').value === "true";
      if (requires_questionnaire && !publishQn) {
        errEl.textContent = "请先设计并保存问卷";
        errEl.style.display = "";
        return;
      }
      const submitBtn = document.querySelector("[data-submit-publish]");
      submitBtn.disabled = true;
      api("/api/requests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUser(), title, match_type: type, purposes, tags, desc,
          requires_questionnaire,
          questionnaire_id: requires_questionnaire ? publishQn.id : null,
        }),
      })
        .then(() => { closePublish(); loadSquare(); })
        .catch((err) => {
          errEl.textContent = "发布失败：" + err.message;
          errEl.style.display = "";
        })
        .finally(() => { submitBtn.disabled = false; });
    });
  }

  // 意向列表模态框（发布者选人接受）
  const intentModal = document.querySelector("[data-intent-modal]");
  const showIntents = (reqId) => {
    api(`/api/requests/mine/${currentUser()}`).then(async (data) => {
      const req = data.published.find((r) => r.id === reqId);
      if (!req) {
        alert("请求不存在");
        return;
      }
      intentModal.setAttribute("data-req-id", reqId);
      document.querySelector("[data-intent-title]").textContent = `意向列表（${req.intent_people.length} 人）`;
      const list = document.querySelector("[data-intent-list]");

      // 需问卷的请求：拉取问卷，把答案下标映射为选项文本
      let qnMap = null; // qid -> {text, options}
      if (req.requires_questionnaire && req.questionnaire_id) {
        try {
          const qn = await api(`/api/requests/questionnaires/${req.questionnaire_id}`);
          qnMap = {};
          qn.questions.forEach((q) => { qnMap[String(q.id)] = { text: q.text, options: q.options }; });
        } catch (err) {
          alert("加载问卷失败：" + err.message);
          return;
        }
      }

      if (!req.intent_people.length) {
        list.innerHTML = `<div style="padding:16px;color:var(--color-text-secondary);text-align:center">还没有人表达意向</div>`;
      } else {
        list.innerHTML = req.intent_people
          .map((p) => {
            const answersHtml = (() => {
              if (!qnMap || !p.answers) return "";
              const lines = Object.entries(p.answers)
                .map(([qid, idx]) => {
                  const q = qnMap[qid];
                  return q ? `${q.text}：${q.options[idx] != null ? q.options[idx] : "（未答）"}` : "";
                })
                .filter(Boolean);
              if (!lines.length) return "";
              return `<div style="margin-top:6px;font-size:12px;color:var(--color-text-secondary);line-height:1.7">${lines.map((l) => `<div>· ${l}</div>`).join("")}</div>`;
            })();
            const scoreHtml = p.answer_score != null
              ? `<span class="req-badge">问卷匹配 ${p.answer_score}%</span>`
              : "";
            return `
            <div class="intent-item">
              <span class="avatar" style="background:${hashColor(p.name || "?")}">${firstName(p.name || "?")}</span>
              <div style="flex:1;min-width:0">
                <div style="font-weight:600">${p.name || ""} ${scoreHtml}</div>
                <div style="font-size:12px;color:var(--color-text-muted)">${p.school || ""}${p.score ? ` · 搭子信 ${p.score}` : ""}</div>
                ${answersHtml}
              </div>
              <button class="btn btn-primary" style="height:28px;font-size:13px" data-accept="${p.id}">接受</button>
            </div>`;
          })
          .join("");
      }
      intentModal.style.display = "flex";
    }).catch((err) => alert("加载意向失败：" + err.message));
  };
  if (intentModal) {
    document.querySelector("[data-close-intent]").addEventListener("click", () => {
      intentModal.style.display = "none";
    });
    intentModal.addEventListener("click", (e) => {
      if (e.target === intentModal) intentModal.style.display = "none";
    });
    document.querySelector("[data-intent-list]").addEventListener("click", (e) => {
      const btn = e.target.closest("[data-accept]");
      if (!btn) return;
      if (!confirm("确定接受 TA 成为你的搭子？")) return;
      const reqId = intentModal.getAttribute("data-req-id");
      api(`/api/requests/${reqId}/accept`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: currentUser(), accepted_user_id: btn.getAttribute("data-accept") }),
      })
        .then(() => {
          intentModal.style.display = "none";
          loadSquare();
        })
        .catch((err) => alert("接受失败：" + err.message));
    });
  }

  loadSquare();
}

/* ---------------- 自定义问卷：编辑器（发布者设计） ---------------- */
let publishQn = null;   // 发布流程中已保存的问卷 {id, title, questions}
let fillOnDone = null;  // 填写问卷完成后的回调（刷新广场）

function qnQuestionBlockHTML(qIndex) {
  return `
    <div class="qn-block" data-qn-block="${qIndex}">
      <div class="qn-block-head">
        <span class="qn-block-title">题目 ${qIndex + 1}</span>
        <button class="btn qn-remove" data-qn-remove-question>删除题目</button>
      </div>
      <input class="form-input" data-qn-q-text placeholder="请输入题干，如：你每周能投入多少时间？" />
      <div class="qn-options" data-qn-options>
        <div class="qn-option-row">
          <label class="qn-expected"><input type="checkbox" data-qn-expected /> 期望</label>
          <input class="form-input" data-qn-opt placeholder="选项内容" />
          <button class="btn qn-remove" data-qn-remove-option>×</button>
        </div>
        <div class="qn-option-row">
          <label class="qn-expected"><input type="checkbox" data-qn-expected /> 期望</label>
          <input class="form-input" data-qn-opt placeholder="选项内容" />
          <button class="btn qn-remove" data-qn-remove-option>×</button>
        </div>
      </div>
      <button class="btn btn-ghost" data-qn-add-option>+ 添加选项</button>
    </div>`;
}

function openQnEditor() {
  const modal = document.querySelector("[data-qn-editor-modal]");
  if (!modal) return;
  document.querySelector("[data-qn-error]").style.display = "none";
  document.querySelector("[data-qn-title]").value = publishQn ? publishQn.title : "";
  const wrap = document.querySelector("[data-qn-questions]");
  if (publishQn && publishQn.questions && publishQn.questions.length) {
    // 回填已保存问卷，便于修改
    wrap.innerHTML = publishQn.questions.map((q) => {
      const opts = q.options.map((o, oi) => `
        <div class="qn-option-row">
          <label class="qn-expected"><input type="checkbox" data-qn-expected ${(q.expected || []).includes(oi) ? "checked" : ""} /> 期望</label>
          <input class="form-input" data-qn-opt value="${o}" />
          <button class="btn qn-remove" data-qn-remove-option>×</button>
        </div>`).join("");
      return `
        <div class="qn-block" data-qn-block>
          <div class="qn-block-head">
            <span class="qn-block-title">题目</span>
            <button class="btn qn-remove" data-qn-remove-question>删除题目</button>
          </div>
          <input class="form-input" data-qn-q-text value="${q.text}" />
          <div class="qn-options" data-qn-options>${opts}</div>
          <button class="btn btn-ghost" data-qn-add-option>+ 添加选项</button>
        </div>`;
    }).join("");
  } else {
    wrap.innerHTML = qnQuestionBlockHTML(0);
  }
  modal.style.display = "flex";
}

function buildQnFromEditor() {
  const title = document.querySelector("[data-qn-title]").value.trim();
  if (!title) return { ok: false, msg: "请填写问卷标题" };
  const blocks = Array.from(document.querySelectorAll("[data-qn-block]"));
  if (!blocks.length) return { ok: false, msg: "至少需要 1 道题" };

  const questions = blocks.map((b, i) => {
    const text = b.querySelector("[data-qn-q-text]").value.trim();
    const rawOptions = Array.from(b.querySelectorAll("[data-qn-opt]")).map((o) => o.value.trim());
    const expectedSet = new Set(
      Array.from(b.querySelectorAll("[data-qn-expected]"))
        .map((cb, idx) => (cb.checked ? idx : null))
        .filter((v) => v != null)
    );
    // 过滤空选项后重建下标，避免与后端校验错位
    const options = [];
    const expected = [];
    rawOptions.forEach((opt, idx) => {
      if (!opt) return;
      const newIdx = options.length;
      options.push(opt);
      if (expectedSet.has(idx)) expected.push(newIdx);
    });
    return { id: String(i + 1), text, options, expected };
  });

  if (questions.some((q) => !q.text)) return { ok: false, msg: "题干不能为空" };
  const bad = questions.find((q) => q.options.length < 2);
  if (bad) return { ok: false, msg: `题目「${bad.text}」至少需要 2 个选项` };
  return { ok: true, title, questions };
}

function initQuestionnaireModals() {
  const editorModal = document.querySelector("[data-qn-editor-modal]");
  const fillModal = document.querySelector("[data-qn-fill-modal]");
  const fillBody = document.querySelector("[data-qn-fill-body]");

  if (editorModal) {
    const errEl = document.querySelector("[data-qn-error]");
    const close = () => editorModal.style.display = "none";

    document.querySelector("[data-qn-add-question]").addEventListener("click", () => {
      const wrap = document.querySelector("[data-qn-questions]");
      wrap.insertAdjacentHTML("beforeend", qnQuestionBlockHTML(wrap.children.length));
    });
    document.querySelector("[data-qn-questions]").addEventListener("click", (e) => {
      const block = e.target.closest("[data-qn-block]");
      if (!block) return;
      if (e.target.closest("[data-qn-add-option]")) {
        block.querySelector("[data-qn-options]").insertAdjacentHTML("beforeend", `
          <div class="qn-option-row">
            <label class="qn-expected"><input type="checkbox" data-qn-expected /> 期望</label>
            <input class="form-input" data-qn-opt placeholder="选项内容" />
            <button class="btn qn-remove" data-qn-remove-option>×</button>
          </div>`);
      } else if (e.target.closest("[data-qn-remove-option]")) {
        const row = e.target.closest(".qn-option-row");
        const rows = block.querySelectorAll(".qn-option-row");
        if (rows.length <= 2) { alert("每道题至少保留 2 个选项"); return; }
        row.remove();
      } else if (e.target.closest("[data-qn-remove-question]")) {
        if (document.querySelectorAll("[data-qn-block]").length <= 1) { alert("至少保留 1 道题"); return; }
        block.remove();
      }
    });

    document.querySelector("[data-qn-save]").addEventListener("click", async () => {
      const data = buildQnFromEditor();
      if (!data.ok) {
        errEl.textContent = data.msg;
        errEl.style.display = "";
        return;
      }
      document.querySelector("[data-qn-save]").disabled = true;
      try {
        const res = await api("/api/requests/questionnaires", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: data.title, questions: data.questions }),
        });
        publishQn = { id: res.questionnaire.id, title: res.questionnaire.title, questions: data.questions };
        const savedEl = document.querySelector("[data-saved-questionnaire]");
        savedEl.textContent = `已保存问卷：${res.questionnaire.title}（${data.questions.length} 题）`;
        savedEl.style.display = "";
        close();
      } catch (err) {
        errEl.textContent = "保存失败：" + err.message;
        errEl.style.display = "";
      } finally {
        document.querySelector("[data-qn-save]").disabled = false;
      }
    });
    document.querySelector("[data-qn-cancel]").addEventListener("click", close);
    editorModal.addEventListener("click", (e) => { if (e.target === editorModal) close(); });
  }

  if (fillModal) {
    const close = () => fillModal.style.display = "none";
    // 单选交互（复用 .quiz-option 样式）
    fillBody.addEventListener("click", (e) => {
      const label = e.target.closest(".quiz-option");
      if (!label) return;
      const item = label.closest(".quiz-item");
      item.querySelectorAll(".quiz-option").forEach((o) => o.classList.remove("selected"));
      label.classList.add("selected");
    });
    document.querySelector("[data-qn-fill-cancel]").addEventListener("click", close);
    fillModal.addEventListener("click", (e) => { if (e.target === fillModal) close(); });

    document.querySelector("[data-qn-fill-submit]").addEventListener("click", () => {
      const reqId = fillModal.getAttribute("data-fill-req-id");
      const items = fillBody.querySelectorAll(".quiz-item");
      const answers = {};
      items.forEach((item) => {
        const sel = item.querySelector(".quiz-option.selected");
        if (sel) answers[item.getAttribute("data-q")] = Number(sel.getAttribute("data-opt"));
      });
      if (Object.keys(answers).length < items.length) {
        alert(`还有 ${items.length - Object.keys(answers).length} 题未作答`);
        return;
      }
      api(`/api/requests/${reqId}/intent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: currentUser(), answers }),
      })
        .then((res) => {
          close();
          alert(res.answer_score != null ? `已表达意向，问卷匹配度 ${res.answer_score}%` : "已表达意向");
          if (fillOnDone) fillOnDone();
        })
        .catch((err) => alert("操作失败：" + err.message));
    });
  }
}

function openQnFillModal(reqId, qid, onDone) {
  const modal = document.querySelector("[data-qn-fill-modal]");
  if (!modal) return;
  if (!qid) { alert("该请求未关联问卷"); return; }
  modal.setAttribute("data-fill-req-id", reqId);
  fillOnDone = onDone;
  const body = document.querySelector("[data-qn-fill-body]");
  body.innerHTML = `<div class="match-loading"><div class="spin"></div><div>加载中…</div></div>`;
  modal.style.display = "flex";
  api(`/api/requests/questionnaires/${qid}`)
    .then((qn) => {
      document.querySelector("[data-qn-fill-title]").textContent = `问卷 · ${qn.title || "搭子筛选"}`;
      body.innerHTML = qn.questions.map((q) => `
        <div class="quiz-item" data-q="${q.id}">
          <div class="quiz-q">${q.text}</div>
          <div class="quiz-options">
            ${q.options.map((opt, i) => `
              <label class="quiz-option" data-opt="${i}">
                <span class="quiz-radio"></span><span>${opt}</span>
              </label>`).join("")}
          </div>
        </div>`).join("");
    })
    .catch((err) => {
      body.innerHTML = `<div style="padding:16px;color:var(--color-accent)">问卷加载失败：${err.message}</div>`;
    });
}