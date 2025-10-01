/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      boxShadow: {
        chat: "inset 0 0 0 1px rgb(227,227,227)"
      },
    },
  },
  plugins: [],
}

