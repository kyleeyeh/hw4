/**
 * Handsome Dan — Yale's bulldog mascot, drawn as a cute cartoon face for the chat.
 * Custom SVG (not a ripped asset): rounded bulldog head, Yale-navy collar, floppy ears,
 * underbite. Used on the chat launcher and the chat header.
 */
export default function HandsomeDan({ size = 44 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" role="img" aria-label="Handsome Dan">
      {/* ears */}
      <ellipse cx="15" cy="20" rx="9" ry="12" fill="#8a6d4b" transform="rotate(-18 15 20)" />
      <ellipse cx="49" cy="20" rx="9" ry="12" fill="#8a6d4b" transform="rotate(18 49 20)" />
      {/* head */}
      <path d="M32 8 C48 8 55 20 55 34 C55 48 45 57 32 57 C19 57 9 48 9 34 C9 20 16 8 32 8 Z"
        fill="#c9a678" />
      {/* face patch */}
      <ellipse cx="32" cy="40" rx="17" ry="15" fill="#e7d3b3" />
      {/* eyes */}
      <circle cx="24" cy="30" r="3.4" fill="#241d15" />
      <circle cx="40" cy="30" r="3.4" fill="#241d15" />
      <circle cx="25.1" cy="29" r="1.1" fill="#fff" />
      <circle cx="41.1" cy="29" r="1.1" fill="#fff" />
      {/* brow furrows (bulldog) */}
      <path d="M20 24 Q24 22 28 25" stroke="#a5825a" strokeWidth="1.6" fill="none" strokeLinecap="round" />
      <path d="M36 25 Q40 22 44 24" stroke="#a5825a" strokeWidth="1.6" fill="none" strokeLinecap="round" />
      {/* nose */}
      <ellipse cx="32" cy="39" rx="5" ry="4" fill="#241d15" />
      <ellipse cx="30.4" cy="38" rx="1" ry="0.8" fill="#5a4a38" />
      {/* mouth + underbite */}
      <path d="M32 43 V47" stroke="#241d15" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M24 47 Q32 53 40 47" stroke="#241d15" strokeWidth="1.6" fill="none" strokeLinecap="round" />
      <path d="M27 48 h4 v3 h-4 z M33 48 h4 v3 h-4 z" fill="#fffdf7" />
      {/* Yale-navy collar */}
      <path d="M15 54 Q32 63 49 54 L49 58 Q32 66 15 58 Z" fill="var(--navy)" />
      <circle cx="32" cy="58.5" r="2.4" fill="var(--gold)" />
    </svg>
  )
}
