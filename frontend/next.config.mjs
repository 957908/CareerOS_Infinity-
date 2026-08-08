/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  // Ensure paths map correctly on GitHub Pages subfolder (if repository name is CareerOS_Infinity-)
  basePath: '/CareerOS_Infinity-',
  assetPrefix: '/CareerOS_Infinity-/',
};

export default nextConfig;
