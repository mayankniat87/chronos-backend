import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow specific dev origins to access Next.js dev resources
  // (e.g. webpack HMR) — add any IPs or hosts you need during development.
  allowedDevOrigins: ["10.32.139.154"],
};

export default nextConfig;
