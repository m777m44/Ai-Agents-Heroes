export function Logo({ size = 32, className = '' }: { size?: number; className?: string }) {
  return (
    <svg className={`logo ${className}`} width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
      <defs>
        <linearGradient id="mahdi-g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#f3d17a" />
          <stop offset="1" stopColor="#2dd4bf" />
        </linearGradient>
      </defs>
      <path d="M32 6l22.5 13v26L32 58 9.5 45V19z" fill="rgba(212,168,75,.08)" stroke="url(#mahdi-g)" strokeWidth="3" strokeLinejoin="round" />
      <path d="M32 19c1.7 8 5 11.3 13 13-8 1.7-11.3 5-13 13-1.7-8-5-11.3-13-13 8-1.7 11.3-5 13-13z" fill="url(#mahdi-g)" />
    </svg>
  );
}
