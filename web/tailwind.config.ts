/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          red: "#CC0000",
          dark: "#0f0f1a",
          card: "#1a1a2e",
          border: "#2a2a3e",
          muted: "#8892a4",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["DM Sans", "Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
