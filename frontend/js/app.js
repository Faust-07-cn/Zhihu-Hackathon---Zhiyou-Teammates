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

/* ---------------- 演示账号 ---------------- */
// 首页与子页面目录层级不同，跳搭子广场需按当前路径拼相对地址
const SQUARE_URL = window.location.pathname.includes("/pages/") ? "requests.html" : "pages/requests.html";

let _usersPromise = null;
// 演示用户池只拉一次，供账号切换、身份卡复用
function loadUsers() {
  if (!_usersPromise) {
    _usersPromise = api("/api/users").then((d) => d.items || []).catch(() => []);
  }
  return _usersPromise;
}

function initAccountSwitcher() {
  const nav = document.querySelector(".nav-links");
  if (!nav || nav.querySelector("[data-account-switch]")) return;
  const wrap = document.createElement("label");
  wrap.className = "account-switch";
  wrap.innerHTML = `<span class="account-switch-label">演示账号</span>
    <select data-account-switch title="切换演示账号，用于演示双用户成组流程"></select>`;
  nav.appendChild(wrap);
  const sel = wrap.querySelector("select");
  loadUsers().then((list) => {
    if (!list.length) {
      wrap.remove();
      return;
    }
    sel.innerHTML = list
      .map((u) => `<option value="${u.id}">${u.name} · ${u.school}</option>`)
      .join("");
    sel.value = currentUser();
  });
  sel.addEventListener("change", () => {
    localStorage.setItem("currentUserId", sel.value);
    localStorage.removeItem("userMbti"); // 画像随账号切换，避免不同演示账号串味
    window.location.reload();
  });
}

/* ---------------- 页面切换过渡 ----------------
   点击站内导航时先淡出（page-leaving）再跳转，新页面加载时自动淡入。
   （style.css 中 body 自带 page-in 动画） */
document.addEventListener("click", (e) => {
  const link = e.target.closest('a[href]');
  if (!link) return;
  const href = link.getAttribute("href");
  // 仅拦截站内页面跳转
  if (!href || href.startsWith("#") || href.startsWith("javascript:") || href.includes("://")) return;
  const cur = window.location.pathname.replace(/^\//, "");
  if (href === cur) return; // 点击的是当前页，不拦截
  e.preventDefault();
  document.body.classList.add("page-leaving");
  setTimeout(() => {
    window.location.href = link.href;
  }, 220);
});

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
  feeds: [
    {
      title: "求队伍一起冲击 2026 美赛 M 奖，已有两位队友",
      excerpt: "我们是一支新的队伍，想找一位擅长论文写作/建模的搭档补足团队拼图。周一三五晚有空，进度透明。",
      author: "阿晚",
      school: "计算机学院",
      tags: ["项目搭子", "数学建模", "组队"],
      channel: "竞赛",
      request: { match_type: "project", purposes: ["竞赛组队"] },
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
      channel: "课程",
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
      channel: "搭子",
      request: { match_type: "project", purposes: ["结伴学习"] },
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
      channel: "生活",
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

/* ---------------- 讨论区：频道切换 + 帖子转搭子 + 发帖 + 知乎搜索 ---------------- */
let forumPosts = [];          // 后端拉取的帖子（新帖在前）
let forumChannel = "all";     // 当前频道（all 表示全部）
let postRefs = [];            // 发帖时选中的知乎引用

// 从后端拉取帖子列表（GET /api/posts）
function loadPosts() {
  return api("/api/posts").then((d) => d.items || []).catch(() => []);
}

// 知乎站内搜索（GET /api/zhihu/search）；后端缺凭据时返回对齐字段的演示 Mock
function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[ch]));
}

function safeZhihuURL(value) {
  try {
    const url = new URL(value);
    if (url.protocol === "https:" && !url.username && !url.password &&
        (url.hostname === "zhihu.com" || url.hostname.endsWith(".zhihu.com"))) return url.href;
  } catch (_) { /* 不可信链接只展示文本 */ }
  return "";
}

const zhihuSearchPending = new Map();
function zhihuSearch(query, count = 6) {
  const key = `${count}:${query}`;
  if (!zhihuSearchPending.has(key)) {
    const request = api(`/api/zhihu/search?query=${encodeURIComponent(query)}&count=${count}`)
      .then((res) => {
        if (!Array.isArray(res.items) || !["mock", "zhihu"].includes(res.source)) throw new Error("搜索响应无效");
        return res;
      })
      .finally(() => zhihuSearchPending.delete(key));
    zhihuSearchPending.set(key, request);
  }
  return zhihuSearchPending.get(key);
}

