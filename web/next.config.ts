import type { NextConfig } from "next";

// A static export: `npm run build` writes out/, which the Python server serves next to its API.
const nextConfig: NextConfig = {
  output: "export",
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
