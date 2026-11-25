/**
 * ==============================================================================
 * Jarvis OS Website Configuration (Single-File Customization)
 * Update your Internet Archive / Cloudflare R2 ISO URL and Ad IDs anytime here.
 * ==============================================================================
 */
window.JARVIS_SITE_CONFIG = {
  version: "v1.0.0",
  codename: "Genesis · Debian 12 Bookworm",
  isoFilename: "jarvis-os-debootstrap-amd64.hybrid.iso",
  isoSizeLabel: "~2.4 GB (x86_64 · BIOS + UEFI Hybrid)",

  // 1. Repository & Download Mirrors (Internet Archive / Cloudflare R2 / GitHub Releases)
  githubRepoUrl: "https://github.com/10JERRY01/Jarvis-os",
  githubReleasesUrl: "https://github.com/10JERRY01/Jarvis-os/releases/latest",
  // Paste your Internet Archive direct .iso link once uploaded, e.g.:
  // "https://archive.org/download/jarvis-os-v1.0/jarvis-os-debootstrap-amd64.hybrid.iso"
  internetArchiveIsoUrl: "",
  // Optional Cloudflare R2 direct link:
  cloudflareR2IsoUrl: "",
  sha256Url: "https://github.com/10JERRY01/Jarvis-os/releases/latest",

  // 2. Privacy-First Developer Ad Network (EthicalAds or Carbon Ads)
  ads: {
    provider: "ethicalads",
    // EthicalAds publisher ID (get at ethicalads.io/publishers/): e.g. "jarvis-os"
    ethicalAdsPublisherId: "",
    // Optional Carbon Ads keys (if switching provider to "carbon"):
    carbonServe: "",
    carbonPlacement: "",
  },

  // 3. Creator Support Links (Rendered at the end of the website)
  support: {
    buyMeACoffeeUrl: "https://buymeacoffee.com/jerrymice45",
    buyMeACoffeeHandle: "jerrymice45",
    patreonUrl: "https://www.patreon.com/c/Jerry42",
    patreonHandle: "Jerry42",
  },
};