function zhihuSourceLabel(res) {
  if (res.source === "zhihu") return "知乎";
  const reasons = {
    missing_credentials: "未配置凭据", auth_failed: "鉴权失败",
    quota_exceeded: "额度或频率受限", network_error: "上游网络错误", upstream_error: "上游服务异常",
  };
  return `演示数据（mock，非真实知乎内容${reasons[res.fallback_reason] ? "；" + reasons[res.fallback_reason] : ""}）`;
}

// 两个入口复用请求状态；输入变化或关闭时让旧响应失效，不自动重试。
function bindZhihuSearch(input, btn, body, onState = () => {}) {
  let version = 0;
  let pendingQuery = null;
  const invalidate = () => {
    version++;
    pendingQuery = null;
    btn.disabled = false;
    body.innerHTML = "";
  };
  input.addEventListener("input", invalidate);
  const run = async () => {
    const q = input.value.trim();
    if (!q || pendingQuery === q) return;
    const id = ++version;
    pendingQuery = q;
    btn.disabled = true;
    onState(q, "搜索中…");
    body.textContent = "搜索中…";
    try {
      const res = await zhihuSearch(q);
      if (id !== version) return;
      onState(q, zhihuSourceLabel(res));
      body.innerHTML = `<div>${escapeHTML(zhihuSourceLabel(res))}</div>` +
        (res.items.length ? res.items.map((it) => zhihuItemHTML(it, { selectable: true, source: res.source })).join("")
          : "<div>未找到相关内容</div>");
    } catch (_) {
      if (id !== version) return;
      onState(q, "搜索失败");
      body.textContent = "搜索失败，请检查网络或后端服务后重试。";
    } finally {
      if (id === version) { pendingQuery = null; btn.disabled = false; }
    }
  };
  btn.addEventListener("click", run);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.isComposing) { e.preventDefault(); run(); }
  });
  return invalidate;
}

// 单条知乎搜索结果；selectable 为 true 时显示「引用」按钮
function zhihuItemHTML(item, opts = {}) {
  const source = opts.source === "zhihu" ? "zhihu" : "mock";
  const url = source === "zhihu" ? safeZhihuURL(item.Url) : "";
  const title = escapeHTML(item.Title);
  const btn = opts.selectable
    ? `<button class="btn btn-ghost zhihu-ref-btn" type="button"
         data-ref-title="${title}" data-ref-url="${escapeHTML(url)}" data-ref-source="${source}"
         data-ref-author="${escapeHTML(item.AuthorName)}" data-ref-type="${escapeHTML(item.ContentType)}">引用</button>`
    : "";
  return `
    <div class="zhihu-item">
      ${url ? `<a class="zhihu-item-title" href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">${title}</a>` : `<span class="zhihu-item-title">${title}</span>`}
      <p class="zhihu-item-text">${escapeHTML(item.ContentText)}</p>
      <div class="zhihu-item-meta">
        <span>${escapeHTML(item.AuthorName)}</span><span>·</span><span>${escapeHTML(item.VoteUpCount || 0)} 赞同</span>
        ${source === "mock" ? "<span>演示数据（mock）</span>" : ""}
        ${btn}
      </div>
    </div>`;
}

function zhihuRefHTML(ref) {
  const mock = ref.source !== "zhihu";
  const title = escapeHTML(ref.title) + (mock ? "（演示数据 mock，非真实知乎内容）" : "");
  const url = mock ? "" : safeZhihuURL(ref.url);
  return url ? `<a class="zhihu-ref-link" href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">${title}</a>`
    : `<span class="zhihu-ref-link">${title}</span>`;
}

function forumFeedHTML(f, idx) {
  const applyBtn = `<button class="feed-action" data-action="to-request" data-idx="${idx}">转为我的搭子需求</button>`;
  const refs = (f.zhihu_refs && f.zhihu_refs.length)
    ? `<div class="zhihu-shared" style="margin-top:10px">
        <div class="zhihu-shared-head">知乎引用</div>
        ${f.zhihu_refs.map(zhihuRefHTML).join("")}
      </div>`
    : "";
  return `
    <article class="feed-item">
      <div class="feed-meta">
        <span class="avatar" style="background:${hashColor(f.author)}">${escapeHTML(firstName(f.author))}</span>
        <span>${escapeHTML(f.author)}</span><span>·</span><span>${escapeHTML(f.school)}</span>
        <span style="margin-left:auto">${escapeHTML(f.time)}</span>
      </div>
      <h3 class="feed-title">${escapeHTML(f.title)}</h3>
      <p class="feed-excerpt">${escapeHTML(f.excerpt)}</p>
      ${refs}
      <div class="feed-tags">${(f.tags || []).map((t) => `<span class="tag">${escapeHTML(t)}</span>`).join("")}</div>
      <div class="feed-footer">
        <button class="feed-action" data-action="like" data-post-id="${escapeHTML(f.id)}">赞 ${escapeHTML(f.likes)}</button>
        <button class="feed-action" data-action="post-detail" data-post-id="${escapeHTML(f.id)}">详情 / 评论 ${escapeHTML(f.comments)}</button>
        ${applyBtn}
      </div>
    </article>`;
}

