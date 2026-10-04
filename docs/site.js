// GamePadTester 소개 페이지: 언어·테마, 최신 릴리스 정보, 화면 갤러리, 웹 체험판(Gamepad API).
// 빌드 도구 없이 동작한다. 패드 그림 데이터(pads.js)는 tools/docs_web.py가 앱의 배치에서 만든다.
"use strict";

(function () {
  const REPO = "deuxdoom/GamePadTester";
  const IMAGE_REVISION = "c132dbed9e6f";
  const RELEASES = `https://github.com/${REPO}/releases/latest`;
  const LANGS = ["ko", "en", "ja", "zh-Hans", "zh-Hant", "es"];
  const LANG_NAMES = { ko: "한국어", en: "English", ja: "日本語", "zh-Hans": "简体中文", "zh-Hant": "繁體中文", es: "Español" };
  // 원형도는 gamepad-tester.com과 같은 방식: π/16 반올림 32구간, 반지름 0.2 초과, 구간 최대 반지름의 RMS 오차
  const CIRCLE_BINS = 32;
  const CIRCLE_SAMPLE_RADIUS = 0.2;
  const CIRCLE_SECONDS = 10;
  const CIRCLE_MIN_RADIUS = 0.6;   // 10초 타이머를 시작하는 가장자리 반지름
  const SVG = "http://www.w3.org/2000/svg";

  // 스크립트에서 쓰는 한국어 기본 문구(다른 언어는 i18n.js)
  const KO_JS = {
    "try.connected": "{name}",
    "try.demoOn": "데모 패드가 움직이는 중 · 패드의 아무 버튼이나 누르면 바로 바뀝니다",
    "try.demoStop": "데모 멈추기",
    "try.circStop": "측정 중지",
    "try.circWaiting": "스틱을 끝까지 미세요.",
    "try.circRunning": "남은 시간 {seconds}초 · 계속 돌리세요.",
    "try.circDone": "끝! 평균 오차 왼쪽 {left} · 오른쪽 {right}",
    "try.circIncomplete": "측정 범위 부족(채움 {coverage}%)",
    "grade.excellent": "우수", "grade.good": "양호", "grade.fair": "보통", "grade.poor": "미흡",
    "dl.size": "{size} MB",
    "dl.date": "{date} 공개",
    "screens.alt": "{name} 화면",
    "screens.play": "자동 넘김 재생",
    "screens.pause": "자동 넘김 일시 정지",
    "meta.title": document.title,
    "meta.desc": document.querySelector('meta[name="description"]').getAttribute("content"),
  };

  // ---- 저장소(사용할 수 없으면 무시) ----
  function load(key) { try { return localStorage.getItem(key); } catch (error) { return null; } }
  function save(key, value) { try { localStorage.setItem(key, value); } catch (error) { /* 저장 없이 계속 */ } }

  // ---- 언어 ----
  const defaults = { text: new Map(), html: new Map(), attr: new Map() };
  let language = "ko";

  function shot(name) {
    // 한국어가 아니면 영어 캡처, 라이트테마면 같은 테마의 캡처를 쓴다.
    const light = document.documentElement.dataset.theme === "light";
    return `images/${name}${language === "ko" ? "" : ".en"}${light ? ".light" : ""}.webp?v=${IMAGE_REVISION}`;
  }

  function updateImages() {
    document.querySelectorAll(".hero-visual img[data-shot]").forEach((image) => { image.src = shot(image.dataset.shot); });
  }

  function collectDefaults() {
    document.querySelectorAll("[data-i18n]").forEach((node) => defaults.text.set(node.dataset.i18n, node.textContent));
    document.querySelectorAll("[data-i18n-html]").forEach((node) => defaults.html.set(node.dataset.i18nHtml, node.innerHTML));
    document.querySelectorAll("[data-i18n-attr]").forEach((node) => {
      node.dataset.i18nAttr.split(";").forEach((pair) => {
        const [attr, key] = pair.split(":");
        defaults.attr.set(key, node.getAttribute(attr) || "");
      });
    });
  }

  function t(key, vars) {
    const table = (window.GPT_I18N || {})[language] || {};
    let text = table[key];
    if (text === undefined) {
      text = defaults.text.get(key) ?? defaults.html.get(key) ?? defaults.attr.get(key) ?? KO_JS[key] ?? key;
    }
    if (vars) {
      text = text.replace(/\{(\w+)\}/g, (match, name) => (name in vars ? String(vars[name]) : match));
    }
    return text;
  }

  function detectLanguage() {
    const asked = new URLSearchParams(location.search).get("lang");   // 공유용 주소: ?lang=en
    if (asked && LANGS.includes(asked)) return asked;
    const saved = load("gpt-lang");
    if (saved && LANGS.includes(saved)) return saved;
    for (const raw of navigator.languages || [navigator.language || "ko"]) {
      const code = raw.toLowerCase();
      if (code.startsWith("ko")) return "ko";
      if (code.startsWith("ja")) return "ja";
      if (code.startsWith("es")) return "es";
      if (code.startsWith("zh")) return /hant|tw|hk|mo/.test(code) ? "zh-Hant" : "zh-Hans";
      if (code.startsWith("en")) return "en";
    }
    return "en";
  }

  function applyLanguage(code, remember) {
    language = LANGS.includes(code) ? code : "en";
    if (remember) save("gpt-lang", language);
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
    document.querySelectorAll("[data-i18n-html]").forEach((node) => { node.innerHTML = t(node.dataset.i18nHtml); });
    document.querySelectorAll("[data-i18n-attr]").forEach((node) => {
      node.dataset.i18nAttr.split(";").forEach((pair) => {
        const [attr, key] = pair.split(":");
        node.setAttribute(attr, t(key));
      });
    });
    document.title = t("meta.title");
    document.querySelector('meta[name="description"]').setAttribute("content", t("meta.desc"));
    document.getElementById("lang-current").textContent = LANG_NAMES[language];
    document.querySelectorAll("#lang-menu [data-lang]").forEach((item) => {
      item.setAttribute("aria-checked", String(item.dataset.lang === language));
    });
    renderRelease();
    tester.refreshTexts();
    updateImages();
    gallery.refresh();
    updateDemo.refreshTexts();
  }

  function setupLanguageMenu() {
    const button = document.getElementById("lang-button");
    const menu = document.getElementById("lang-menu");
    const close = () => { menu.hidden = true; button.setAttribute("aria-expanded", "false"); };
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      menu.hidden = !menu.hidden;
      button.setAttribute("aria-expanded", String(!menu.hidden));
    });
    menu.addEventListener("click", (event) => {
      const item = event.target.closest("[data-lang]");
      if (!item) return;
      const change = () => applyLanguage(item.dataset.lang, true);
      document.startViewTransition ? document.startViewTransition(change) : change();
      close();
    });
    document.addEventListener("click", close);
    document.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); });
  }

  // ---- 테마 ----
  function setupTheme() {
    document.getElementById("theme-button").addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      const change = () => {
        document.documentElement.dataset.theme = next;
        save("gpt-theme", next);
        updateImages();
        updateDemo.refreshTexts();
        gallery.refresh();
      };
      document.startViewTransition ? document.startViewTransition(change) : change();
    });
  }

  // ---- 최신 릴리스 ----
  let release = null;

  async function fetchRelease() {
    const cached = (() => { try { return JSON.parse(sessionStorage.getItem("gpt-release") || "null"); } catch (e) { return null; } })();
    if (cached && Date.now() - cached.at < 30 * 60 * 1000) {
      release = cached.data;
      renderRelease();
      return;
    }
    try {
      const response = await fetch(`https://api.github.com/repos/${REPO}/releases/latest`, { headers: { Accept: "application/vnd.github+json" } });
      if (!response.ok) return;
      const data = await response.json();
      const asset = (data.assets || []).find((item) => /^GamePadTester_v?\d+\.zip$/i.test(item.name));
      release = {
        tag: data.tag_name, date: data.published_at, page: data.html_url,
        url: asset ? asset.browser_download_url : data.html_url,
        size: asset ? asset.size : 0, sha: asset && /^sha256:[0-9a-f]{64}$/i.test(asset.digest || "") ? asset.digest.slice(7) : "",
      };
      try { sessionStorage.setItem("gpt-release", JSON.stringify({ at: Date.now(), data: release })); } catch (e) { /* 무시 */ }
      renderRelease();
    } catch (error) {
      /* 연결이 안 되면 정적 링크(릴리스 페이지)를 그대로 쓴다. */
    }
  }

  function renderRelease() {
    if (!release) return;
    document.querySelectorAll(".version-text").forEach((node) => { node.textContent = release.tag; });
    const date = new Date(release.date);
    document.getElementById("dl-date").textContent = isNaN(date) ? "" :
      t("dl.date", { date: new Intl.DateTimeFormat(language, { dateStyle: "medium" }).format(date) });
    document.getElementById("dl-size").textContent = release.size ? t("dl.size", { size: (release.size / 1048576).toFixed(1) }) : "";
    document.getElementById("dl-link").href = release.url;
    document.getElementById("hero-download").href = release.url;          // 최신 릴리스의 ZIP을 바로 받는다
    document.getElementById("release-chip").href = release.page || RELEASES; // 누르면 최신 릴리스 페이지

    const box = document.getElementById("dl-sha-box");
    box.hidden = !release.sha;
    document.getElementById("dl-sha").textContent = release.sha.toUpperCase();
  }

  function setupCopy() {
    document.getElementById("dl-copy").addEventListener("click", async () => {
      const text = document.getElementById("dl-sha").textContent;
      try { await navigator.clipboard.writeText(text); } catch (error) { return; }
      const button = document.getElementById("dl-copy");
      button.classList.add("copied");
      setTimeout(() => button.classList.remove("copied"), 1200);
    });
  }

  // ---- 화면 갤러리: 애플 제품 페이지처럼 일정 시간마다 다음 화면으로 넘어가는 가로 슬라이드 ----
  // 점이나 화면을 직접 고르거나 손가락으로 넘기면 자동 넘김을 멈추고, 재생 버튼으로 다시 시작한다.
  // 갤러리가 화면 밖에 있거나 탭이 숨겨졌거나 확대 보기가 열려 있는 동안은 시간을 세지 않는다.
  // 동작 줄이기(prefers-reduced-motion) 환경에서도 자동 넘김은 하되, 미끄러지는 이동 없이 바로 바꾼다.
  const gallery = {
    index: 0, elapsed: 0, last: 0, duration: 5000,
    playing: true, visible: false, running: false, settleTimer: 0, lockUntil: 0,

    setup() {
      this.root = document.getElementById("gallery");
      this.track = document.getElementById("gallery-track");
      this.play = document.getElementById("gallery-play");
      this.dialog = document.getElementById("lightbox");
      this.slides = [...this.track.querySelectorAll(".gallery-slide")];
      this.reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
      const dots = this.root.querySelector(".gallery-dots");
      this.dots = this.slides.map((slide, index) => {
        const dot = document.createElement("button");
        dot.type = "button";
        dot.setAttribute("role", "tab");
        dot.append(document.createElement("span"));
        dot.addEventListener("click", () => { this.pause(); this.go(index); });
        dots.append(dot);
        return dot;
      });
      this.slides.forEach((slide, index) => {
        slide.querySelector(".gallery-view").addEventListener("click", () => {
          if (index !== this.index) { this.pause(); this.go(index); return; }
          document.getElementById("lightbox-image").src = shot(slide.dataset.shot);
          this.dialog.showModal();
        });
      });
      this.dialog.addEventListener("click", (event) => { if (event.target === this.dialog) this.dialog.close(); });
      this.play.addEventListener("click", () => (this.playing ? this.pause() : this.resume()));
      this.track.addEventListener("scroll", () => this.settle(), { passive: true });
      this.root.addEventListener("keydown", (event) => {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        const onDot = this.dots.includes(document.activeElement);
        this.pause();
        this.go((this.index + (event.key === "ArrowRight" ? 1 : this.slides.length - 1)) % this.slides.length);
        if (onDot) this.dots[this.index].focus();
      });
      new IntersectionObserver((entries) => {
        this.visible = entries.some((entry) => entry.isIntersecting);
        this.loop();
      }, { threshold: 0.35 }).observe(this.track);
      window.addEventListener("resize", () => this.align(false));
      this.go(0, false);
      this.refresh();
    },

    go(index, smooth = true) {
      const total = this.slides.length;
      this.index = index;
      this.elapsed = 0;
      this.slides.forEach((slide, position) => {
        const current = position === index;
        slide.classList.toggle("current", current);
        slide.setAttribute("aria-hidden", String(!current));
        slide.querySelector(".gallery-view").tabIndex = current ? 0 : -1;
        // 지금 화면과 다음 화면은 미리 받아 둔다(넘어갈 때 빈 그림이 보이지 않게).
        if (current || position === (index + 1) % total) slide.querySelector("img").loading = "eager";
      });
      this.dots.forEach((dot, position) => {
        dot.setAttribute("aria-selected", String(position === index));
        dot.tabIndex = position === index ? 0 : -1;
        dot.style.removeProperty("--progress");
      });
      this.align(smooth);
    },

    align(smooth) {
      const slide = this.slides[this.index];
      const left = slide.offsetLeft - (this.track.clientWidth - slide.offsetWidth) / 2;
      const animate = smooth && !this.reduced.matches;
      this.lockUntil = performance.now() + (animate ? 1200 : 100);
      this.track.scrollTo({ left, behavior: animate ? "smooth" : "auto" });
    },

    // 사용자가 손가락·휠로 넘긴 경우: 스크롤이 멈춘 뒤 가운데에 가장 가까운 화면을 현재 화면으로 삼는다.
    settle() {
      clearTimeout(this.settleTimer);
      this.settleTimer = setTimeout(() => {
        if (performance.now() < this.lockUntil) { this.settle(); return; }
        const middle = this.track.scrollLeft + this.track.clientWidth / 2;
        let nearest = this.index;
        let best = Infinity;
        this.slides.forEach((slide, position) => {
          const distance = Math.abs(slide.offsetLeft + slide.offsetWidth / 2 - middle);
          if (distance < best) { best = distance; nearest = position; }
        });
        if (nearest !== this.index) { this.pause(); this.go(nearest, false); }
      }, 140);
    },

    pause() { this.playing = false; this.refreshButton(); },

    resume() {
      this.playing = true;
      this.refreshButton();
      this.loop();
    },

    loop() {
      if (this.running || !this.visible) return;
      this.running = true;
      this.last = 0;
      const tick = (time) => {
        if (!this.visible) { this.running = false; return; }
        const counting = this.playing && !document.hidden && !this.dialog.open;
        if (counting && this.last) this.elapsed += Math.min(100, time - this.last);
        this.last = time;
        this.dots[this.index].style.setProperty("--progress", String(Math.min(1, this.elapsed / this.duration)));
        if (this.elapsed >= this.duration) this.go((this.index + 1) % this.slides.length);
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    },

    refreshButton() {
      const label = t(this.playing ? "screens.pause" : "screens.play");
      this.play.dataset.state = this.playing ? "playing" : "paused";
      this.play.setAttribute("aria-label", label);
      this.play.title = label;
    },

    // 언어·테마가 바뀌면 그림 주소와 대체 글자, 점 이름을 다시 쓴다.
    refresh() {
      if (!this.root) return;
      const total = this.slides.length;
      this.slides.forEach((slide, position) => {
        const name = slide.querySelector("figcaption strong").textContent;
        const image = slide.querySelector("img");
        const source = shot(slide.dataset.shot);
        if (image.getAttribute("src") !== source) image.src = source;
        image.alt = t("screens.alt", { name });
        slide.setAttribute("aria-label", `${position + 1} / ${total}`);
        this.dots[position].setAttribute("aria-label", name);
      });
      const lightbox = document.getElementById("lightbox-image");
      const current = this.slides[this.index];
      lightbox.alt = current.querySelector("img").alt;
      if (this.dialog.open) lightbox.src = shot(current.dataset.shot);
      this.refreshButton();
    },
  };

  // ---- 웹 체험판 ----
  function familyOf(id) {
    const text = (id || "").toLowerCase();
    if (/054c|dualsense|dualshock|playstation/.test(text)) return "playstation";
    if (/057e|pro controller|nintendo|switch/.test(text)) return "nintendo";
    return "xbox";
  }

  function el(name, attrs, parent) {
    const node = document.createElementNS(SVG, name);
    for (const [key, value] of Object.entries(attrs || {})) node.setAttribute(key, value);
    if (parent) parent.appendChild(node);
    return node;
  }

  function cssVar(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }

  const tester = {
    svg: null, family: "", parts: {}, demo: true, padIndex: -1, padId: "", lastTimestamp: 0, rateTimes: [],
    circle: { running: false, started: 0, left: new Float32Array(CIRCLE_BINS), right: new Float32Array(CIRCLE_BINS), done: false },

    setup() {
      this.svg = document.getElementById("pad-svg");
      if (!window.GPT_PADS) return;
      if (!("getGamepads" in navigator)) document.getElementById("try-unsupported").hidden = false;
      this.build("xbox");
      window.addEventListener("gamepadconnected", (event) => { if (event.gamepad.axes.length >= 2) this.demo = false; this.refreshTexts(); });
      window.addEventListener("gamepaddisconnected", (event) => {
        if (event.gamepad.index === this.padIndex) this.padIndex = -1;   // 고정한 패드가 빠졌을 때만 다시 고른다
        this.refreshTexts();
      });
      document.getElementById("demo-button").addEventListener("click", () => { this.demo = !this.demo; this.refreshTexts(); });
      document.getElementById("circ-button").addEventListener("click", () => this.toggleCircle());
      requestAnimationFrame((time) => this.frame(time));
    },

    build(family) {
      const pad = window.GPT_PADS[family];
      this.family = family;
      const svg = this.svg;
      svg.replaceChildren();
      const [bx, by, bw, bh] = pad.bounds;
      svg.setAttribute("viewBox", `${bx} ${by} ${bw} ${bh}`);
      svg.style.aspectRatio = `${bw} / ${bh}`;
      const defs = el("defs", {}, svg);
      const parts = { buttons: {}, labels: {}, triggers: [], sticks: [] };
      pad.triggers.forEach(([x, y, w, h], index) => {
        const clip = el("clipPath", { id: `trigger-clip-${index}` }, defs);
        // 트리거는 세로로 선 캡슐(앱과 같다), 값은 아래에서 차오른다.
        el("rect", { x, y, width: w, height: h, rx: w / 2 }, clip);
        el("rect", { class: "part", x, y, width: w, height: h, rx: w / 2 }, svg);
        const fill = el("rect", { class: "trigger-fill", x, y: y + h, width: w, height: 0, "clip-path": `url(#trigger-clip-${index})` }, svg);
        const label = el("text", { class: "label", x: x + w / 2, y: y + 37 }, svg);
        label.textContent = pad.triggerLabels[index];
        const value = el("text", { class: "value", x: x + w / 2, y: y + 74 }, svg);
        value.textContent = "0%";
        parts.triggers.push({ fill, value, y, h });
      });
      pad.shoulders.forEach(([x, y, w, h], index) => {
        const button = 4 + index;
        parts.buttons[button] = el("rect", { class: "part", x, y, width: w, height: h, rx: h / 2 }, svg);
        parts.labels[button] = el("text", { class: "label", x: x + w / 2, y: y + h / 2 }, svg);
        parts.labels[button].textContent = pad.labels[button] || "";
      });
      // 앱과 같은 단일 외곽선. DualSense는 흐린 앞판 이음선과 스피커 구멍을 함께 그린다.
      el("path", { class: "body", d: pad.body }, svg);
      pad.seams.forEach((d) => el("path", { class: "seam", d }, svg));
      pad.grille.forEach(([cx, cy]) => el("circle", { class: "hole", cx, cy, r: pad.grilleRadius }, svg));
      if (pad.dpadWell > 0) el("circle", { class: "well", cx: pad.dpad[0], cy: pad.dpad[1], r: pad.dpadWell }, svg);
      // 터치패드 윗변은 몸체 윤곽과 같은 곡선이다(앱이 만든 경로를 그대로 쓴다).
      if (pad.touchpad) parts.buttons[17] = el("path", { class: "part", d: pad.touchpad }, svg);
      [pad.leftStick, pad.rightStick].forEach(([cx, cy], index) => {
        el("circle", { class: "well", cx, cy, r: pad.stickWell }, svg);
        const color = index ? "var(--stick-right)" : "var(--stick-left)";
        const cap = el("circle", { class: "cap part", cx, cy, r: pad.stickCap, stroke: color }, svg);
        const ring = el("circle", { cx, cy, r: pad.stickCap * pad.stickRing, fill: "none", stroke: "var(--border)", "stroke-width": 1.5 }, svg);
        parts.sticks.push({ cap, ring, cx, cy, button: 10 + index });
      });
      // 방향 버튼: 십자의 둥근 팔 또는 DualSense식 화살표 키(앱이 만든 경로). 십자는 가운데 칸을 덮는다.
      for (const [button, d] of Object.entries(pad.dpadKeys)) parts.buttons[button] = el("path", { class: "part", d }, svg);
      if (pad.dpadHub) {
        const [x, y, w, h] = pad.dpadHub;
        el("rect", { x, y, width: w, height: h, fill: "var(--card-alt)" }, svg);
      }
      const [fx, fy] = pad.face;
      [[0, 0, 1], [1, 1, 0], [2, -1, 0], [3, 0, -1]].forEach(([button, sx, sy]) => {
        const cx = fx + sx * pad.faceOffset, cy = fy + sy * pad.faceOffsetY;
        const tint = pad.faceColors[button] || "";
        const circle = el("circle", { class: "part", cx, cy, r: pad.faceRadius }, svg);
        if (tint) circle.style.stroke = tint;
        parts.buttons[button] = circle;
        parts.labels[button] = this.glyph(svg, cx, cy, pad.labels[button] || "", tint, pad.faceRadius, pad.glyphScale);
      });
      pad.small.forEach((item) => {
        const [x, y, w, h] = item.rect;
        const shape = item.shape === "circle" ? el("ellipse", { class: "part", cx: x + w / 2, cy: y + h / 2, rx: w / 2, ry: h / 2 }, svg)
          : el("rect", { class: "part", x, y, width: w, height: h, rx: item.shape === "square" ? 6 : Math.min(w, h) / 2 }, svg);
        if (item.angle) shape.setAttribute("transform", `rotate(${item.angle} ${x + w / 2} ${y + h / 2})`);
        parts.buttons[item.button] = shape;
        const inside = item.glyph || (item.shape === "circle" && w >= 36);
        const label = el("text", { class: "label", x: x + w / 2, y: inside ? y + h / 2 : y + h + 14 }, svg);
        label.textContent = item.glyph || item.label;
        if (item.glyph) label.style.fontSize = "20px";
        if (inside) parts.labels[item.button] = label;
      });
      this.parts = parts;
    },

    glyph(svg, cx, cy, label, tint, radius, scale) {
      const size = radius * scale;
      const style = { class: "glyph", stroke: tint || "var(--muted)" };
      if (label === "✕") return el("path", { ...style, d: `M${cx - size} ${cy - size}L${cx + size} ${cy + size}M${cx - size} ${cy + size}L${cx + size} ${cy - size}` }, svg);
      if (label === "○") return el("circle", { ...style, cx, cy, r: size * 1.1 }, svg);
      if (label === "□") return el("rect", { ...style, x: cx - size, y: cy - size, width: size * 2, height: size * 2 }, svg);
      if (label === "△") return el("path", { ...style, d: `M${cx} ${cy - size * 1.15}L${cx + size * 1.1} ${cy + size * 0.8}L${cx - size * 1.1} ${cy + size * 0.8}Z` }, svg);
      const text = el("text", { class: "label", x: cx, y: cy }, svg);
      text.textContent = label;
      text.style.fontSize = "24px";
      text.style.fontWeight = "800";
      if (tint) text.style.fill = tint;
      return text;
    },

    readPad() {
      // 브라우저는 보안상 페이지를 연 뒤 패드 버튼을 한 번 눌러야 이미 연결된 패드를 보여 준다.
      // 무선 수신기는 축이 없는 보조 인터페이스를 함께 내보내기도 하므로(실측: Leadjoy) 축이 있는 패드만 고른다.
      // 가만히 있어도 보고서를 계속 보내는 패드(프로콘2 등)가 함께 있으면 '최근 입력' 기준으로는 매 프레임 대상이
      // 바뀌므로, 한 번 고른 패드는 연결이 끊길 때까지 고정해서 한 장치만 보여 준다.
      const pads = navigator.getGamepads ? Array.from(navigator.getGamepads()).filter((pad) => pad && pad.connected) : [];
      const usable = pads.filter((pad) => pad.axes.length >= 2);
      const pool = usable.length ? usable : pads;
      if (!pool.length) { this.padIndex = -1; return null; }
      const locked = pool.find((pad) => pad.index === this.padIndex && pad.id === this.padId);
      if (locked) return locked;
      // 처음에는 버튼을 누르거나 스틱을 크게 움직인 패드를 고르고, 없으면 표준 매핑·앞 번호 패드를 쓴다.
      // 트리거·방향 패드를 축으로 보내는 패드는 쉬는 값이 ±1이라 앞의 네 축(두 스틱)만 본다.
      const pressed = (button) => (typeof button === "object" ? button.pressed || button.value > 0.5 : button > 0.5);
      const active = (pad) => pad.buttons.some(pressed) || pad.axes.slice(0, 4).some((value) => Math.abs(value) > 0.6);
      const best = pool.find(active) || pool.find((pad) => pad.mapping === "standard") || pool[0];
      this.padIndex = best.index;
      this.padId = best.id;
      return best;
    },

    demoState(time) {
      const t = (time / 1000) % 12;
      const buttons = new Array(18).fill(0);
      let lx = 0, ly = 0, rx = 0, ry = 0;
      if (t < 6) {
        const a = (2 * Math.PI * t) / 1.4, b = (-2 * Math.PI * t) / 1.7 + 0.6;
        const ra = 1 + 0.015 * Math.cos(4 * a), rb = 1 + 0.01 * Math.cos(4 * b);
        lx = ra * Math.cos(a); ly = ra * Math.sin(a); rx = rb * Math.cos(b); ry = rb * Math.sin(b);
      } else if (t >= 9) {
        const p = ((t - 9) / 3) * 2 * Math.PI;
        lx = 0.4 * Math.cos(p); ly = 0.4 * Math.sin(p); rx = -0.3 * Math.sin(p); ry = 0.3 * Math.cos(p);
      }
      buttons[Math.floor(time / 300) % 16] = (time % 300) < 150 ? 1 : 0;
      const tri = (time / 1800) % 2;
      buttons[6] = tri < 1 ? tri : 2 - tri;
      buttons[7] = 1 - buttons[6];
      return { axes: [lx, ly, rx, ry], buttons, id: "", timestamp: 0 };
    },

    frame(time) {
      const real = this.readPad();
      if (real && this.demo) { this.demo = false; this.refreshTexts(); }
      const state = real ? { axes: real.axes, buttons: real.buttons.map((b) => (typeof b === "object" ? b.value : b)), id: real.id, timestamp: real.timestamp }
        : this.demo ? this.demoState(time) : null;
      const family = real ? familyOf(real.id) : "playstation";
      if (state && family !== this.family) this.build(family);
      if (state) this.draw(state);
      if (real) this.measureRate(real.timestamp, time);
      this.updateCircle(state, time);
      requestAnimationFrame((next) => this.frame(next));
    },

    draw(state) {
      const pad = window.GPT_PADS[this.family];
      const parts = this.parts;
      for (const [index, node] of Object.entries(parts.buttons)) {
        const on = (state.buttons[index] || 0) > 0.5;
        node.classList.toggle("on", on);
        const tint = pad.faceColors[index];
        node.style.fill = on && tint ? tint : "";
        const label = parts.labels[index];
        if (label && label.tagName === "text") label.classList.toggle("on", on && !tint);
        if (label && tint) label.style[label.tagName === "text" ? "fill" : "stroke"] = on ? "#fff" : tint;
      }
      parts.triggers.forEach((trigger, index) => {
        const value = Math.max(0, Math.min(1, state.buttons[6 + index] || 0));
        trigger.fill.setAttribute("y", trigger.y + trigger.h * (1 - value));
        trigger.fill.setAttribute("height", trigger.h * value);
        trigger.value.textContent = `${Math.round(value * 100)}%`;
      });
      const travel = pad.stickWell - pad.stickCap * 0.72;
      parts.sticks.forEach((stick, index) => {
        const x = state.axes[index * 2] || 0, y = state.axes[index * 2 + 1] || 0;
        const cx = stick.cx + Math.max(-1, Math.min(1, x)) * travel, cy = stick.cy + Math.max(-1, Math.min(1, y)) * travel;
        for (const node of [stick.cap, stick.ring]) { node.setAttribute("cx", cx); node.setAttribute("cy", cy); }
        stick.cap.classList.toggle("on", (state.buttons[stick.button] || 0) > 0.5);
      });
    },

    measureRate(timestamp, time) {
      if (timestamp && timestamp !== this.lastTimestamp) {
        this.lastTimestamp = timestamp;
        this.rateTimes.push(time);
      }
      while (this.rateTimes.length && time - this.rateTimes[0] > 1000) this.rateTimes.shift();
      if (Math.floor(time / 250) !== Math.floor((time - 16) / 250)) {
        document.getElementById("rate-value").textContent = this.rateTimes.length > 2 ? String(this.rateTimes.length) : "–";
      }
    },

    toggleCircle() {
      const circle = this.circle;
      if (circle.running) {
        circle.running = false;
      } else {
        circle.left.fill(0); circle.right.fill(0);
        circle.running = true; circle.started = 0; circle.done = false;
      }
      this.refreshTexts();
    },

    updateCircle(state, time) {
      const circle = this.circle;
      if (circle.running && state) {
        [[circle.left, 0], [circle.right, 2]].forEach(([bins, base]) => {
          const x = state.axes[base] || 0, y = state.axes[base + 1] || 0;
          const r = Math.hypot(x, y);
          if (r <= CIRCLE_SAMPLE_RADIUS) return;
          if (!circle.started && r >= CIRCLE_MIN_RADIUS) circle.started = time;
          const bin = ((Math.round(Math.atan2(y, x) / (Math.PI / 16)) % CIRCLE_BINS) + CIRCLE_BINS) % CIRCLE_BINS;
          bins[bin] = Math.max(bins[bin], r);
        });
        if (circle.started && time - circle.started >= CIRCLE_SECONDS * 1000) {
          circle.running = false;
          circle.done = true;
          this.refreshTexts();
        } else if (Math.floor(time / 100) !== Math.floor((time - 16) / 100)) {
          this.refreshTexts(time);
        }
      }
      this.drawCircle("circ-left", circle.left, "--stick-left", state ? [state.axes[0], state.axes[1]] : null);
      this.drawCircle("circ-right", circle.right, "--stick-right", state ? [state.axes[2], state.axes[3]] : null);
    },

    result(bins) {
      const filled = Array.from(bins).filter((r) => r > 0);
      const coverage = filled.length / CIRCLE_BINS;
      if (filled.length < CIRCLE_BINS / 4) return { error: null, grade: null, coverage, complete: false };
      const error = Math.sqrt(filled.reduce((sum, r) => sum + (1 - r) ** 2, 0) / filled.length) * 100;
      const complete = coverage >= 0.95;
      const grade = complete ? (error <= 3 ? "excellent" : error <= 6 ? "good" : error <= 10 ? "fair" : "poor") : null;
      return { error, grade, coverage, complete };
    },

    drawCircle(id, bins, colorVar, point) {
      const canvas = document.getElementById(id);
      const ratio = window.devicePixelRatio || 1;
      const size = canvas.clientWidth || 240;
      if (canvas.width !== Math.round(size * ratio)) { canvas.width = Math.round(size * ratio); canvas.height = Math.round(size * ratio); }
      const g = canvas.getContext("2d");
      g.setTransform(ratio, 0, 0, ratio, 0, 0);
      g.clearRect(0, 0, size, size);
      const c = size / 2, unit = size * 0.4, color = cssVar(colorVar);
      g.strokeStyle = cssVar("--border-strong"); g.lineWidth = 1.5;
      g.beginPath(); g.arc(c, c, unit, 0, Math.PI * 2); g.stroke();
      g.strokeStyle = cssVar("--border"); g.beginPath(); g.moveTo(c - unit, c); g.lineTo(c + unit, c); g.moveTo(c, c - unit); g.lineTo(c, c + unit); g.stroke();
      const filled = Array.from(bins).some((r) => r > 0);
      if (filled) {
        // 앱과 같은 쐐기 표시: 구간마다 최대 반지름까지 부채꼴을 채우고, 1.0에서 벗어날수록 빨강으로 섞는다.
        const rgb = (hex) => { const v = parseInt(hex.replace("#", "").slice(0, 6), 16); return [(v >> 16) & 255, (v >> 8) & 255, v & 255]; };
        const base = rgb(color), bad = rgb(cssVar("--bad") || "#FF5D6C"), half = Math.PI / CIRCLE_BINS;
        for (let i = 0; i < CIRCLE_BINS; i++) {
          const r = bins[i];
          if (!r) continue;
          const a = i / CIRCLE_BINS * Math.PI * 2;   // 구간 가운데, 화면 좌표(y 아래 +)
          const mix = Math.min(1, Math.abs(r - 1) / 0.15);
          const [cr, cg, cb] = base.map((v, k) => Math.round(v + (bad[k] - v) * mix));
          g.beginPath(); g.moveTo(c, c); g.arc(c, c, r * unit, a - half, a + half); g.closePath();
          g.fillStyle = `rgba(${cr},${cg},${cb},0.43)`; g.fill();
          g.strokeStyle = `rgba(${cr},${cg},${cb},0.8)`; g.lineWidth = 1; g.stroke();
        }
        g.setLineDash([4, 3]); g.strokeStyle = cssVar("--muted"); g.lineWidth = 1;
        g.beginPath(); g.arc(c, c, unit, 0, Math.PI * 2); g.stroke(); g.setLineDash([]);
        const result = this.result(bins);
        if (result && result.complete && result.error != null) {
          g.fillStyle = cssVar("--text"); g.textAlign = "center"; g.textBaseline = "middle";
          g.font = `800 ${Math.round(size * 0.11)}px ${cssVar("--mono")}`;
          g.fillText(`${result.error.toFixed(1)}%`, c, c);
        }
      }
      if (point) {
        const x = Math.max(-1.1, Math.min(1.1, point[0] || 0)), y = Math.max(-1.1, Math.min(1.1, point[1] || 0));
        g.fillStyle = color; g.beginPath(); g.arc(c + x * unit, c + y * unit, 5, 0, Math.PI * 2); g.fill();
      }
    },

    refreshTexts(time) {
      const real = this.readPad && navigator.getGamepads ? this.readPad() : null;
      const name = document.getElementById("pad-name");
      const dot = document.getElementById("pad-dot");
      if (!name) return;
      dot.className = "status-dot" + (real ? " on" : this.demo ? " demo" : "");
      name.textContent = real ? t("try.connected", { name: real.id }) : this.demo ? t("try.demoOn") : t("try.waiting");
      document.getElementById("demo-button").hidden = Boolean(real);
      document.getElementById("demo-button").textContent = this.demo ? t("try.demoStop") : t("try.demo");
      document.getElementById("demo-button").setAttribute("aria-pressed", String(this.demo));
      const circle = this.circle;
      const button = document.getElementById("circ-button");
      button.textContent = circle.running ? t("try.circStop") : t("try.circStart");
      const status = document.getElementById("circ-status");
      if (circle.running) {
        status.textContent = circle.started
          ? t("try.circRunning", { seconds: Math.max(0, CIRCLE_SECONDS - ((time || performance.now()) - circle.started) / 1000).toFixed(1) })
          : t("try.circWaiting");
      } else if (circle.done) {
        const left = this.result(circle.left), right = this.result(circle.right);
        const text = (result) => (result && result.complete
          ? `${result.error.toFixed(1)}% (${t("grade." + result.grade)})`
          : t("try.circIncomplete", { coverage: String(Math.round((result ? result.coverage : 0) * 100)) }));
        status.textContent = t("try.circDone", { left: text(left), right: text(right) });
      } else {
        status.textContent = t("try.circHint");
      }
    },
  };

  // ---- 독립 업데이트 창의 실제 단계별 캡처 ----
  const updateDemo = {
    step: 0, started: 0, visible: false, running: false, auto: true,
    durations: [5000, 5000, 5000, 5000],
    screens: ["notice", "download", "install", "done"],

    setup() {
      this.root = document.getElementById("update-preview");
      this.image = document.getElementById("update-shot");
      if (!this.root) return;
      this.auto = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      document.querySelectorAll("#update-steps [data-step]").forEach((button) => {
        button.addEventListener("click", () => { this.auto = false; this.go(Number(button.dataset.step)); });
      });
      new IntersectionObserver((entries) => {
        this.visible = entries.some((entry) => entry.isIntersecting);
        if (this.visible) this.loop();
      }, { threshold: 0.15 }).observe(this.root);
      const asked = Number.parseInt(new URLSearchParams(location.search).get("update-step") || "1", 10);
      this.go(Math.min(4, Math.max(1, Number.isFinite(asked) ? asked : 1)) - 1);
    },

    go(step) {
      this.step = step;
      this.started = performance.now();
      this.refreshTexts();
    },

    loop() {
      if (this.running || !this.root || !this.auto) return;
      this.running = true;
      const tick = (time) => {
        if (!this.visible || !this.auto) { this.running = false; return; }
        if (time - this.started >= this.durations[this.step]) this.go((this.step + 1) % 4);
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    },

    refreshTexts() {
      if (!this.root) return;
      this.image.src = shot(`update-${this.screens[this.step]}`);
      this.image.alt = `${t("update.title")} · ${t(`update.step${this.step + 1}`)}`;
      document.querySelectorAll("#update-steps [data-step]").forEach((button) => {
        button.setAttribute("aria-current", Number(button.dataset.step) === this.step ? "step" : "false");
      });
    },
  };

  // 상단 '내려받기': 맨 아래 '최신 버전 내려받기'로 내려가서 그 단추를 잠깐 강조한다.
  function setupDownloadLink() {
    document.getElementById("nav-download").addEventListener("click", () => {
      const button = document.getElementById("dl-link");
      button.classList.remove("flash");
      setTimeout(() => { button.classList.add("flash"); button.focus({ preventScroll: true }); }, 450);
      setTimeout(() => button.classList.remove("flash"), 3400);
    });
  }

  // ---- 시작 ----
  function setupHeader() {
    const bar = document.getElementById("topbar");
    const update = () => bar.classList.toggle("scrolled", window.scrollY > 8);
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  document.addEventListener("DOMContentLoaded", () => {
    collectDefaults();
    setupHeader();
    setupTheme();
    setupLanguageMenu();
    setupCopy();
    gallery.setup();
    tester.setup();
    updateDemo.setup();
    setupDownloadLink();
    applyLanguage(detectLanguage(), false);
    fetchRelease();
  });
})();
