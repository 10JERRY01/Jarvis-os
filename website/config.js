/**
 * ==============================================================================
 * Jarvis OS Website Configuration (Single-File Customization)
 * Update your Cloudflare R2 download URL, Ad Network IDs, and Support Links here.
 * ==============================================================================
 */
window.JARVIS_SITE_CONFIG = {
  version: "v1.0.0",
  codename: "Genesis · Debian 12 Bookworm",
  isoFilename: "jarvis-os-debootstrap-amd64.hybrid.iso",
  isoSizeLabel: "~2.4 GB (x86_64 · BIOS + UEFI Hybrid)",

  // 1. Repository & Download Mirrors (Cloudflare R2 + GitHub Releases Fallback)
  githubRepoUrl: "https://github.com/10JERRY01/Jarvis-os",
  githubReleasesUrl: "https://github.com/10JERRY01/Jarvis-os/releases",
  // Replace with your public Cloudflare R2 custom domain or pub-*.r2.dev URL once uploaded:
  cloudflareR2IsoUrl: "https://github.com/10JERRY01/Jarvis-os/releases/latest",
  cloudflareR2Configured: false, // Set to true once you paste your exact *.r2.dev ISO URL above
  sha256Url: "https://github.com/10JERRY01/Jarvis-os/releases/latest",

  // 2. Developer Ad Network (EthicalAds or Carbon Ads)
  ads: {
    // Choose "ethicalads" (privacy-first contextual dev ads) or "carbon"
    provider: "ethicalads",
    // EthicalAds publisher ID (get at ethicalads.io/publishers/): e.g. "jarvis-os"
    ethicalAdsPublisherId: "",
    // Optional Carbon Ads keys (if switching provider to "carbon"):
    carbonServe: "",
    carbonPlacement: "",
  },

  // 3. Creator Support Links (Rendered at the end of the website)
  support: {
    // Paste your exact Buy Me a Coffee URL when ready (e.g. "https://buymeacoffee.com/10jerry01")
    buyMeACoffeeUrl: "",
    buyMeACoffeeHandle: "10JERRY01",
    // Paste your exact Patreon URL when ready (e.g. "https://patreon.com/10jerry01")
    patreonUrl: "",
    patreonHandle: "JarvisOS",
  },
};