// 渲染当前频道可见帖子；把可见列表暴露给「转搭子」按钮取数据
function renderForumFeed() {
  const wrap = document.querySelector("[data-feed]");
  if (!wrap) return;
  const list = forumChannel === "all"
    ? forumPosts
    : forumPosts.filter((f) => f.channel === forumChannel);
  window.__forumVisible = list;
  wrap.innerHTML = list.map((f, idx) => forumFeedHTML(f, idx)).join("");
}

// 渲染发帖时已选中的知乎引用
function renderZhihuRefs() {
  const sel = document.querySelector("[data-zhihu-ref-selected]");
  if (!sel) return;
  if (!postRefs.length) {
    sel.innerHTML = "";
    return;
  }
  sel.innerHTML = `
    <div class="zhihu-shared">
      <div class="zhihu-shared-head">已选引用</div>
      ${postRefs.map((r, i) => `
        <div class="zhihu-ref-picked">
          <span>${zhihuRefHTML(r)}</span>
          <button class="btn" type="button" data-remove-ref="${i}" style="margin-left:auto;padding:2px 8px">移除</button>
        </div>`).join("")}
    </div>`;
}

function addPostRef(ref) {
  if (postRefs.some((r) => r.source === ref.source &&
      (ref.url ? r.url === ref.url : r.title === ref.title && r.author_name === ref.author_name))) return;
  postRefs.push(ref);
  renderZhihuRefs();
}

function openPostModal() {
  const modal = document.querySelector("[data-post-modal]");
  if (!modal) return;
  renderZhihuRefs();
  modal.style.display = "flex";
}

function initForumPage() {
  const wrap = document.querySelector("[data-feed]");
  const tabs = Array.from(document.querySelectorAll("[data-channel]"));
  if (!wrap || !tabs.length) return; // 非讨论区页

  // 频道切换（只绑定顶部 data-channel 标签，发帖模态框用 data-post-channel-val 隔离）
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      forumChannel = tab.getAttribute("data-channel");
      renderForumFeed();
    });
  });

  // 帖子列表点击：转搭子 / 引用
  wrap.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action='to-request']");
    if (!btn || btn.disabled) return;
    const f = (window.__forumVisible || [])[Number(btn.getAttribute("data-idx"))];
    if (!f) return;
    createRequestFromPost(f, btn);
  });

  initPostModal();

  // 拉取后端帖子并渲染
  wrap.innerHTML = `<div style="padding:20px;color:var(--color-text-secondary);text-align:center">加载中…</div>`;
  loadPosts().then((items) => {
    const existing = new Set(forumPosts.map((post) => post.id));
    forumPosts = [...forumPosts, ...items.filter((post) => !existing.has(post.id))];
    renderForumFeed();
  });
}

// 全站顶部搜索统一进入讨论区；讨论区复用知乎搜索与引用结果。
function initForumSearch() {
  const input = document.querySelector(".nav .search input");
  const btn = document.querySelector(".nav .search button");
  if (!input || !btn) return;
  input.placeholder = "搜索知乎回答、文章…";
  const box = document.querySelector("[data-zhihu-results]");
  if (!box) {
    const navigate = () => {
      const q = input.value.trim();
      if (!q) return;
      const forumURL = window.location.pathname.includes("/pages/") ? "forum.html" : "pages/forum.html";
      window.location.href = `${forumURL}?q=${encodeURIComponent(q)}`;
    };
    btn.addEventListener("click", navigate);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.isComposing) { e.preventDefault(); navigate(); }
    });
    return;
  }

  const body = box.querySelector("[data-zhihu-results-body]");
  const title = box.querySelector("[data-zhihu-results-title]");
  bindZhihuSearch(input, btn, body, (q, state) => {
    box.style.display = "";
    title.textContent = `知乎搜索 · ${q}（${state}）`;
  });
  const query = new URLSearchParams(window.location.search).get("q");
  if (query && query.trim()) {
    input.value = query.trim();
    btn.click();
  }

  // 顶部搜索结果中的「引用」→ 加入发帖引用池并打开发帖框
  box.addEventListener("click", (e) => {
    const b = e.target.closest("[data-ref-title]");
    if (!b) return;
    addPostRef({
      title: b.getAttribute("data-ref-title"),
      url: b.getAttribute("data-ref-url"),
      author_name: b.getAttribute("data-ref-author"),
      content_type: b.getAttribute("data-ref-type"),
      source: b.getAttribute("data-ref-source"),
    });
    openPostModal();
  });
}

