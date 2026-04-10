module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "Segoe UI Variable",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif"
        ]
      },
      colors: {
        gold: "#D6A84F",
        dark: "#0B1220",
        "dark-panel": "#0F1A2B",
        "dark-card": "#14233A"
      }
    }
  },
  plugins: []
};
