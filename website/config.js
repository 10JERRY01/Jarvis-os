/**
 * ==============================================================================
 * Jarvis OS Website Configuration (Single-File Customization)
 * Direct Internet Archive ISO Mirror, Checksums, Theme Sync, Ads & Support Links
 * ==============================================================================
 */
window.JARVIS_SITE_CONFIG = {
  version: "v1.0.0",
  codename: "Genesis · Debian 12 Bookworm",
  isoFilename: "jarvis-os-debootstrap-amd64.hybrid.iso",
  isoSizeLabel: "1.58 GiB (1.70 GB · x86_64 UEFI + BIOS Hybrid)",
  sha256Hash: "c4ae2351dc1abecf1cba1ec078074500fbcb073c0f792e2788b4f6e659d0278a",

  // 1. Repository & Verified Download Mirrors (Internet Archive + GitHub Releases)
  githubRepoUrl: "https://github.com/10JERRY01/Jarvis-os",
  githubReleasesUrl: "https://github.com/10JERRY01/Jarvis-os/releases/tag/v1.0.0",
  internetArchiveIsoUrl: "https://archive.org/download/jarvis-os-debootstrap-amd64.hybrid/jarvis-os-debootstrap-amd64.hybrid.iso",
  internetArchiveDirUrl: "https://archive.org/download/jarvis-os-debootstrap-amd64.hybrid",
  internetArchiveTorrentUrl: "https://archive.org/download/jarvis-os-debootstrap-amd64.hybrid/jarvis-os-debootstrap-amd64.hybrid_archive.torrent",
  sha256Url: "https://archive.org/download/jarvis-os-debootstrap-amd64.hybrid/SHA256SUMS.txt",
  githubSha256Url: "https://github.com/10JERRY01/Jarvis-os/releases/download/v1.0.0/SHA256SUMS.txt",

  // 2. Privacy-First Developer Ad Network (EthicalAds Primary + Optional Carbon Fallback)
  ads: {
    provider: "ethicalads",
    // Paste your EthicalAds Publisher ID from https://www.ethicalads.io/publishers/ (e.g. "jarvis-os")
    ethicalAdsPublisherId: "",
    // Placement format: "text" (minimalist banner) or "image" (card with logo)
    ethicalAdsType: "text",
    // Contextual keywords for relevant Linux / Debian / AI developer ads
    keywords: "linux|debian|open-source|local-ai|devtools",
    // Optional Carbon Ads keys (if switching provider to "carbon"):
    carbonServe: "",
    carbonPlacement: "",
    // EthicalAds is cookie-free contextual by default; set true to hold ads until click
    requireConsentClick: false,
  },

  // 3. Creator Support Links (Rendered cleanly at the end of the website)
  support: {
    buyMeACoffeeUrl: "https://buymeacoffee.com/jerrymice45",
    buyMeACoffeeHandle: "jerrymice45",
    patreonUrl: "https://www.patreon.com/Jerry42",
    patreonHandle: "Jerry42",
  },
};