// 发帖模态框：写帖 + 搜索知乎并引用 + 发布到 /api/posts
function initPostModal() {
  const modal = document.querySelector("[data-post-modal]");
  if (!modal) return;
  const openBtn = document.querySelector("[data-open-post]");

  let postChannel = "搭子";
  const channelOpts = Array.from(modal.querySelectorAll("[data-post-channel-val]"));
  const setChannel = (ch) => {
    postChannel = ch;
    channelOpts.forEach((o) =>
      o.classList.toggle("active", o.getAttribute("data-post-channel-val") === ch));
  };
  channelOpts.forEach((o) =>
    o.addEventListener("click", () => setChannel(o.getAttribute("data-post-channel-val"))));

  if (openBtn) openBtn.addEventListener("click", () => {
    const draft = document.querySelector("[data-post-draft]");
    const content = modal.querySelector("[data-post-content]");
    if (draft && draft.value.trim()) {
      content.value = content.value ? `${content.value}\n${draft.value}` : draft.value;
      draft.value = "";
    }
    if (forumChannel !== "all") setChannel(forumChannel);
    openPostModal();
  });

  // 发帖内「搜索知乎并引用」
  const refQuery = modal.querySelector("[data-zhihu-ref-query]");
  const refSearch = modal.querySelector("[data-zhihu-ref-search]");
  const refResults = modal.querySelector("[data-zhihu-ref-results]");
  const resetRefSearch = bindZhihuSearch(refQuery, refSearch, refResults);
  modal.querySelectorAll("[data-close-post]").forEach((b) =>
    b.addEventListener("click", () => {
      modal.style.display = "none";
      resetRefSearch();
    }));
  refResults.addEventListener("click", (e) => {
    const b = e.target.closest("[data-ref-title]");
    if (!b) return;
    addPostRef({
      title: b.getAttribute("data-ref-title"),
      url: b.getAttribute("data-ref-url"),
      author_name: b.getAttribute("data-ref-author"),
      content_type: b.getAttribute("data-ref-type"),
      source: b.getAttribute("data-ref-source"),
    });
  });

  // 移除已选引用
  const selBox = modal.querySelector("[data-zhihu-ref-selected]");
  selBox.addEventListener("click", (e) => {
    const b = e.target.closest("[data-remove-ref]");
    if (!b) return;
    postRefs.splice(Number(b.getAttribute("data-remove-ref")), 1);
    renderZhihuRefs();
  });

  // 发布
  modal.querySelector("[data-submit-post]").addEventListener("click", () => {
    const errBox = modal.querySelector("[data-post-error]");
    const title = modal.querySelector("[data-post-title]").value.trim();
    const content = modal.querySelector("[data-post-content]").value.trim();
    const tags = modal.querySelector("[data-post-tags]").value.split(/[,，]/)
      .map((s) => s.trim()).filter(Boolean);
    if (!title) { errBox.textContent = "标题不能为空"; errBox.style.display = ""; return; }
    if (!content) { errBox.textContent = "正文不能为空"; errBox.style.display = ""; return; }
    errBox.style.display = "none";

    const submitBtn = modal.querySelector("[data-submit-post]");
    submitBtn.disabled = true;
    api("/api/posts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: currentUser(),
        title,
        content,
        channel: postChannel,
        tags,
        zhihu_refs: postRefs,
      }),
    })
      .then((post) => {
        modal.style.display = "none";
        resetRefSearch();
        submitBtn.disabled = false;
        modal.querySelector("[data-post-title]").value = "";
        modal.querySelector("[data-post-content]").value = "";
        modal.querySelector("[data-post-tags]").value = "";
        refQuery.value = "";
        refResults.innerHTML = "";
        postRefs = [];
        renderZhihuRefs();
        forumPosts = [post, ...forumPosts.filter((item) => item.id !== post.id)];
        forumChannel = post.channel;
        document.querySelectorAll("[data-channel]").forEach((tab) =>
          tab.classList.toggle("active", tab.getAttribute("data-channel") === forumChannel));
        renderForumFeed();
      })
      .catch((err) => {
        submitBtn.disabled = false;
        errBox.textContent = "发布失败：" + err.message;
        errBox.style.display = "";
      });
  });
}

