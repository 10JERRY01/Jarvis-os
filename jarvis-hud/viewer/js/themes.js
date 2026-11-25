/**
 * Jarvis OS Theme Registry & Switcher (100% Offline)
 */

window.JarvisThemes = {
  themes: [],
  activeTheme: "cupertino-dark",

  async load() {
    try {
      const res = await fetch("/themes");
      const data = await res.json();
      this.themes = data.themes || [];
      this.applyVisuals(data.active_theme || "cupertino-dark", false);
    } catch (e) {
      this.applyVisuals("cupertino-dark", false);
    }
  },

  async selectTheme(themeId) {
    try {
      const res = await fetch("/themes/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme: themeId }),
      });
      const data = await res.json();
      if (data.success && data.theme) {
        this.applyVisuals(themeId, true);
      }
      return data;
    } catch (e) {
      this.applyVisuals(themeId, true);
      return { success: true, theme: { id: themeId, name: themeId } };
    }
  },

  applyVisuals(themeId, notify) {
    this.activeTheme = themeId;
    const shell = document.getElementById("desktop-shell");
    if (!shell) return;

    shell.setAttribute("data-theme", themeId);
    const meta = this.themes.find((t) => t.id === themeId);
    const layout = meta ? meta.button_layout : (themeId.startsWith("cupertino") ? "left" : "right");
    shell.setAttribute("data-buttons", layout);

    const wpEl = document.getElementById("desktop-wallpaper");
    const slugMap = {
      "cupertino-dark": "jarvis-cupertino-dark",
      "cupertino-light": "jarvis-cupertino-light",
      "zen": "jarvis-zen",
      "nordic": "jarvis-nordic",
      "cyber": "jarvis-cyber",
    };
    const slug = (meta && meta.wallpaper) || slugMap[themeId] || "jarvis-cupertino-dark";
    const grad = (meta && meta.preview_gradient) || "linear-gradient(135deg, #0d162c, #0a84ff)";
    if (wpEl) {
      wpEl.style.backgroundImage = `url('/wallpapers/${slug}.png'), ${grad}`;
    }

    if (notify && window.DesktopOS) {
      window.DesktopOS.refreshThemeCards();
    }
  },
};
