/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gain: '#16a34a',
        loss: '#dc2626',
      },
    },
  },
  plugins: [],
}
