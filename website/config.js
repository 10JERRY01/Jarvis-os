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

  // 2. Day-1 + Scaled Monetization Engine
  // provider modes:
  // - "auto"       : Uses EthicalAds if ID set -> else A-ADS if aadsUnitId set -> else rotates Day-1 cards cleanly
  // - "ethicalads" : EthicalAds only (~50k/mo guideline)
  // - "carbon"     : Carbon Ads only (~10k/mo min, exclusive)
  // - "aads"       : A-ADS zero-minimum banner (paste numeric ad unit ID from aads.com)
  // - "sponsor"    : Rotates Direct Sponsor / Supporter Pack / Affiliate cards from Day 1
  ads: {
    provider: "auto",
    // Paste your EthicalAds Publisher ID from https://www.ethicalads.io/publishers/ (e.g. "jarvis-os")
    ethicalAdsPublisherId: "",
    // Placement format: "text" (minimalist banner) or "image" (card with logo)
    ethicalAdsType: "text",
    // Contextual keywords for relevant Linux / Debian / AI developer ads
    keywords: "linux|debian|open-source|local-ai|devtools",
    // Zero-minimum A-ADS numeric ad unit ID (create free at https://aads.com/):
    aadsUnitId: "",
    // Optional Carbon Ads keys (if switching provider to "carbon"):
    carbonServe: "",
    carbonPlacement: "",
    // Cookie-free contextual ads & native sponsor cards load automatically unless opted out
    requireConsentClick: false,
    // Day-1 rotated cards shown automatically until EthicalAds / A-ADS / Carbon IDs are active:
    // Tip: Replace card 2/3 URLs with DigitalOcean, Hetzner, or Vultr affiliate links anytime.
    dayOneCards: [
      {
        badge: "Supporter Extra · Zero Minimum",
        headline: "Unlock the Jarvis OS 5K Wallpaper & Minimalist Dotfile Pack ($5+)",
        description: "15 exclusive 5K, Ultrawide & Mobile wallpapers across all 5 themes plus Starship, Fastfetch & Kitty presets.",
        ctaLabel: "Get Theme Pack",
        ctaUrl: "https://buymeacoffee.com/jerrymice45",
      },
      {
        badge: "Direct Sponsorship Open",
        headline: "Reach Linux Developers, Gamers & Offline AI Builders",
        description: "Zero tracking scripts. Feature your DevTool, Cloud VPS, or Linux hardware above the fold on Home & Docs.",
        ctaLabel: "Sponsor Jarvis OS",
        ctaUrl: "https://www.patreon.com/Jerry42",
      },
      {
        badge: "Community Backed · Early Access",
        headline: "Fuel Overnight Liquorix Kernel & Debian v1.x ISO Builds",
        description: "Join monthly backers on Patreon for early ISO drops, roadmap voting, and custom Cupertino theme packs.",
        ctaLabel: "Join on Patreon",
        ctaUrl: "https://www.patreon.com/Jerry42",
      },
    ],
  },

  // 3. Creator Support & Digital Extras (Rendered cleanly at the end of the website)
  support: {
    buyMeACoffeeUrl: "https://buymeacoffee.com/jerrymice45",
    buyMeACoffeeHandle: "jerrymice45",
    patreonUrl: "https://www.patreon.com/Jerry42",
    patreonHandle: "Jerry42",
    githubSponsorsUrl: "https://github.com/sponsors/10JERRY01",
    // Replace with your direct Buy Me a Coffee Extras or Gumroad item link after uploading dist/jarvis-os-supporter-pack-v1.0.zip:
    supporterPackUrl: "https://buymeacoffee.com/jerrymice45",
    supporterPackPrice: "$5+ Pay What You Want",
  },
};
