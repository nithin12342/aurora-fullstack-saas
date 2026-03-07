/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@aurora/ui-components', '@aurora/shared-types', '@aurora/shared-utils'],
  webpack: config => {
    // Module Federation for micro-frontends
    config.experiments = {
      ...config.experiments,
      topLevelAwait: true,
    };
    return config;
  },
  async rewrites() {
    return [
      // Proxy API requests to backend services
      {
        source: '/api/tasks/:path*',
        destination: 'http://localhost:8001/tasks/:path*',
      },
      {
        source: '/api/users/:path*',
        destination: 'http://localhost:8002/users/:path*',
      },
      {
        source: '/api/billing/:path*',
        destination: 'http://localhost:8003/billing/:path*',
      },
      {
        source: '/api/graphql',
        destination: 'http://localhost:8000/graphql',
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
