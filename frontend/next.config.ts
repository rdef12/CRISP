import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // Can change this to optimise the load times I believe...
};

export default nextConfig;

// Use this below and place /api in all FastAPI handler routes.
// Without this initial routing, all images will also be prepended by
// the backend URL, breaking the app.

// import { NextConfig } from "next";

// const nextConfig: NextConfig = {
//   async rewrites() {
//     return [
//       {
//         source: "/api/:path*", // Proxy API calls
//         destination:`${process.env.NEXT_PUBLIC_BACKEND}/:path*`,
//       },
//     ];
//   },
// };

// export default nextConfig;

