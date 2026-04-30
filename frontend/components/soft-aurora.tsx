'use client'

interface SoftAuroraProps {
  speed?: number
  scale?: number
  brightness?: number
  color1?: string
  color2?: string
  color3?: string
}

export function SoftAurora({
  speed = 0.6,
  scale = 1.5,
  brightness = 1.2,
  color1 = '#7c3aed',
  color2 = '#ec4899',
  color3 = '#3b82f6',
}: SoftAuroraProps) {
  return (
    <div className="absolute inset-0 overflow-hidden">
      <svg
        className="absolute w-full h-full"
        viewBox="0 0 1200 600"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <filter id="blur">
            <feGaussianBlur in="SourceGraphic" stdDeviation="80" />
          </filter>
          <radialGradient id="grad1" cx="20%" cy="20%">
            <stop offset="0%" stopColor={color1} stopOpacity="0.8" />
            <stop offset="100%" stopColor={color1} stopOpacity="0" />
          </radialGradient>
          <radialGradient id="grad2" cx="80%" cy="50%">
            <stop offset="0%" stopColor={color2} stopOpacity="0.7" />
            <stop offset="100%" stopColor={color2} stopOpacity="0" />
          </radialGradient>
          <radialGradient id="grad3" cx="50%" cy="80%">
            <stop offset="0%" stopColor={color3} stopOpacity="0.6" />
            <stop offset="100%" stopColor={color3} stopOpacity="0" />
          </radialGradient>
        </defs>

        <style>{`
          @keyframes aurora-drift-1 {
            0%, 100% { transform: translate(0, 0) scale(${scale}); }
            50% { transform: translate(50px, -30px) scale(${scale * 1.1}); }
          }
          @keyframes aurora-drift-2 {
            0%, 100% { transform: translate(0, 0) scale(${scale}); }
            50% { transform: translate(-40px, 40px) scale(${scale * 0.9}); }
          }
          @keyframes aurora-drift-3 {
            0%, 100% { transform: translate(0, 0) scale(${scale}); }
            50% { transform: translate(30px, 20px) scale(${scale}); }
          }
          .aurora-1 {
            animation: aurora-drift-1 ${20 / speed}s ease-in-out infinite;
            filter: url(#blur);
            opacity: ${brightness * 0.4};
          }
          .aurora-2 {
            animation: aurora-drift-2 ${25 / speed}s ease-in-out infinite;
            filter: url(#blur);
            opacity: ${brightness * 0.35};
          }
          .aurora-3 {
            animation: aurora-drift-3 ${30 / speed}s ease-in-out infinite;
            filter: url(#blur);
            opacity: ${brightness * 0.3};
          }
        `}</style>

        <circle
          cx="200"
          cy="150"
          r="400"
          fill="url(#grad1)"
          className="aurora-1"
        />
        <circle
          cx="1000"
          cy="300"
          r="350"
          fill="url(#grad2)"
          className="aurora-2"
        />
        <circle
          cx="600"
          cy="500"
          r="300"
          fill="url(#grad3)"
          className="aurora-3"
        />
      </svg>
    </div>
  )
}
