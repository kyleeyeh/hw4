/**
 * A collegiate Yale-style shield for the footer, signifying officially-licensed status.
 * Hand-built (NOT Yale's trademarked logo file): a navy shield with a gold border and a
 * crafted serif "Y". Reads as legit without copying protected artwork.
 */
export default function YaleSeal() {
  return (
    <div className="yale-seal">
      <svg width="50" height="58" viewBox="0 0 50 58" role="img" aria-label="Yale">
        <path
          d="M25 2 L47 9 V30 C47 44 37 52 25 56 C13 52 3 44 3 30 V9 Z"
          fill="var(--navy)" stroke="var(--gold)" strokeWidth="2.5"
        />
        <path
          d="M25 6 L43 11.5 V30 C43 41.5 34.5 48.5 25 52 C15.5 48.5 7 41.5 7 30 V11.5 Z"
          fill="none" stroke="var(--gold-soft)" strokeWidth="0.8" opacity="0.6"
        />
        <text x="25" y="38" textAnchor="middle" fontFamily="Fraunces, Georgia, serif"
          fontWeight="900" fontSize="30" fill="#fffdf7">Y</text>
      </svg>
      <div className="yale-seal-text">
        <strong>Yale</strong>
        <span>Officially Licensed<br />Collegiate Product</span>
      </div>
    </div>
  )
}
