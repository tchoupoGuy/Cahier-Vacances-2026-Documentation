import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Config par défaut : le serveur de dev tourne sur le port 5173, celui
// que l'API (api/main.py) autorise déjà dans son middleware CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
