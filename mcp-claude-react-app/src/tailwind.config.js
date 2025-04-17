// tailwind.config.js
export default {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          light: "#00C49F", // Use wherever you had `text-indigo-600` etc.
          DEFAULT: "#0088FE", // e.g. for buttons & links
          dark: "#002B3E", // background/navbars
          accent: "#FFC800", // CTAs, highlights
        },
      },
    },
  },
  plugins: [],
};
