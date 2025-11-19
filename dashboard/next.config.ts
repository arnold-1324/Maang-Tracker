import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5100/api/:path*',
      },
      {
        source: '/flask/:path*',
        destination: 'http://localhost:5100/:path*',
      },
    ];
  },
};

export default nextConfig;