// 帖子 → 搭子请求：带上帖子主题与需求信息，复用后端发布接口
function createRequestFromPost(f, btn) {
  const conv = f.request || { match_type: "interest", purposes: ["兴趣交流"] };
  if (!confirm("将根据该帖子在搭子广场发起一个搭子需求，确定继续？")) return;
  btn.disabled = true;
  api("/api/requests", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: currentUser(),
      title: f.title,
      match_type: conv.match_type,
      purposes: conv.purposes,
      tags: f.tags,
      desc: f.excerpt,
      requires_questionnaire: false,
      questionnaire_id: null,
    }),
  })
    .then(() => {
      window.location.href = SQUARE_URL;
    })
    .catch((err) => {
      btn.disabled = false;
      alert("发起失败：" + err.message);
    });
}

/* 渲染后端匹配结果（GET /api/match/{id}）
   opts.compact：紧凑模式（首页只展示前 2 条理由、不展开分数拆解） */
function renderMatchResults(results, selector = "[data-match-results]", opts = {}) {
  const wrap = document.querySelector(selector);
  if (!wrap) return;
  if (!results || !results.length) {
    wrap.innerHTML = `<div style="padding:20px;color:var(--color-text-secondary);text-align:center">暂无匹配结果</div>`;
    return;
  }
  wrap.innerHTML = results.map((r) => matchCardHTML(r, opts)).join("");
}

// 单张推荐卡：匹配分拆解 + 推荐理由 + 共同知乎内容 + 发起搭子
function matchCardHTML(r, opts = {}) {
  const c = r.candidate || {};
  const d = r.detail || {};
  const connect = r.connect || {};
  const compact = !!opts.compact;

  const purposeBadges = (d.matched_purposes || [])
    .map((p) => `<span class="purpose-badge">✓ 目的 · ${p}</span>`)
    .join("");

  // 推荐理由来自后端 detail.reasons，前端不写死
  const reasons = (d.reasons || []).slice(0, compact ? 2 : 4);
  const reasonsHTML = reasons.length
    ? `<ul class="reason-list">${reasons.map((t) => `<li class="reason-line">${t}</li>`).join("")}</ul>`
    : "";

  // 共同知乎内容：话题 + 创作/收藏
  const zhihuItems = [
    ...(d.shared_zhihu_topics || []).map((t) => `<span class="tag tag-zhihu">话题 · ${t}</span>`),
    ...(d.shared_zhihu_contents || []).map(
      (it) => `<span class="tag tag-zhihu" title="${it.excerpt || ""}">知乎${it.kind || ""} · ${it.title}</span>`
    ),
  ];
  const zhihuHTML = zhihuItems.length
    ? `<div class="zhihu-shared">
        <div class="zhihu-shared-head">共同知乎内容${
          d.zhihu_source === "mock" ? `<span class="mock-badge">演示数据</span>` : ""
        }</div>
        <div class="partner-tags">${zhihuItems.join("")}</div>
      </div>`
    : "";

  // 匹配分拆解：让用户看懂分数从哪里来（首页紧凑模式也保留，是「可解释」的核心展示）
  const breakdown = d.breakdown || [];
  const breakdownHTML =
    breakdown.length
      ? `<div class="breakdown">${breakdown
          .map((b) => `<span class="breakdown-item">${b.label} <b>${b.score}</b><i>×${b.weight}%</i></span>`)
          .join("")}</div>`
      : "";

  const mbtiBadge = d.mbti ? `<span class="tag tag-mbti">MBTI ${d.mbti}</span>` : "";

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
      ${reasonsHTML}
      ${zhihuHTML}
      ${breakdownHTML}
      ${connectButtonHTML(c, connect)}
    </div>`;
}

// 「发起搭子」按钮：真实调用后端表达意向接口，并区分已发送 / 需问卷 / 无请求三种状态
function connectButtonHTML(candidate, connect) {
  const base = `class="btn btn-block" style="margin-top:10px"`;
  if (connect.has_intent) {
    return `<button ${base} disabled>已表达意向 ✓ 等待对方接受</button>`;
  }
  if (connect.request_id && !connect.requires_questionnaire) {
    return `<button class="btn btn-primary btn-block" style="margin-top:10px" data-action="connect" data-uid="${candidate.id}">发起搭子</button>`;
  }
  if (connect.request_id && connect.requires_questionnaire) {
    return `<a ${base} href="${SQUARE_URL}">TA 的请求需先填问卷 · 去搭子广场</a>`;
  }
  return `<button ${base} disabled>TA 暂无开放请求</button>`;
}

function bindConnectButtons() {
  document.body.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-action='connect']");
    if (!btn || btn.disabled) return;
    const uid = btn.getAttribute("data-uid");
    const original = btn.textContent;
    btn.disabled = true;
    btn.textContent = "发送中…";
    try {
      const res = await api(`/api/match/${currentUser()}/connect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_user_id: uid }),
      });
      if (res.mode === "intent") {
        btn.textContent = "已表达意向 ✓ 等待对方接受";
        btn.classList.remove("btn-primary");
      } else {
        btn.textContent = original;
        btn.disabled = false;
        alert(res.message || "暂时无法发起搭子");
      }
    } catch (err) {
      btn.textContent = original;
      btn.disabled = false;
      alert("操作失败：" + err.message);
    }
  });
}

