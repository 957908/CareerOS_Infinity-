/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === 'production';

const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  // Dynamically set basePath to support local runs on root URL and subfolders on GitHub Pages
  basePath: isProd ? '/CareerOS_Infinity-' : '',
  assetPrefix: isProd ? '/CareerOS_Infinity-/' : '',
};

export default nextConfig;
