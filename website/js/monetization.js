/**
 * Jarvis OS Website Orchestrator:
 * - Multi-Theme parity with Jarvis OS (Cupertino Dark/Light, Zen Slate, Nordic, Cyber)
 * - Verified Internet Archive direct ISO, .torrent, SHA256SUMS.txt, and GitHub Releases binding
 * - Interactive Terminal & Dual-Persona Workstation Preview
 * - Privacy Consent + EthicalAds / Carbon Ads contextual loader
 * - Buy Me a Coffee & Patreon footer binding
 */
(function () {
  const cfg = window.JARVIS_SITE_CONFIG || {};

  // 1. Unified Multi-Theme Selector (Synced across index, docs, privacy)
  const themeSelect = document.getElementById("site-theme-select");
  const validThemes = ["cupertino-dark", "cupertino-light", "zen", "nordic", "cyber"];
  const savedTheme = validThemes.includes(localStorage.getItem("jarvis_site_theme"))
    ? localStorage.getItem("jarvis_site_theme")
    : "cupertino-dark";

  const applySiteTheme = (themeId) => {
    document.documentElement.setAttribute("data-site-theme", themeId);
    localStorage.setItem("jarvis_site_theme", themeId);
    if (themeSelect) themeSelect.value = themeId;
  };
  applySiteTheme(savedTheme);

  if (themeSelect) {
    themeSelect.addEventListener("change", () => applySiteTheme(themeSelect.value));
  }

  // 2. Interactive Dual-Persona & Live Terminal Preview
  const tabBtns = document.querySelectorAll("[data-preview-mode]");
  const mockScreen = document.getElementById("mock-screen");
  const mockContent = document.getElementById("mock-content");

  const terminalDemos = {
    nala: "jarvis@jarvis-os:~$ sudo nala install obs-studio gimp\n[Nala] Fetching packages from Debian Bookworm...\n[OK] Installed obs-studio, gimp cleanly.",
    theme: "jarvis@jarvis-os:~$ jarvis theme cupertino-light\n[SUCCESS] Applied Apple Cupertino Light + 4K Mesh Wallpaper.",
    neofetch: "jarvis@jarvis-os:~$ neofetch\nOS: Jarvis OS 1.0 (Debian 12 Bookworm) x86_64\nKernel: 6.11-liquorix-amd64 (1000Hz)\nDE: KDE Plasma Wayland | Theme: Cupertino Dark",
    ai: "jarvis@jarvis-os:~$ ?? find files over 100MB in /var/log\n[Bonsai 27B] find /var/log -type f -size +100M  [SAFE]",
  };

  const renderMockup = (mode) => {
    if (!mockScreen || !mockContent) return;
    mockScreen.className = "mockup-screen " + (mode === "ambient" ? "ambient" : "cupertino");
    if (mode === "ambient") {
      mockContent.innerHTML = `
        <div class="mock-topbar">
          <span><strong>◈ JARVIS CORE</strong> · KNOWLEDGE GALAXY</span>
          <span>BONSAI 27B (64/64 GPU) · 100% AIR-GAPPED</span>
        </div>
        <div class="mock-windows">
          <div class="mock-win">
            <div style="font-size:11px; color:#38bdf8; font-weight:700; margin-bottom:8px;">BONSAI 27B LOCAL INFERENCE</div>
            <div class="mock-code">
              > "Jarvis, check VRAM &amp; index project docs"<br/>
              <span style="color:#30d158;">[Jarvis]:</span> "3,540 MB active on GPU, sir.<br/>
              102 AST code chunks &amp; notes indexed locally."<br/><br/>
              <span style="color:#94a3b8;">100% Offline | Mode: Ambient Voice Active</span>
            </div>
          </div>
          <div class="mock-win">
            <div style="font-size:11px; color:#a855f7; font-weight:700; margin-bottom:8px;">INSTANT DESKTOP SWITCH</div>
            <div class="mock-code">
              Shortcut: <strong>Meta + Shift + M</strong><br/>
              Target: Apple Cupertino / Minimalist Zen<br/>
              Action: keep_alive: 0 (100% VRAM Freed)<br/>
              Audio: PipeWire Mic Stream Released
            </div>
          </div>
        </div>
        <div class="mock-dock"><i></i><i></i><i></i><i></i></div>
      `;
    } else {
      mockContent.innerHTML = `
        <div class="mock-topbar">
          <span><strong></strong> &nbsp; Terminal &nbsp; Finder &nbsp; Software &nbsp; Themes</span>
          <span>Apple Cupertino · <strong>VRAM 0 MB</strong> · Switch to Jarvis Core</span>
        </div>
        <div class="mock-windows">
          <div class="mock-win">
            <div>
              <div class="mock-win-bar">
                <div class="mock-dots"><span style="background:#ff5f56"></span><span style="background:#ffbd2e"></span><span style="background:#27c93f"></span></div>
                <span style="font-size:11px; color:#98989f;">Terminal — zsh</span>
              </div>
              <pre id="demo-term-out" class="mock-code">${terminalDemos.nala}</pre>
            </div>
            <div class="mock-chips">
              <button class="mock-chip" data-demo="nala">nala install</button>
              <button class="mock-chip" data-demo="theme">jarvis theme</button>
              <button class="mock-chip" data-demo="neofetch">neofetch</button>
              <button class="mock-chip" data-demo="ai">?? smart shell</button>
            </div>
          </div>
          <div class="mock-win">
            <div>
              <div class="mock-win-bar">
                <div class="mock-dots"><span style="background:#ff5f56"></span><span style="background:#ffbd2e"></span><span style="background:#27c93f"></span></div>
                <span style="font-size:11px; color:#98989f;">Debian Workstation</span>
              </div>
              <div class="mock-code">
                • <strong>ISO Size:</strong> 1.58 GiB (Zstd Level 19)<br/>
                • <strong>Browsers:</strong> Firefox ESR + Chromium<br/>
                • <strong>Gaming:</strong> Steam, Lutris, GameMode, Wine<br/>
                • <strong>Store:</strong> Discover (APT + Flatpak), Synaptic<br/>
                • <strong>Themes:</strong> Cupertino Light/Dark, Zen, Nordic
              </div>
            </div>
          </div>
        </div>
        <div class="mock-dock"><i></i><i></i><i></i><i></i><i></i><i></i></div>
      `;

      mockContent.querySelectorAll("[data-demo]").forEach((chip) => {
        chip.addEventListener("click", () => {
          const out = document.getElementById("demo-term-out");
          if (out) out.textContent = terminalDemos[chip.getAttribute("data-demo")] || "";
        });
      });
    }
  };

  if (tabBtns.length) {
    renderMockup("cupertino");
    tabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        tabBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        renderMockup(btn.getAttribute("data-preview-mode"));
      });
    });
  }

  // 3. Bind All Verified Download Mirrors
  const primaryIsoUrl = cfg.internetArchiveIsoUrl || cfg.githubReleasesUrl || "https://github.com/10JERRY01/Jarvis-os/releases/tag/v1.0.0";
  document.querySelectorAll("[data-iso-download]").forEach((el) => el.setAttribute("href", primaryIsoUrl));
  document.querySelectorAll("[data-ia-dir]").forEach((el) => el.setAttribute("href", cfg.internetArchiveDirUrl || primaryIsoUrl));
  document.querySelectorAll("[data-ia-torrent]").forEach((el) => el.setAttribute("href", cfg.internetArchiveTorrentUrl || primaryIsoUrl));
  document.querySelectorAll("[data-gh-release]").forEach((el) => el.setAttribute("href", cfg.githubReleasesUrl || "https://github.com/10JERRY01/Jarvis-os/releases/tag/v1.0.0"));
  document.querySelectorAll("[data-gh-repo]").forEach((el) => el.setAttribute("href", cfg.githubRepoUrl || "https://github.com/10JERRY01/Jarvis-os"));

  const shaLink = document.getElementById("sha-link");
  if (shaLink) shaLink.setAttribute("href", cfg.sha256Url || cfg.githubSha256Url);

  const shaTextEl = document.getElementById("sha-hash-text");
  if (shaTextEl && cfg.sha256Hash) shaTextEl.textContent = cfg.sha256Hash;

  const sizeLabelEl = document.getElementById("iso-size-label");
  if (sizeLabelEl && cfg.isoSizeLabel) sizeLabelEl.textContent = cfg.isoSizeLabel;

  // 4. Bind Support Buttons (Buy Me a Coffee + Patreon)
  const bmcBtn = document.getElementById("bmc-btn");
  const patreonBtn = document.getElementById("patreon-btn");
  if (bmcBtn && cfg.support?.buyMeACoffeeUrl) bmcBtn.setAttribute("href", cfg.support.buyMeACoffeeUrl);
  if (patreonBtn && cfg.support?.patreonUrl) patreonBtn.setAttribute("href", cfg.support.patreonUrl);

  // 5. Privacy Consent + EthicalAds / Carbon Ads Loader
  const adContainer = document.getElementById("ad-slot-container");
  const cookieBanner = document.getElementById("cookie-banner");
  const acceptBtn = document.getElementById("cookie-accept");
  const declineBtn = document.getElementById("cookie-decline");

  const loadDeveloperAds = () => {
    if (!adContainer || !cfg.ads) return;
    const isLight = (document.documentElement.getAttribute("data-site-theme") || "").includes("light");
    const themeMode = isLight ? "light" : "dark";

    if (cfg.ads.provider === "ethicalads" && cfg.ads.ethicalAdsPublisherId) {
      adContainer.innerHTML = `<div class="${themeMode}" data-ea-publisher="${cfg.ads.ethicalAdsPublisherId}" data-ea-type="text"></div>`;
      const s = document.createElement("script");
      s.async = true;
      s.src = "https://media.ethicalads.io/media/client/ethicalads.min.js";
      document.body.appendChild(s);
    } else if (cfg.ads.provider === "carbon" && cfg.ads.carbonServe && cfg.ads.carbonPlacement) {
      const s = document.createElement("script");
      s.async = true;
      s.id = "_carbonads_js";
      s.src = `https://cdn.carbonads.com/carbon.js?serve=${encodeURIComponent(cfg.ads.carbonServe)}&placement=${encodeURIComponent(cfg.ads.carbonPlacement)}`;
      adContainer.innerHTML = "";
      adContainer.appendChild(s);
    }
  };

  const consent = localStorage.getItem("jarvis_ad_consent");
  if (!consent && cookieBanner) {
    cookieBanner.classList.add("visible");
  } else if (consent === "accepted") {
    loadDeveloperAds();
  }

  if (acceptBtn) {
    acceptBtn.addEventListener("click", () => {
      localStorage.setItem("jarvis_ad_consent", "accepted");
      cookieBanner.classList.remove("visible");
      loadDeveloperAds();
    });
  }
  if (declineBtn) {
    declineBtn.addEventListener("click", () => {
      localStorage.setItem("jarvis_ad_consent", "declined");
      cookieBanner.classList.remove("visible");
    });
  }

  // Copy SHA-256 checksum helper
  const copyBtn = document.getElementById("copy-verify-btn");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const hashLine = cfg.sha256Hash ? `${cfg.sha256Hash}  ${cfg.isoFilename}` : "sha256sum -c SHA256SUMS.txt";
      navigator.clipboard?.writeText(hashLine);
      copyBtn.textContent = "Copied!";
      setTimeout(() => (copyBtn.textContent = "Copy SHA-256"), 1600);
    });
  }
})();