function initProfileEditor() {
  const modal = document.querySelector("[data-profile-modal]");
  const open = document.querySelector("[data-edit-profile]");
  if (!modal || !open) return;
  const fill = (u) => {
    modal.querySelector("[data-profile-tags]").value = (u.tags || []).join("，");
    modal.querySelector("[data-profile-skills]").value = (u.questionnaire?.["技能"] || []).join("，");
    modal.querySelector("[data-profile-hours]").value = u.availability?.weekly_hours || "";
    modal.querySelector("[data-profile-channel]").value = u.collab?.channel || "";
  };
  open.onclick = () => loadUsers().then((list) => { const u = list.find((x) => x.id === currentUser()); if (u) fill(u); modal.style.display = "flex"; });
  modal.querySelector("[data-profile-close]").onclick = () => { modal.style.display = "none"; };
  modal.querySelector("[data-profile-save]").onclick = async () => {
    const tags = modal.querySelector("[data-profile-tags]").value.split(/[,，]/).map((s) => s.trim()).filter(Boolean);
    const skills = modal.querySelector("[data-profile-skills]").value.split(/[,，]/).map((s) => s.trim()).filter(Boolean);
    try { await api(`/api/users/${currentUser()}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tags, availability: { weekly_hours: Number(modal.querySelector("[data-profile-hours]").value) || 0 }, collab: { channel: modal.querySelector("[data-profile-channel]").value.trim() }, questionnaire: { 技能: skills } }) }); _usersPromise = null; modal.style.display = "none"; renderIdentity(); } catch (err) { modal.querySelector("[data-profile-error]").textContent = "保存失败：" + err.message; }
  };
}

function renderIdentity() {
  const wrap = document.querySelector("[data-identity]");
  if (!wrap) return;
  wrap.innerHTML = `<div class="match-loading"><div class="spin"></div><div>加载中…</div></div>`;
  loadUsers().then((list) => {
    const me = list.find((u) => u.id === currentUser());
    wrap.innerHTML = identityHTML(me || MOCK.user);
  });
}

// 身份卡：展示当前演示账号的真实画像与知乎兴趣
function identityHTML(u) {
  const zhihu = u.zhihu || {};
  const topics = (zhihu.topics || []).slice(0, 4);
  const mbti = u.mbti || getMbti();
  return `
    <div class="identity-avatar">${firstName(u.name)}</div>
    <div class="identity-name">${u.name}</div>
    ${u.school ? `<div class="identity-meta">${u.school}</div>` : ""}
    ${u.role ? `<div class="identity-meta">${u.role}</div>` : ""}
    <div class="identity-tags">${(u.tags || []).map((t) => `<span class="tag">${t}</span>`).join("")}</div>
    ${mbti ? `<div class="identity-row"><span class="tag tag-mbti">MBTI ${mbti}</span></div>` : ""}
    ${
      topics.length
        ? `<div class="identity-tags">${topics.map((t) => `<span class="tag tag-zhihu">知乎 · ${t}</span>`).join("")}</div>`
        : ""
    }
    ${zhihu.source === "mock" ? `<div class="identity-row"><span class="mock-badge">知乎兴趣 · 演示数据</span></div>` : ""}
    <div class="identity-row">
      <span class="score-badge"><span class="score-num">${u.score != null ? u.score : "-"}</span> 搭子信评分${
        u.level ? " · " + u.level : ""
      }</span>
    </div>
  `;
}

/* 首页推荐搭子：加载真实匹配结果（与「发起搭子」按钮同源） */
function loadHomeMatchList() {
  const wrap = document.querySelector("[data-home-match-list]");
  if (!wrap) return;
  wrap.innerHTML = `<div class="match-loading"><div class="spin"></div><div>正在推荐搭子…</div></div>`;
  api(`/api/match/${currentUser()}?match_type=interest&top_n=4`)
    .then((data) => renderMatchResults(data.results, "[data-home-match-list]", { compact: true }))
    .catch((err) => {
      wrap.innerHTML = `<div style="padding:16px;color:var(--color-accent)">搭子加载失败：${err.message}</div>`;
    });
}

function bindLikes() {
  document.body.addEventListener("click", async (e) => {
    const detail = e.target.closest("[data-action='post-detail']");
    if (detail) { openPostDetail(detail.getAttribute("data-post-id")); return; }
    const btn = e.target.closest("[data-action='like']");
    if (!btn || btn.disabled) return;
    const id = btn.getAttribute("data-post-id");
    if (!id) return;
    btn.disabled = true;
    try {
      const result = await api(`/api/posts/${encodeURIComponent(id)}/like`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: currentUser() }),
      });
      const post = forumPosts.find((p) => p.id === id);
      if (post) post.likes = result.likes;
      document.querySelectorAll("[data-action='like'][data-post-id]").forEach((button) => {
        if (button.getAttribute("data-post-id") === id) {
          button.textContent = `${result.liked ? "已赞" : "赞"} ${result.likes}`;
          button.setAttribute("aria-pressed", String(result.liked));
        }
      });
    } catch (err) { alert("点赞失败：" + err.message); }
    finally { btn.disabled = false; }
  });
}

async function openPostDetail(id) {
  let modal = document.querySelector("[data-post-detail-modal]");
  if (!modal) {
    modal = document.createElement("div");
    modal.className = "modal-mask";
    modal.setAttribute("data-post-detail-modal", "");
    document.body.appendChild(modal);
  }
  modal.style.display = "flex";
  modal.innerHTML = `<div class="modal"><div class="modal-body" data-detail-body>加载中…</div><div class="modal-footer"><button class="btn" data-detail-close>关闭</button></div></div>`;
  modal.querySelector("[data-detail-close]").onclick = () => { modal.style.display = "none"; };
  const body = modal.querySelector("[data-detail-body]");
  try {
    const data = await api(`/api/posts/${encodeURIComponent(id)}`);
    const post = data.post;
    const existing = forumPosts.find((p) => p.id === id);
    if (existing) Object.assign(existing, post);
    renderForumFeed();
    body.innerHTML = `<h2>${escapeHTML(post.title)}</h2>
      <p>${escapeHTML(post.author)} · ${escapeHTML(post.time)}</p>
      <div style="white-space:pre-wrap">${escapeHTML(post.excerpt)}</div>
      ${(post.zhihu_refs || []).map(zhihuRefHTML).join("")}
      <h3>评论</h3>
      ${(data.comments || []).map((c) => `<article><b>${escapeHTML(c.author)}</b><p style="white-space:pre-wrap">${escapeHTML(c.content)}</p></article>`).join("") || "暂无评论"}
      <form data-comment-form><label>发表评论<textarea class="form-input" name="content" required rows="3"></textarea></label>
      <p data-comment-error role="alert"></p><button class="btn btn-primary" type="submit">提交评论</button></form>`;
    body.querySelector("[data-comment-form]").onsubmit = async (event) => {
      event.preventDefault();
      const form = event.currentTarget;
      const content = form.elements.content.value.trim();
      if (!content) return;
      const submit = form.querySelector("button");
      submit.disabled = true;
      try {
        await api(`/api/posts/${encodeURIComponent(id)}/comments`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: currentUser(), content }),
        });
        await openPostDetail(id);
      } catch (err) {
        form.querySelector("[data-comment-error]").textContent = "评论失败：" + err.message;
        submit.disabled = false;
      }
    };
  } catch (err) { body.textContent = "详情加载失败：" + err.message; }
}

document.addEventListener("DOMContentLoaded", () => {
  initForumSearch();
  renderFeed(MOCK.feeds);
  renderHotList();
  renderIdentity();
  initProfileEditor();
  bindLikes();
  bindConnectButtons();
  initAccountSwitcher();
  initMbtiPage();
  initRequestsPage();
  initQuestionnaireModals();
  initForumPage();
  loadHomeMatchList();
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
      ${
        it.detail && it.detail.reasons && it.detail.reasons.length
          ? `<div class="reason-line">${it.detail.reasons[0]}</div>`
          : ""
      }
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
          ? `<div style="margin-top:10px">
              <div style="font-size:13px;color:var(--color-text-secondary);margin-bottom:6px">收到意向：${r.intent_people
                .map((p) => p.name)
                .join("、")}</div>
              <div style="display:flex;gap:8px;flex-wrap:wrap">${r.intent_people
                .map(
                  (p) =>
                    `<button class="btn btn-primary" style="height:28px;font-size:13px" data-action="accept" data-req="${r.id}" data-uid="${p.id}">接受 ${p.name}</button>`
                )
                .join("")}</div>
            </div>`
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
          loadMine();
        })
        .catch((err) => alert("接受失败：" + err.message));
    });
  }

  // 「我的请求」里直接接受意向，省去回到广场找「查看意向」的步骤
  myWrap.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action='accept']");
    if (!btn || btn.disabled) return;
    if (!confirm("确定接受 TA 成为你的搭子？")) return;
    btn.disabled = true;
    api(`/api/requests/${btn.getAttribute("data-req")}/accept`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: currentUser(), accepted_user_id: btn.getAttribute("data-uid") }),
    })
      .then(() => {
        loadMine();
        loadSquare();
      })
      .catch((err) => {
        btn.disabled = false;
        alert("接受失败：" + err.message);
      });
  });

  loadSquare();
}

/* ---------------- 自定义问卷：编辑器（发布者设计） ---------------- */
let publishQn = null;   // 发布流程中已保存的问卷 {id, title, questions}
let fillOnDone = null;  // 填写问卷完成后的回调（刷新广场）

/* ---------------- 竞赛组队问卷模板 ----------------
   依据建议文档 P1-2：覆盖比赛/项目类型、擅长角色、当前与期望阶段、
   每周投入、最晚合作时间、队伍规模、跨校/线上偏好。发布者套用后，
   可再逐题勾选「期望」以启用问卷匹配计分（未勾选则为中性分）。 */
const COMPETITION_QN_TEMPLATE = {
  title: "竞赛组队队友筛选",
  questions: [
    { id: "1", text: "你想参加的比赛或项目类型？", options: ["数学建模 / 美赛", "程序设计 / 算法", "创新创业 / 挑战杯", "工程实践 / 硬件", "数据分析 / 科研", "其他"], expected: [] },
    { id: "2", text: "你擅长的角色是？", options: ["产品", "设计", "前端开发", "后端开发", "算法", "运营 / 答辩"], expected: [] },
    { id: "3", text: "你目前处于哪个阶段？", options: ["有想法，还没起步", "已经组队，缺人", "进行中，需补位", "接近收尾"], expected: [] },
    { id: "4", text: "你期望加入什么阶段的队伍？", options: ["从零开始", "早期孵化", "中期加速", "已有基础补位"], expected: [] },
    { id: "5", text: "你每周能投入多少时间？", options: ["5 小时以下", "5~10 小时", "10~20 小时", "20 小时以上"], expected: [] },
    { id: "6", text: "你最晚能合作到什么时候？", options: ["1 周内", "1 个月内", "3 个月内", "长期不限"], expected: [] },
    { id: "7", text: "你希望的队伍规模？", options: ["2 人", "3~4 人", "5~6 人", "7 人以上"], expected: [] },
    { id: "8", text: "是否接受跨校 / 线上合作？", options: ["只接受同校线下", "接受线上", "跨校 + 线上都行"], expected: [] },
  ],
};

// 把一组题目渲染进问卷编辑器（供回填与套用模板共用）
function editorQuestionsHTML(questions) {
  return questions.map((q, qi) => {
    const opts = q.options.map((o, oi) => `
        <div class="qn-option-row">
          <label class="qn-expected"><input type="checkbox" data-qn-expected ${(q.expected || []).includes(oi) ? "checked" : ""} /> 期望</label>
          <input class="form-input" data-qn-opt value="${o}" />
          <button class="btn qn-remove" data-qn-remove-option>×</button>
        </div>`).join("");
    return `
      <div class="qn-block" data-qn-block="${qi}">
        <div class="qn-block-head">
          <span class="qn-block-title">题目 ${qi + 1}</span>
          <button class="btn qn-remove" data-qn-remove-question>删除题目</button>
        </div>
        <input class="form-input" data-qn-q-text value="${q.text}" />
        <div class="qn-options" data-qn-options>${opts}</div>
        <button class="btn btn-ghost" data-qn-add-option>+ 添加选项</button>
      </div>`;
  }).join("");
}

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
    wrap.innerHTML = editorQuestionsHTML(publishQn.questions);
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

    // 套用竞赛组队问卷模板：预填 8 道组队关键题，供发布者按需增删与勾选期望
    const compTmplBtn = document.querySelector("[data-qn-template-comp]");
    if (compTmplBtn) {
      compTmplBtn.addEventListener("click", () => {
        const wrap = document.querySelector("[data-qn-questions]");
        const hasContent = Array.from(wrap.querySelectorAll("[data-qn-q-text]"))
          .some((el) => el.value.trim());
        if (hasContent && !confirm("套用模板将覆盖当前编辑器中的问卷内容，确定继续？")) return;
        document.querySelector("[data-qn-title]").value = COMPETITION_QN_TEMPLATE.title;
        wrap.innerHTML = editorQuestionsHTML(COMPETITION_QN_TEMPLATE.questions);
        document.querySelector("[data-qn-error]").style.display = "none";
      });
    }

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