import type { NextConfig } from "next";

const engine = process.env.ENGINE_URL || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/engine/:path*",
        destination: `${engine}/:path*`,
      },
    ];
  },
};

export default nextConfig;
