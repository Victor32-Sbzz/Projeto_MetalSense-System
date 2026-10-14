/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
        display: ["Space Grotesk", "sans-serif"],
      },
      colors: {
        ms: {
          black: "#000000",
          window: "#0E0E10",
          sidebar: "#121214",
          main: "#161618",
          surface: "#1C1C1E",
          card: "#1E1E20",
          cardAlt: "#222224",
          hover: "#2A2A2E",
          elevated: "#2E2E32",
          border: "rgba(255,255,255,0.07)",
          borderSubtle: "rgba(255,255,255,0.04)",
          borderSolid: "#27272A",
          borderActive: "rgba(255,255,255,0.14)",
          textPrimary: "#F2F2F3",
          textSecondary: "#9CA3AF",
          textMuted: "#6B7280",
          textDim: "#4B5563",
          pillActive: "rgba(255,255,255,0.08)",
          pillBorder: "rgba(255,255,255,0.12)",
        },
      },
      borderRadius: {
        ms: "14px",
        "ms-lg": "18px",
      },
    },
  },
  plugins: [],
}
