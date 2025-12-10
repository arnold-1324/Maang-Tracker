import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone mode for Docker
  output: 'standalone',

  async rewrites() {
    // Use environment-based API URL for development/production flexibility
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5100';
    const mcpUrl = process.env.NEXT_PUBLIC_MCP_URL || 'http://localhost:8765';

    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
      {
        source: '/mcp/:path*',
        destination: `${mcpUrl}/:path*`,
      },
    ];
  },

  // Enable image optimization
  images: {
    unoptimized: true,
  },

  // Disable static optimization for development
  experimental: {
    isrMemoryCacheSize: 0,
  },
};

export default nextConfig;
