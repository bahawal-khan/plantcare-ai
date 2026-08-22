import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output produces a minimal self-contained server bundle,
  // used by frontend/Dockerfile for production deployment (Phase 12).
  output: "standalone",
};

export default nextConfig;
