const assert = require("node:assert/strict");
const { test } = require("node:test");
const vm = require("node:vm");
const fs = require("node:fs");
const path = require("node:path");
const code = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");

function element() {
  const events = {};
  return {
    value: "", disabled: false, style: {}, innerHTML: "", textContent: "",
    addEventListener(name, fn) { (events[name] ||= []).push(fn); },
    fire(name, event = {}) { for (const fn of events[name] || []) fn(event); },
    click() { if (!this.disabled) this.fire("click"); },
  };
}

function setup(page, search = "", response = { source: "mock", fallback_reason: "missing_credentials", items: [] }) {
  const input = element(), btn = element(), body = element(), title = element();
  const box = page === "pages/forum.html" ? element() : null;
  if (box) box.querySelector = (s) => s.includes("-body") ? body : title;
  const selectors = { ".nav .search input": input, ".nav .search button": btn, "[data-zhihu-results]": box };
  const calls = [];
  const location = { pathname: `/frontend/${page}`, search, href: "unchanged" };
  const context = vm.createContext({
    window: { location }, URL, URLSearchParams,
    localStorage: { getItem: () => null },
    document: { addEventListener() {}, querySelector: (s) => selectors[s] || null },
    fetch: async (url) => {
      calls.push(url);
      if (response instanceof Error) throw response;
      return { ok: true, json: async () => response };
    },
  });
  vm.runInContext(code, context);
  context.initForumSearch();
  return { input, btn, body, title, box, calls, location };
}
const settled = () => new Promise((resolve) => setImmediate(resolve));

test("全部五页均具备公共搜索结构并加载 app.js，初始化不再依赖讨论区", () => {
  for (const page of ["index.html", "pages/requests.html", "pages/me.html", "pages/mbti.html", "pages/forum.html"]) {
    const html = fs.readFileSync(path.join(__dirname, "..", page), "utf8");
    assert.match(html, /class="nav"/);
    assert.match(html, /class="search">\s*<input[^>]+>\s*<button/);
    assert.match(html, /src="(?:\.\.\/)?js\/app.js"/);
  }
  assert.match(code, /DOMContentLoaded", \(\) => \{\s*initForumSearch\(\);/);
  assert.equal((code.match(/\n\s+initForumSearch\(\);/g) || []).length, 1);
});

for (const page of ["index.html", "pages/requests.html", "pages/me.html", "pages/mbti.html"]) {
  test(`${page} 点击和回车携带编码后的关键词跳转，空白和输入法确认不跳转`, () => {
    const s = setup(page);
    s.input.value = "  "; s.btn.click();
    assert.equal(s.location.href, "unchanged");
    s.input.value = "  数学 & C++?  ";
    s.input.fire("keydown", { key: "Enter", isComposing: true });
    assert.equal(s.location.href, "unchanged");
    const expected = `${page === "index.html" ? "pages/" : ""}forum.html?q=${encodeURIComponent("数学 & C++?")}`;
    s.btn.click(); assert.equal(s.location.href, expected);
    s.location.href = "unchanged";
    s.input.fire("keydown", { key: "Enter", preventDefault() {} });
    assert.equal(s.location.href, expected);
    assert.equal(s.calls.length, 0);
  });
}

test("讨论区 q 自动且仅一次搜索，沿用 mock 来源和失败原因标注", async () => {
  const s = setup("pages/forum.html", `?q=${encodeURIComponent(" 数学 & C++? ")}`);
  s.btn.click();
  await settled();
  assert.equal(s.calls.length, 1);
  assert.equal(s.calls[0], `http://localhost:8001/api/zhihu/search?query=${encodeURIComponent("数学 & C++?")}&count=6`);
  assert.equal(s.input.value, "数学 & C++?");
  assert.match(s.title.textContent, /mock，非真实知乎内容；未配置凭据/);
  assert.match(s.body.innerHTML, /未找到相关内容/);
  assert.equal(s.box.style.display, "");
  assert.equal(s.btn.disabled, false);
});

test("无 q 或空白 q 不搜索；讨论区点击与回车可搜索", async () => {
  for (const query of ["", "?q=%20%20"]) {
    const s = setup("pages/forum.html", query);
    assert.equal(s.calls.length, 0);
    s.input.value = "算法";
    s.input.fire("keydown", { key: "Enter", isComposing: true });
    assert.equal(s.calls.length, 0);
    s.input.fire("keydown", { key: "Enter", preventDefault() {} });
    await settled();
    s.input.value = "英语"; s.input.fire("input"); s.btn.click();
    await settled();
    assert.equal(s.calls.length, 2);
  }
});

test("真实来源结果安全渲染；服务断连明确报错并恢复按钮", async () => {
  const real = setup("pages/forum.html", "?q=test", {
    source: "zhihu", items: [{ Title: "<script>bad</script>", Url: "https://www.zhihu.com/question/123", ContentText: "摘要", AuthorName: "作者" }],
  });
  const failed = setup("pages/forum.html", "?q=test", new Error("offline"));
  await settled();
  assert.match(real.body.innerHTML, /&lt;script&gt;/);
  assert.match(real.body.innerHTML, /https:\/\/www.zhihu.com\/question\/123/);
  assert.doesNotMatch(real.body.innerHTML, /演示数据/);
  assert.match(failed.body.textContent, /搜索失败/);
  assert.equal(failed.btn.disabled, false);
});
