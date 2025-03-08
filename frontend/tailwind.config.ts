import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-red': '#E31837',
        'secondary-red': '#FF1B3B',
        'accent-red': '#FF4D6D',
        'off-white': '#F8F9FA',
        'dark-gray': '#212529',
      },
    },
  },
  plugins: [],
};

export default config;