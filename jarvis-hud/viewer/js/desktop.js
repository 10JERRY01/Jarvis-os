/**
 * Jarvis OS Window Manager & Dual-Environment Orchestrator
 * Seamlessly switches between Jarvis Ambient Core (3D HUD) and the
 * Apple macOS / Multi-Theme Linux Desktop Environment.
 */

window.DesktopOS = {
  windows: {},
  topZ: 100,
  focusedApp: "Finder",

  APP_META: {
    finder:   { title: "Finder",             w: 720, h: 460, x: 110, y: 54 },
    terminal: { title: "Terminal — zsh",     w: 760, h: 470, x: 160, y: 74 },
    software: { title: "Software Center",    w: 840, h: 520, x: 140, y: 46 },
    themes:   { title: "Theme Studio",       w: 780, h: 500, x: 180, y: 66 },
    monitor:  { title: "System Monitor",     w: 680, h: 400, x: 220, y: 94 },
    browser:  { title: "Web & Distro Guide", w: 680, h: 410, x: 150, y: 84 },
  },

  init() {
    this.updateClock();
    setInterval(() => this.updateClock(), 15000);
    window.JarvisThemes.load();
    this.bindGlobalEvents();
    this.syncStatus();
  },

  async syncStatus() {
    try {
      const res = await fetch("/mode/status");
      const data = await res.json();
      const mode = data.mode || "jarvis";
      const theme = data.desktop_theme || "cupertino-dark";

      window.JarvisThemes.applyVisuals(theme, false);
      if (mode === "zen" || mode === "desktop") {
        this.applyEnvironmentUI("desktop");
        if (Object.keys(this.windows).length === 0) {
          this.openApp("terminal");
        }
      } else {
        this.applyEnvironmentUI("jarvis");
      }
    } catch (e) {
      this.applyEnvironmentUI("jarvis");
    }
  },

  async switchEnvironment(targetMode) {
    const modePayload = targetMode === "desktop" ? "zen" : targetMode;
    try {
      const res = await fetch("/mode/switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: modePayload }),
      });
      const data = await res.json();
      const uiTarget = (data.mode === "zen" || targetMode === "desktop") ? "desktop" : "jarvis";
      this.applyEnvironmentUI(uiTarget);
      if (uiTarget === "desktop" && Object.keys(this.windows).length === 0) {
        this.openApp("terminal");
      }
    } catch (e) {
      this.applyEnvironmentUI(targetMode);
    }
  },

  applyEnvironmentUI(env) {
    const body = document.body;
    if (env === "desktop") {
      body.classList.remove("env-ambient");
      body.classList.add("env-desktop");
      const vramEl = document.getElementById("de-vram-pill");
      if (vramEl) vramEl.textContent = "VRAM Freed";
    } else {
      body.classList.remove("env-desktop");
      body.classList.add("env-ambient");
      if (typeof applyZenModeUI === "function") {
        applyZenModeUI(false);
      }
    }
  },

  openApp(appId) {
    // Ensure we are in Desktop view if launching an app
    if (!document.body.classList.contains("env-desktop")) {
      this.switchEnvironment("desktop");
    }

    if (this.windows[appId]) {
      const win = this.windows[appId];
      win.classList.remove("minimized");
      this.focusWindow(appId);
      return;
    }

    const meta = this.APP_META[appId] || { title: appId, w: 700, h: 440, x: 140, y: 70 };
    const stage = document.getElementById("desktop-stage");

    const win = document.createElement("div");
    win.className = "de-window";
    win.style.width = `${meta.w}px`;
    win.style.height = `${meta.h}px`;
    win.style.left = `${meta.x}px`;
    win.style.top = `${meta.y}px`;
    win.style.zIndex = ++this.topZ;
    win.innerHTML = `
      <div class="de-titlebar">
        <div class="traffic-lights">
          <button class="tl-btn tl-close" title="Close">✕</button>
          <button class="tl-btn tl-min" title="Minimize">−</button>
          <button class="tl-btn tl-max" title="Zoom">+</button>
        </div>
        <div class="de-title">${meta.title}</div>
        <div class="de-titlebar-spacer"></div>
      </div>
      <div class="de-body"></div>
      <div class="resize-handle"></div>
    `;

    stage.appendChild(win);
    this.windows[appId] = win;
    this.updateDockDot(appId, true);
    this.focusWindow(appId);

    // Wire traffic lights
    win.querySelector(".tl-close").addEventListener("click", (e) => {
      e.stopPropagation();
      win.remove();
      delete this.windows[appId];
      this.updateDockDot(appId, false);
    });
    win.querySelector(".tl-min").addEventListener("click", (e) => {
      e.stopPropagation();
      win.classList.add("minimized");
    });
    win.querySelector(".tl-max").addEventListener("click", (e) => {
      e.stopPropagation();
      win.classList.toggle("maximized");
    });

    win.addEventListener("mousedown", () => this.focusWindow(appId));
    this.makeDraggable(win, win.querySelector(".de-titlebar"));
    this.makeResizable(win, win.querySelector(".resize-handle"));

    window.DesktopApps.render(appId, win.querySelector(".de-body"));
  },

  focusWindow(appId) {
    const win = this.windows[appId];
    if (!win) return;
    win.style.zIndex = ++this.topZ;
    const meta = this.APP_META[appId];
    const activeAppEl = document.getElementById("menubar-active-app");
    if (activeAppEl && meta) {
      activeAppEl.textContent = meta.title.split("—")[0].trim();
    }
  },

  updateDockDot(appId, running) {
    const dockIcon = document.querySelector(`.dock-item[data-app="${appId}"]`);
    if (dockIcon) {
      dockIcon.classList.toggle("running", running);
    }
  },

  makeDraggable(win, handle) {
    let dragging = false, startX = 0, startY = 0, origX = 0, origY = 0;
    handle.addEventListener("mousedown", (e) => {
      if (e.target.closest(".tl-btn") || win.classList.contains("maximized")) return;
      dragging = true;
      startX = e.clientX;
      startY = e.clientY;
      origX = parseInt(win.style.left, 10) || 0;
      origY = parseInt(win.style.top, 10) || 0;
    });
    window.addEventListener("mousemove", (e) => {
      if (!dragging) return;
      win.style.left = `${origX + (e.clientX - startX)}px`;
      win.style.top = `${Math.max(0, origY + (e.clientY - startY))}px`;
    });
    window.addEventListener("mouseup", () => { dragging = false; });
  },

  makeResizable(win, handle) {
    let resizing = false, startX = 0, startY = 0, startW = 0, startH = 0;
    handle.addEventListener("mousedown", (e) => {
      e.stopPropagation();
      resizing = true;
      startX = e.clientX;
      startY = e.clientY;
      startW = win.offsetWidth;
      startH = win.offsetHeight;
    });
    window.addEventListener("mousemove", (e) => {
      if (!resizing) return;
      win.style.width = `${Math.max(380, startW + (e.clientX - startX))}px`;
      win.style.height = `${Math.max(260, startH + (e.clientY - startY))}px`;
    });
    window.addEventListener("mouseup", () => { resizing = false; });
  },

  refreshThemeCards() {
    const win = this.windows["themes"];
    if (win) {
      window.DesktopApps.renderThemes(win.querySelector(".de-body"));
    }
  },

  updateClock() {
    const el = document.getElementById("menubar-clock");
    if (!el) return;
    const now = new Date();
    const opts = { weekday: "short", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" };
    el.textContent = now.toLocaleDateString("en-US", opts);
  },

  bindGlobalEvents() {
    // Dock & Shortcut Tiles & Menu Items
    document.querySelectorAll("[data-app]").forEach((el) => {
      el.addEventListener("click", () => {
        if (applePanel) applePanel.classList.remove("open");
        if (ccPanel) ccPanel.classList.remove("open");
        const app = el.getAttribute("data-app");
        if (app === "jarvis-core") {
          this.switchEnvironment("jarvis");
        } else {
          this.openApp(app);
        }
      });
    });

    // Control Center & Apple Dropdown
    const ccBtn = document.getElementById("menubar-cc-btn");
    const ccPanel = document.getElementById("control-center");
    const appleBtn = document.getElementById("menubar-apple-btn");
    const applePanel = document.getElementById("apple-dropdown");

    if (ccBtn && ccPanel) {
      ccBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        applePanel.classList.remove("open");
        ccPanel.classList.toggle("open");
      });
    }
    if (appleBtn && applePanel) {
      appleBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        ccPanel.classList.remove("open");
        applePanel.classList.toggle("open");
      });
    }

    document.addEventListener("click", (e) => {
      if (ccPanel && !ccPanel.contains(e.target)) ccPanel.classList.remove("open");
      if (applePanel && !applePanel.contains(e.target)) applePanel.classList.remove("open");
      const spot = document.getElementById("spotlight-modal");
      if (spot && spot.classList.contains("open") && !spot.contains(e.target) && !e.target.closest("#menubar-spotlight-btn")) {
        spot.classList.remove("open");
      }
    });

    // Quick theme buttons inside Control Center
    document.querySelectorAll("[data-quick-theme]").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (ccPanel) ccPanel.classList.remove("open");
        window.JarvisThemes.selectTheme(btn.getAttribute("data-quick-theme"));
      });
    });

    // Spotlight Toggle
    const spotBtn = document.getElementById("menubar-spotlight-btn");
    const spotModal = document.getElementById("spotlight-modal");
    const spotInput = document.getElementById("spotlight-input");
    const spotRes = document.getElementById("spotlight-results");

    const openSpotlight = () => {
      spotModal.classList.add("open");
      spotInput.value = "";
      renderSpotlight("");
      setTimeout(() => spotInput.focus(), 30);
    };

    const renderSpotlight = (q) => {
      const items = [
        { label: "Terminal — Install Debian Software (nala / apt)", action: () => this.openApp("terminal") },
        { label: "Software Center — App Store", action: () => this.openApp("software") },
        { label: "Finder — Browse Distro Files", action: () => this.openApp("finder") },
        { label: "Theme Studio — Apple Cupertino / Nordic / Pop", action: () => this.openApp("themes") },
        { label: "Switch to Jarvis Ambient Core (3D AI HUD)", action: () => this.switchEnvironment("jarvis") },
        { label: "Apply Apple Cupertino Dark Theme", action: () => window.JarvisThemes.selectTheme("cupertino-dark") },
        { label: "Apply Apple Cupertino Light Theme", action: () => window.JarvisThemes.selectTheme("cupertino-light") },
        { label: "Apply Minimalist Pop!_OS / Ubuntu Theme", action: () => window.JarvisThemes.selectTheme("zen") },
      ].filter((it) => !q || it.label.toLowerCase().includes(q.toLowerCase()));

      spotRes.innerHTML = items.map((it, idx) => `
        <button class="sidebar-btn" data-spot-idx="${idx}">${it.label}</button>
      `).join("");
      spotRes.querySelectorAll("[data-spot-idx]").forEach((b) => {
        b.addEventListener("click", () => {
          items[parseInt(b.getAttribute("data-spot-idx"), 10)].action();
          spotModal.classList.remove("open");
        });
      });
    };

    if (spotBtn) spotBtn.addEventListener("click", openSpotlight);
    if (spotInput) spotInput.addEventListener("input", () => renderSpotlight(spotInput.value));

    // Global Keyboard Shortcut: Ctrl/Cmd + K for Spotlight, Meta+Shift+M for Mode Switch
    window.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (document.body.classList.contains("env-desktop")) openSpotlight();
      } else if (e.key === "Escape" && spotModal) {
        spotModal.classList.remove("open");
      }
    });
  },
};

window.addEventListener("DOMContentLoaded", () => {
  window.DesktopOS.init();
});
