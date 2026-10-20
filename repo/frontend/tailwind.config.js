export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: { extend: {
    colors: { mist: '#F5F7F7', ink: '#14201F', pine: { DEFAULT: '#0E5A4F', dark: '#0A433B', soft: '#E3F0ED' }, slate2: '#5B6B69', line: '#E3E8E7',
              amber2: '#9A6A12', amberbg: '#FBF1DC', skybg: '#E8EEF3', sky2: '#3A5670' },
    fontFamily: { display: ['Fraunces', 'Georgia', 'serif'], sans: ['"Hanken Grotesk"', '"Noto Sans Arabic"', 'system-ui', 'sans-serif'] },
    boxShadow: { soft: '0 1px 2px rgba(20,32,31,.04), 0 8px 24px -12px rgba(20,32,31,.12)' } } },
}
