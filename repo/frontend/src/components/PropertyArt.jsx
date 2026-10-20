// Generated skyline placeholder: demo properties carry no real photography.
const TINT = { 'Dubai Marina': '#cfe3e0', 'Downtown Dubai': '#d9dee6', 'Business Bay': '#dde6dc', Jumeirah: '#e8e2d4', 'Palm Jumeirah': '#cde4e8', 'Arabian Ranches': '#e6e0d0', 'Dubai Hills': '#d6e5d6', JVC: '#e0dfe8' }
export default function PropertyArt({ property, className = '' }) {
  const bg = TINT[property.area] || '#dfe6e5'
  const tall = property.property_type === 'Apartment' || property.property_type === 'Penthouse'
  const seed = property.id * 37
  const bars = Array.from({ length: 6 }, (_, i) => ({ x: 14 + i * 30, h: 40 + ((seed + i * 53) % 70) }))
  return (
    <svg viewBox="0 0 200 120" className={className} preserveAspectRatio="xMidYMid slice" role="img" aria-label={`Illustration for ${property.title}`}>
      <rect width="200" height="120" fill={bg} />
      <circle cx="165" cy="26" r="11" fill="#fff" opacity=".7" />
      {tall ? bars.map((b, i) => <rect key={i} x={b.x} y={110 - b.h} width="22" height={b.h} fill="#0E5A4F" opacity={0.25 + (i % 3) * 0.2} />)
        : (<g fill="#0E5A4F"><rect x="40" y="62" width="120" height="48" opacity=".75" /><polygon points="32,62 100,28 168,62" opacity=".95" /><rect x="90" y="84" width="20" height="26" fill="#fff" opacity=".8" /></g>)}
      <rect y="108" width="200" height="12" fill="#14201F" opacity=".12" />
    </svg>
  )
}
