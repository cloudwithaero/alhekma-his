import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import path from "path"

export default defineConfig({
  plugins: [react(), tailwindcss()],

  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },

  server: {
    host: "0.0.0.0",
    port: 5173,

    allowedHosts: ["alhekma.local"],

    proxy: {
      "/api": {
        target: "http://alhekma.local:8000",
        changeOrigin: true,
        secure: false,
      },

      "/assets": {
        target: "http://alhekma.local:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
