import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: [
        "localhost:3000",
        "*.github.dev",
        "*.app.github.dev",
        "suplementosdeloscampeonesgn.shop",
        "www.suplementosdeloscampeonesgn.shop"
      ],
    },
  },
};

export default nextConfig;
