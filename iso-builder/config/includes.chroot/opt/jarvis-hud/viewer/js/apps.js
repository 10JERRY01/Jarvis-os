/**
 * Jarvis OS Desktop Environment Built-in Applications (100% Offline)
 * - Terminal (Real backend command runner + nala/apt/jarvis-pkg + ?? AI translation)
 * - Software Store (Curated Debian & Flatpak catalog + one-click install)
 * - Finder (Live project/chroot file inspector)
 * - Appearance & Theme Studio (Apple Cupertino Dark/Light, Pop Zen, Nordic, Cyber)
 * - System Monitor (Live CPU/RAM/GPU/VRAM status)
 * - Browser / Distro Guide (Local docs preview)
 */

window.DesktopApps = {
  terminalHistory: [],
  terminalHistIdx: -1,
  termCwd: "~",

  render(appId, container) {
    if (appId === "terminal") return this.renderTerminal(container);
    if (appId === "software") return this.renderSoftwareStore(container);
    if (appId === "finder") return this.renderFinder(container, "");
    if (appId === "themes") return this.renderThemes(container);
    if (appId === "monitor") return this.renderMonitor(container);
    if (appId === "browser") return this.renderBrowser(container);
  },

  /* ==================== 1. TERMINAL APP ==================== */
  renderTerminal(container) {
    container.innerHTML = `
      <div class="term-wrap">
        <div class="term-toolbar">
          <button class="term-chip" data-cmd="fastfetch">fastfetch</button>
          <button class="term-chip" data-cmd="jarvis-pkg list">jarvis-pkg list</button>
          <button class="term-chip" data-cmd="nala install obs-studio">nala install obs-studio</button>
          <button class="term-chip" data-cmd="jarvis theme list">jarvis theme list</button>
          <button class="term-chip" data-cmd="?? check largest files in project">?? AI shell</button>
          <button class="term-chip" data-cmd="help">help</button>
        </div>
        <div class="term-output" id="term-out">Welcome to Jarvis OS Terminal (Debian 12 Bookworm / Liquorix Kernel).
Type 'help' for package manager, theme switcher, and AI shell commands.
</div>
        <div class="term-prompt-line">
          <span class="term-ps1" id="term-ps1">jarvis@jarvis-os:~$</span>
          <input class="term-input" id="term-in" type="text" placeholder="Enter bash, nala install <pkg>, jarvis theme <name>, or ?? <prompt>..." autocomplete="off" />
        </div>
      </div>
    `;

    const outEl = container.querySelector("#term-out");
    const inEl = container.querySelector("#term-in");
    const ps1El = container.querySelector("#term-ps1");

    const runCommand = async (cmd) => {
      const trimmed = cmd.trim();
      if (!trimmed) return;
      this.terminalHistory.unshift(trimmed);
      this.terminalHistIdx = -1;

      if (trimmed === "clear") {
        outEl.textContent = "";
        return;
      }

      outEl.textContent += `\n${ps1El.textContent} ${trimmed}\n`;
      outEl.scrollTop = outEl.scrollHeight;

      try {
        const res = await fetch("/terminal/exec", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ command: trimmed }),
        });
        const data = await res.json();
        if (data.output) {
          outEl.textContent += `${data.output}\n`;
        }
        if (data.cwd) {
          const shortCwd = data.cwd.split(/[\\/]/).pop() || "~";
          ps1El.textContent = `jarvis@jarvis-os:${shortCwd}$`;
        }
        if (data.refresh_ui) {
          window.JarvisThemes.load();
          if (window.DesktopOS) window.DesktopOS.syncStatus();
        }
      } catch (err) {
        outEl.textContent += `[Error] ${err.message}\n`;
      }
      outEl.scrollTop = outEl.scrollHeight;
    };

    container.querySelectorAll(".term-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        const cmd = btn.getAttribute("data-cmd");
        inEl.value = "";
        runCommand(cmd);
        inEl.focus();
      });
    });

    inEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const val = inEl.value;
        inEl.value = "";
        runCommand(val);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (this.terminalHistIdx + 1 < this.terminalHistory.length) {
          this.terminalHistIdx++;
          inEl.value = this.terminalHistory[this.terminalHistIdx];
        }
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        if (this.terminalHistIdx > 0) {
          this.terminalHistIdx--;
          inEl.value = this.terminalHistory[this.terminalHistIdx];
        } else {
          this.terminalHistIdx = -1;
          inEl.value = "";
        }
      }
    });

    setTimeout(() => inEl.focus(), 50);
  },

  /* ==================== 2. SOFTWARE STORE ==================== */
  async renderSoftwareStore(container) {
    container.innerHTML = `
      <div class="app-split">
        <div class="app-sidebar">
          <div class="sidebar-section">Discover Software</div>
          <button class="sidebar-btn active" data-cat="All">All Packages</button>
          <button class="sidebar-btn" data-cat="Browsers">Web Browsers</button>
          <button class="sidebar-btn" data-cat="Gaming">Gaming & Proton</button>
          <button class="sidebar-btn" data-cat="Developer">Developer & AI</button>
          <button class="sidebar-btn" data-cat="Creative">Creative & Media</button>
          <button class="sidebar-btn" data-cat="Power Tools">Power CLI Tools</button>
          <button class="sidebar-btn" data-cat="System">System & Utilities</button>
        </div>
        <div class="app-main">
          <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
            <input class="search-input" id="pkg-search" type="text" placeholder="Search Debian APT & Flatpak software (e.g., blender, steam, nala)..." />
            <span id="pkg-host-badge" class="badge-tag" style="white-space:nowrap;">Loading...</span>
          </div>
          <div id="pkg-log" style="display:none; font-family:var(--de-mono); font-size:11.5px; padding:10px; border-radius:8px; background:rgba(0,0,0,0.45); white-space:pre-wrap;"></div>
          <div class="card-grid" id="pkg-grid"></div>
        </div>
      </div>
    `;

    let allPackages = [];
    let selectedCategory = "All";

    const gridEl = container.querySelector("#pkg-grid");
    const searchEl = container.querySelector("#pkg-search");
    const logEl = container.querySelector("#pkg-log");
    const badgeEl = container.querySelector("#pkg-host-badge");

    const drawGrid = () => {
      const q = searchEl.value.trim().toLowerCase();
      const filtered = allPackages.filter((p) => {
        const catOk = selectedCategory === "All" || p.category === selectedCategory;
        const qOk = !q || p.id.toLowerCase().includes(q) || p.name.toLowerCase().includes(q) || p.desc.toLowerCase().includes(q);
        return catOk && qOk;
      });

      gridEl.innerHTML = filtered.map((pkg) => {
        const isInstalled = !!pkg.installed;
        const statusText = isInstalled ? (pkg.status === "installed" ? "Installed" : "Included in ISO") : "Available";
        return `
          <div class="de-card">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <h4>${pkg.name}</h4>
                <span style="font-size:10px; padding:2px 7px; border-radius:99px; background:${isInstalled ? "rgba(48,209,88,0.18)" : "var(--de-accent-soft)"}; color:${isInstalled ? "#30d158" : "var(--de-accent)"};">${statusText}</span>
              </div>
              <p>${pkg.desc}</p>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:10.5px; color:var(--de-muted); font-family:var(--de-mono);">${pkg.source}: ${pkg.id}</span>
              ${
                isInstalled
                  ? `<button class="de-btn secondary pkg-act" data-act="remove" data-pkg="${pkg.id}">Remove</button>`
                  : `<button class="de-btn pkg-act" data-act="install" data-pkg="${pkg.id}">Install</button>`
              }
            </div>
          </div>
        `;
      }).join("");

      gridEl.querySelectorAll(".pkg-act").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const pkgId = btn.getAttribute("data-pkg");
          const act = btn.getAttribute("data-act");
          btn.disabled = true;
          btn.textContent = act === "install" ? "Installing..." : "Removing...";
          try {
            const res = await fetch(`/packages/${act}`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ package: pkgId }),
            });
            const data = await res.json();
            logEl.style.display = "block";
            logEl.textContent = data.output || "Completed.";
            await loadCatalog();
          } catch (e) {
            logEl.style.display = "block";
            logEl.textContent = "Error: " + e.message;
          }
        });
      });
    };

    const loadCatalog = async () => {
      const res = await fetch("/packages/catalog");
      const data = await res.json();
      allPackages = data.packages || [];
      badgeEl.textContent = `${data.staged_total || 0} Staged (${data.host_os})`;
      drawGrid();
    };

    container.querySelectorAll(".sidebar-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        container.querySelectorAll(".sidebar-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        selectedCategory = btn.getAttribute("data-cat");
        drawGrid();
      });
    });

    searchEl.addEventListener("input", drawGrid);
    loadCatalog();
  },

  /* ==================== 3. FINDER (FILE BROWSER) ==================== */
  async renderFinder(container, startPath = "") {
    container.innerHTML = `
      <div class="app-split">
        <div class="app-sidebar">
          <div class="sidebar-section">Places</div>
          <button class="sidebar-btn" data-path="">Jarvis OS Root</button>
          <button class="sidebar-btn" data-path="jarvis-core">Jarvis Core</button>
          <button class="sidebar-btn" data-path="iso-builder/config/package-lists">Package Lists</button>
          <button class="sidebar-btn" data-path="iso-builder/config/includes.chroot">ISO Rootfs Overlay</button>
          <button class="sidebar-btn" data-path="notes/captures">Memory Captures</button>
        </div>
        <div class="app-main" id="finder-main">
          <div style="font-size:12px; color:var(--de-muted);" id="finder-crumb">Loading...</div>
          <div id="finder-list"></div>
          <pre id="finder-preview" style="display:none; background:rgba(0,0,0,0.45); padding:12px; border-radius:10px; font-family:var(--de-mono); font-size:11.5px; overflow:auto; max-height:240px;"></pre>
        </div>
      </div>
    `;

    const crumbEl = container.querySelector("#finder-crumb");
    const listEl = container.querySelector("#finder-list");
    const prevEl = container.querySelector("#finder-preview");

    const openDir = async (relPath) => {
      prevEl.style.display = "none";
      crumbEl.textContent = `Path: /${relPath || ""}`;
      const res = await fetch(`/fs/list?path=${encodeURIComponent(relPath)}`);
      const data = await res.json();
      const items = data.items || [];

      let html = "";
      if (relPath) {
        const parent = relPath.split("/").slice(0, -1).join("/");
        html += `<div class="finder-row" data-up="${parent}"><span>📁 .. (Up)</span><span style="color:var(--de-muted);">Directory</span></div>`;
      }
      html += items.map((it) => `
        <div class="finder-row" data-item="${it.path}" data-dir="${it.is_dir}">
          <span>${it.is_dir ? "📁" : "📄"} ${it.name}</span>
          <span style="color:var(--de-muted);">${it.is_dir ? "Folder" : `${it.size} B`}</span>
        </div>
      `).join("");

      listEl.innerHTML = html;
      listEl.querySelectorAll(".finder-row").forEach((row) => {
        row.addEventListener("click", async () => {
          const up = row.getAttribute("data-up");
          if (up !== null) return openDir(up);
          const itemPath = row.getAttribute("data-item");
          const isDir = row.getAttribute("data-dir") === "true";
          if (isDir) {
            openDir(itemPath);
          } else {
            const fres = await fetch(`/fs/read?path=${encodeURIComponent(itemPath)}`);
            const fdata = await fres.json();
            prevEl.style.display = "block";
            prevEl.textContent = fdata.content || fdata.error || "";
          }
        });
      });
    };

    container.querySelectorAll(".sidebar-btn").forEach((btn) => {
      btn.addEventListener("click", () => openDir(btn.getAttribute("data-path")));
    });

    openDir(startPath);
  },

  /* ==================== 4. APPEARANCE & THEME STUDIO ==================== */
  async renderThemes(container) {
    await window.JarvisThemes.load();
    const themes = window.JarvisThemes.themes;
    const active = window.JarvisThemes.activeTheme;

    container.innerHTML = `
      <div class="app-main" style="padding:18px 22px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h3 style="font-size:16px;">Appearance & Theme Studio</h3>
            <p style="font-size:12px; color:var(--de-muted); margin-top:3px;">
              Switch seamlessly between Apple macOS Cupertino Glass, Minimalist Pop/Ubuntu Zen, Nordic Frost, and Jarvis Cyber.
            </p>
          </div>
          <button class="de-btn secondary" id="studio-to-jarvis">Enter Jarvis 3D Core</button>
        </div>
        <div class="card-grid" id="theme-studio-grid">
          ${themes.map((t) => `
            <div class="de-card">
              <div class="theme-swatch" style="background:${t.preview_gradient};">
                <div style="position:absolute; top:8px; ${t.button_layout === "left" ? "left:10px;" : "right:10px;"} display:flex; gap:4px;">
                  <span style="width:8px;height:8px;border-radius:50%;background:#ff5f56;"></span>
                  <span style="width:8px;height:8px;border-radius:50%;background:#ffbd2e;"></span>
                  <span style="width:8px;height:8px;border-radius:50%;background:#27c93f;"></span>
                </div>
              </div>
              <div>
                <h4>${t.name}</h4>
                <p style="margin-top:4px;">${t.subtitle}</p>
              </div>
              <button class="de-btn ${t.id === active ? "secondary" : ""} apply-theme-btn" data-tid="${t.id}">
                ${t.id === active ? "Active Theme" : "Apply Theme"}
              </button>
            </div>
          `).join("")}
        </div>
      </div>
    `;

    container.querySelector("#studio-to-jarvis").addEventListener("click", () => {
      window.DesktopOS.switchEnvironment("jarvis");
    });

    container.querySelectorAll(".apply-theme-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        await window.JarvisThemes.selectTheme(btn.getAttribute("data-tid"));
        this.renderThemes(container);
      });
    });
  },

  /* ==================== 5. SYSTEM MONITOR ==================== */
  async renderMonitor(container) {
    container.innerHTML = `<div class="app-main"><p>Polling hardware telemetry...</p></div>`;
    try {
      const [mRes, sRes] = await Promise.all([fetch("/metrics"), fetch("/status")]);
      const m = await mRes.json();
      const s = await sRes.json();
      container.innerHTML = `
        <div class="app-main">
          <h3 style="font-size:16px;">Jarvis OS System Telemetry</h3>
          <div class="card-grid">
            <div class="de-card">
              <h4>Operating System & Kernel</h4>
              <p>Host: ${m.host_os}</p>
              <p>Target Distro: Debian 12 Bookworm (Liquorix 1000Hz)</p>
              <p>Air-Gapped: ${s.local_only ? "100% Offline Compliant" : "Network"}</p>
            </div>
            <div class="de-card">
              <h4>Local AI & GPU Memory</h4>
              <p>Engine: Bonsai 27B (${s.active_brain})</p>
              <p>GPU VRAM Allocated: ${m.vram_freed ? "0 MB (Freed in Desktop Mode)" : "Active (~3.5 GB)"}</p>
              <p>Telemetry: ${m.summary || "Operational"}</p>
            </div>
            <div class="de-card">
              <h4>Desktop Environment State</h4>
              <p>Mode: ${String(m.mode || "zen").toUpperCase()}</p>
              <p>Active Theme: ${m.desktop_theme}</p>
              <p>Icon Pack: Papirus-Dark /SF Vector</p>
            </div>
          </div>
        </div>
      `;
    } catch (e) {
      container.innerHTML = `<div class="app-main"><p>Error loading telemetry: ${e.message}</p></div>`;
    }
  },

  /* ==================== 6. BROWSER / SYSTEM OVERVIEW ==================== */
  renderBrowser(container) {
    container.innerHTML = `
      <div class="app-main">
        <div style="display:flex; align-items:center; gap:8px; padding:8px 12px; border-radius:10px; background:var(--de-card-bg); border:1px solid var(--de-border);">
          <span style="font-size:12px; color:var(--de-green);">🔒</span>
          <span style="font-family:var(--de-mono); font-size:12px; color:var(--de-muted);">jarvis://distro-overview (100% Air-Gapped Local Workspace)</span>
        </div>
        <div class="de-card">
          <h4>Jarvis OS · Debian 12 + Apple & Multi-Theme Workstation</h4>
          <p>
            On live Debian Linux, the native web browsers (<strong>Firefox ESR</strong> & <strong>Chromium</strong>) launch directly from the Dock.
            You can toggle freely between this multi-window Desktop Environment and the 3D <strong>Jarvis Ambient Core</strong> at any time using the top menu bar, Dock, or <code>Meta + Shift + M</code>.
          </p>
          <div style="display:flex; gap:10px; margin-top:8px;">
            <button class="de-btn" id="br-open-term">Open Terminal to Install Software</button>
            <button class="de-btn secondary" id="br-open-store">Open App Store</button>
          </div>
        </div>
      </div>
    `;
    container.querySelector("#br-open-term").addEventListener("click", () => window.DesktopOS.openApp("terminal"));
    container.querySelector("#br-open-store").addEventListener("click", () => window.DesktopOS.openApp("software"));
  },
};
