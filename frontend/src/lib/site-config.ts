/**
 * Central site configuration: API base URL and social/contact links.
 * CLAUDE.md requires GitHub/LinkedIn/email links to be configured centrally
 * rather than scattered across components, and no hard-coded machine-specific
 * paths -- the API base URL comes from NEXT_PUBLIC_API_BASE_URL.
 */

export const siteConfig = {
  name: "PlantCare AI",
  tagline: "AI-powered plant disease detection",
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  upload: {
    // Client-side pre-check only, mirrors the backend's default MAX_UPLOAD_SIZE_BYTES
    // (see .env.example) so users get instant feedback -- the backend always
    // re-validates and remains the authoritative limit.
    maxSizeBytes: Number(process.env.NEXT_PUBLIC_MAX_UPLOAD_MB ?? 5) * 1024 * 1024,
    acceptedTypes: ["image/jpeg", "image/png", "image/webp"] as const,
    acceptedExtensions: ".jpg,.jpeg,.png,.webp",
  },
  social: {
    github: "https://github.com/bahawal-khan",
    linkedin: "https://www.linkedin.com/in/bahawal-khan-9b1124313",
    email: "khanbahawal2004@gmail.com",
  },
  nav: [
    { label: "Home", href: "/" },
    { label: "Diseases", href: "/diseases" },
    { label: "How It Works", href: "/how-it-works" },
    { label: "About", href: "/about" },
  ],
  footerLinks: {
    quickLinks: [
      { label: "Home", href: "/" },
      { label: "Diseases", href: "/diseases" },
      { label: "How It Works", href: "/how-it-works" },
      { label: "About", href: "/about" },
    ],
    features: [
      { label: "AI Detection", href: "/diagnose" },
      { label: "Disease Library", href: "/diseases" },
      { label: "Grad-CAM Explainability", href: "/how-it-works" },
    ],
  },
} as const;
