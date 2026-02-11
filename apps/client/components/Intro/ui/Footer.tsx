export default function Footer() {
  return (
    <footer className="relative pb-12 pt-32">
      <div className="relative mx-auto max-w-6xl px-4 sm:px-6">
        {/* Big futuristic text that fades from bottom */}
        <div className="relative flex h-[400px] items-end justify-center overflow-hidden" aria-hidden="true">
          {/* Gradient text */}
          <div
            className="pointer-events-none select-none font-nacelle text-[280px] font-bold leading-none tracking-tighter text-transparent bg-gradient-to-b from-indigo-200/40 via-indigo-300/20 to-transparent bg-clip-text"
            style={{
              maskImage: 'linear-gradient(to top, transparent 0%, black 40%, black 100%)',
              WebkitMaskImage: 'linear-gradient(to top, transparent 0%, black 40%, black 100%)',
            }}
          >
            VAULTA
          </div>

          {/* Indigo glow effect */}
          <div
            className="absolute bottom-0 left-1/2 -translate-x-1/2"
            aria-hidden="true"
          >
            <div className="h-48 w-[600px] rounded-full bg-indigo-600/30 blur-[120px]"></div>
          </div>
        </div>
      </div>
    </footer>
  );
}
