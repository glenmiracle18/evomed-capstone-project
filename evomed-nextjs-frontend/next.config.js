/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
import "./src/env.js";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import("next").NextConfig} */
const config = {
  reactStrictMode: false,

  // Disable TypeScript type checking during builds
  typescript: {
    ignoreBuildErrors: true,
  },

  // Disable ESLint checking during builds
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Configure webpack to handle path aliases
  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      "~": path.join(__dirname, "src"),
      "~/lib": path.join(__dirname, "src", "lib"),
      "~/components": path.join(__dirname, "src", "components"),
      "~/utils": path.join(__dirname, "src", "utils"),
    };
    return config;
  },

  // Configure headers for security and CORS
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },

  // Configure external domains for API calls
  experimental: {
    serverComponentsExternalPackages: [],
  },

  // Configure images if needed for external domains
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.modal.run",
        port: "",
        pathname: "/**",
      },
    ],
  },
};

export default config;
