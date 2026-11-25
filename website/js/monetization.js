/**
 * Jarvis OS Website Orchestrator:
 * - Binds Cloudflare R2 / GitHub Releases ISO links dynamically from config.js
 * - Handles Privacy/Consent + EthicalAds / Carbon Ads contextual loading
 * - Binds Buy Me a Coffee & Patreon support CTAs
 * - Controls Light/Dark UI toggle and Dual-Persona Interactive Mockup
 */
(function () {
  const cfg = window.JARVIS_SITE_CONFIG || {};

  // 1. Theme Toggle (Dark <-> Apple Pearl Light)
  const themeBtn = document.getElementById("site-theme-toggle");
  const savedTheme = localStorage.getItem("jarvis_site_theme") || "dark";
  if (savedTheme === "light") document.documentElement.setAttribute("data-site-theme", "light");

  if (themeBtn) {
    themeBtn.textContent = savedTheme === "light" ? "☾" : "☀";
    themeBtn.addEventListener("click", () => {
      const isLight = document.documentElement.getAttribute("data-site-theme") === "light";
      const next = isLight ? "dark" : "light";
      if (next === "light") {
        document.documentElement.setAttribute("data-site-theme", "light");
      } else {
        document.documentElement.removeAttribute("data-site-theme");
      }
      localStorage.setItem("jarvis_site_theme", next);
      themeBtn.textContent = next === "light" ? "☾" : "☀";
    });
  }

  // 2. Interactive Dual-Persona Preview Tabs
  const tabBtns = document.querySelectorAll("[data-preview-mode]");
  const mockScreen = document.getElementById("mock-screen");
  const mockContent = document.getElementById("mock-content");

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
              > "Jarvis, check VRAM & index kernel notes"<br/>
              <span style="color:#30d158;">[Jarvis]:</span> "3,540 MB allocated on GPU, sir.<br/>
              Knowledge Galaxy synced across 102 AST code chunks."<br/><br/>
              <span style="color:#94a3b8;">Mode: Ambient Voice Active | Latency: 1.74s</span>
            </div>
          </div>
          <div class="mock-win">
            <div style="font-size:11px; color:#a855f7; font-weight:700; margin-bottom:8px;">MODE & RESOURCE SWITCHER</div>
            <div class="mock-code">
              Command: <strong>Meta + Shift + M</strong><br/>
              Next State: Apple Cupertino Desktop<br/>
              VRAM Action: keep_alive: 0 (100% Freed)<br/>
              Privacy: Mic stream released
            </div>
          </div>
        </div>
        <div class="mock-dock"><i></i><i></i><i></i><i></i></div>
      `;
    } else {
      mockContent.innerHTML = `
        <div class="mock-topbar">
          <span><strong></strong> &nbsp; Terminal &nbsp; File &nbsp; Edit &nbsp; Software &nbsp; Themes</span>
          <span>Apple Cupertino Dark · <strong>VRAM 0 MB</strong> · Switch to Jarvis Core</span>
        </div>
        <div class="mock-windows">
          <div class="mock-win">
            <div class="mock-dots"><span style="background:#ff5f56"></span><span style="background:#ffbd2e"></span><span style="background:#27c93f"></span></div>
            <div class="mock-code">
              jarvis@jarvis-os:~$ <strong>sudo nala install obs-studio gimp</strong><br/>
              [OK] Installing Debian Bookworm packages...<br/>
              jarvis@jarvis-os:~$ <strong>jarvis theme cupertino-light</strong><br/>
              [SUCCESS] Applied Apple Cupertino Light
            </div>
          </div>
          <div class="mock-win">
            <div class="mock-dots"><span style="background:#ff5f56"></span><span style="background:#ffbd2e"></span><span style="background:#27c93f"></span></div>
            <div style="font-size:12px; font-weight:700; margin-bottom:6px;">Debian Software & Gaming Hub</div>
            <div class="mock-code">
              • Firefox ESR & Chromium (Installed)<br/>
              • Steam + Lutris + GameMode (Ready)<br/>
              • Liquorix 1000Hz Kernel (Active)<br/>
              • Papirus Vector Icons + Global AppMenu
            </div>
          </div>
        </div>
        <div class="mock-dock"><i></i><i></i><i></i><i></i><i></i><i></i></div>
      `;
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

  // 3. Bind Download URLs (Cloudflare R2 Primary + GitHub Releases Fallback)
  const primaryIsoUrl = cfg.cloudflareR2Configured && cfg.cloudflareR2IsoUrl
    ? cfg.cloudflareR2IsoUrl
    : (cfg.githubReleasesUrl || "https://github.com/10JERRY01/Jarvis-os/releases");

  document.querySelectorAll("[data-iso-download]").forEach((el) => {
    el.setAttribute("href", primaryIsoUrl);
  });
  document.querySelectorAll("[data-gh-release]").forEach((el) => {
    el.setAttribute("href", cfg.githubReleasesUrl || "https://github.com/10JERRY01/Jarvis-os/releases");
  });
  document.querySelectorAll("[data-gh-repo]").forEach((el) => {
    el.setAttribute("href", cfg.githubRepoUrl || "https://github.com/10JERRY01/Jarvis-os");
  });
  const shaLink = document.getElementById("sha-link");
  if (shaLink) shaLink.setAttribute("href", cfg.sha256Url || cfg.githubReleasesUrl);

  const mirrorBadge = document.getElementById("mirror-badge-text");
  if (mirrorBadge) {
    mirrorBadge.textContent = cfg.cloudflareR2Configured
      ? "Mirror: Cloudflare R2 Global CDN (Direct .iso)"
      : "Mirror: GitHub Releases (Ready for Cloudflare R2 CDN URL)";
  }

  // 4. Bind Support Buttons at end of site (Buy Me a Coffee + Patreon)
  const bmcBtn = document.getElementById("bmc-btn");
  const patreonBtn = document.getElementById("patreon-btn");
  const supportNotice = document.getElementById("support-config-note");

  if (bmcBtn) {
    if (cfg.support && cfg.support.buyMeACoffeeUrl) {
      bmcBtn.setAttribute("href", cfg.support.buyMeACoffeeUrl);
    } else {
      bmcBtn.setAttribute("href", "#support-configure");
      bmcBtn.addEventListener("click", (e) => {
        e.preventDefault();
        if (supportNotice) {
          supportNotice.textContent = "Buy Me a Coffee URL ready to link: set support.buyMeACoffeeUrl in website/config.js.";
          supportNotice.style.display = "block";
        }
      });
    }
  }

  if (patreonBtn) {
    if (cfg.support && cfg.support.patreonUrl) {
      patreonBtn.setAttribute("href", cfg.support.patreonUrl);
    } else {
      patreonBtn.setAttribute("href", "#support-configure");
      patreonBtn.addEventListener("click", (e) => {
        e.preventDefault();
        if (supportNotice) {
          supportNotice.textContent = "Patreon URL ready to link: set support.patreonUrl in website/config.js.";
          supportNotice.style.display = "block";
        }
      });
    }
  }

  // 5. Privacy Consent + EthicalAds / Carbon Ads Loader
  const adContainer = document.getElementById("ad-slot-container");
  const cookieBanner = document.getElementById("cookie-banner");
  const acceptBtn = document.getElementById("cookie-accept");
  const declineBtn = document.getElementById("cookie-decline");

  const loadDeveloperAds = () => {
    if (!adContainer || !cfg.ads) return;
    const themeMode = document.documentElement.getAttribute("data-site-theme") === "light" ? "light" : "dark";

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

  // Copy checksum snippet helper
  const copyBtn = document.getElementById("copy-verify-btn");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const cmd = "sha256sum -c SHA256SUMS.txt";
      navigator.clipboard?.writeText(cmd);
      copyBtn.textContent = "Copied!";
      setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
    });
  }
})();
