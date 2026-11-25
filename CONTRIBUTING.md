# Contributing to Jarvis OS

Thank you for helping build **Jarvis OS**!

## Engineering Principles
1. **The Wi-Fi-Off Law**: All assets inside `jarvis-hud/viewer/` must remain 100% vendored offline with zero external CDN imports. Verify with `python preflight/wifi_off_drill.py`.
2. **Debian Bookworm Compatibility**: Only add verified Debian 12 packages into `iso-builder/config/package-lists/*.list.chroot`, or place optional packages in resilient fallback hooks.
3. **Dual-Environment Harmony**: Desktop theme changes in `jarvis-core/tools/theme_manager.py` should stay synchronized with `jarvis-hud/viewer/js/themes.js` and `iso-builder/config/includes.chroot/usr/share/color-schemes/`.
4. **Preflight Verification**: Run `python preflight/preflight.py` (requires `12/12 PASS`) and `python showcase.py` before opening a pull request.

## Pull Request Workflow
1. Fork `https://github.com/10JERRY01/Jarvis-os` and create a feature branch (`feat/...` or `fix/...`).
2. Keep `.gitignore` intact (never commit `.gguf`, `.iso`, or `.db` binaries).
3. Submit a clear pull request describing your changes and test output.
