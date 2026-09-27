/**
 * Campus Customs collegiate seal — a hand-built varsity monogram (not AI-default box art).
 * Circular seal: navy field, aged-gold double ring, interlocked serif "CC", arced
 * "CAMPUS CUSTOMS · NEW HAVEN" text and little stars. Scales cleanly from the nav (36px)
 * to large marketing use.
 */
export default function CampusCustomsLogo({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" role="img" aria-label="Campus Customs">
      <defs>
        <path id="cc-arc-top" d="M 50 50 m -38 0 a 38 38 0 1 1 76 0" fill="none" />
        <path id="cc-arc-bot" d="M 50 50 m -32 0 a 32 32 0 1 0 64 0" fill="none" />
      </defs>

      <circle cx="50" cy="50" r="49" fill="var(--navy)" />
      <circle cx="50" cy="50" r="49" fill="none" stroke="var(--gold)" strokeWidth="2" />
      <circle cx="50" cy="50" r="42" fill="none" stroke="var(--gold-soft)" strokeWidth="1" opacity="0.7" />

      <text fill="var(--gold-light)" fontFamily="Inter, sans-serif" fontSize="8.5" fontWeight="700" letterSpacing="2.2">
        <textPath href="#cc-arc-top" startOffset="50%" textAnchor="middle">CAMPUS CUSTOMS</textPath>
      </text>
      <text fill="var(--gold-light)" fontFamily="Inter, sans-serif" fontSize="7.5" fontWeight="600" letterSpacing="2">
        <textPath href="#cc-arc-bot" startOffset="50%" textAnchor="middle">NEW HAVEN</textPath>
      </text>

      {/* interlocked serif CC */}
      <text x="50" y="63" textAnchor="middle" fontFamily="Fraunces, Georgia, serif"
        fontWeight="900" fontSize="44" fill="#fffdf7" style={{ letterSpacing: '-6px' }}>CC</text>

      {/* flanking stars */}
      <text x="20" y="55" textAnchor="middle" fontSize="8" fill="var(--gold)">★</text>
      <text x="80" y="55" textAnchor="middle" fontSize="8" fill="var(--gold)">★</text>
    </svg>
  )
}
