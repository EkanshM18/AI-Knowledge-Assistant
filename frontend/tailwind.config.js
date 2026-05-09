/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#102033',
        slate: '#445266',
        mist: '#dbe4ef',
        shell: '#f5f7fb',
        accent: '#1f7a72',
        amber: '#d58b1b',
        coral: '#dc675d'
      },
      boxShadow: {
        panel: '0 18px 48px rgba(16, 32, 51, 0.08)'
      },
      backgroundImage: {
        mesh:
          'radial-gradient(circle at top left, rgba(31,122,114,0.18), transparent 32%), radial-gradient(circle at bottom right, rgba(213,139,27,0.16), transparent 28%)'
      }
    }
  },
  plugins: []
}

