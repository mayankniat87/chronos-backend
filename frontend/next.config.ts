import type { NextConfig } from "next";
import { fileURLToPath } from "node:url";

const nextConfig: NextConfig = {
  // Allow specific dev origins to access Next.js dev resources
  // (e.g. webpack HMR) — add any IPs or hosts you need during development.
  allowedDevOrigins: ["10.32.139.154"],
  // Explicitly set the workspace root so Turbopack doesn't mis-detect it when
  // a stray lockfile exists in a parent directory (which hangs the dev server).
  turbopack: {
    root: fileURLToPath(new URL(".", import.meta.url)),
  },
};

export default nextConfig;
