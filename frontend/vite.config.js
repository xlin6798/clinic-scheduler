import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "localhost", // ensures consistent origin
    port: 5173, // force port
    strictPort: true, // 🔥 prevents auto-switch to 5174+
  },
});
