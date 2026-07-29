import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@storyforge/ui', '@storyforge/types', '@storyforge/config'],
};

export default nextConfig;
