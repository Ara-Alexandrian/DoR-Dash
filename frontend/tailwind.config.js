/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Mary Bird Perkins colors - primary theme (burgundy)
        primary: {
          50: '#fdf2f2',
          100: '#f9e6e6',
          200: '#f5c7c7',
          300: '#eb9999',
          400: '#dd6b6b',
          500: '#c93a3a',
          600: '#b82727',
          700: '#971f1f',
          800: '#781e1e',
          900: '#621e1e', // Mary Bird Perkins Burgundy
          950: '#450e0e',
        },
        // LSU colors - secondary theme (purple)
        secondary: {
          50: '#f5f3ff',
          100: '#ede8ff',
          200: '#dcd5ff',
          300: '#c3b4fe',
          400: '#a586fd',
          500: '#8a51fc',
          600: '#7c34f5',
          700: '#6d2ae0',
          800: '#5b21b6',
          900: '#461d97', // LSU Purple
          950: '#2a1065',
        },
        // LSU Gold
        gold: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#713f12', // Darker gold
          950: '#422006',
        },
        // Mary Bird Perkins Black
        mbpblack: {
          50: '#f6f6f6',
          100: '#e7e7e7',
          200: '#d1d1d1',
          300: '#b0b0b0',
          400: '#888888',
          500: '#6d6d6d',
          600: '#5d5d5d',
          700: '#4f4f4f',
          800: '#454545',
          900: '#3d3d3d', // MBP Black
          950: '#000000',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}